#!/usr/bin/env python3
"""
pre_write_language_compliance: Enforce language-specific testing, linting, and analysis.

Validates:
1. Language detection and mapping
2. Presence of language-specific test/lint configuration
3. Test framework presence for changed code
4. Linting tool availability

Enforced across: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, 
Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "c": [".c", ".h"],
    "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".h"],
    "csharp": [".cs"],
    "go": [".go"],
    "rust": [".rs"],
    "php": [".php"],
    "ruby": [".rb"],
    "swift": [".swift"],
    "kotlin": [".kt"],
    "r": [".r"],
    "matlab": [".m"],
}

TEST_CONFIG_FILES = {
    "python": ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"],
    "javascript": ["package.json", "jest.config.js", "vitest.config.ts"],
    "typescript": ["package.json", "jest.config.js", "vitest.config.ts"],
    "java": ["pom.xml", "build.gradle", "build.gradle.kts"],
    "c": ["CMakeLists.txt", "Makefile"],
    "cpp": ["CMakeLists.txt", "Makefile"],
    "csharp": [".csproj", ".sln"],
    "go": ["go.mod", "go.sum"],
    "rust": ["Cargo.toml"],
    "php": ["phpunit.xml", "composer.json"],
    "ruby": ["Gemfile", "Rakefile", "spec_helper.rb"],
    "swift": ["Package.swift"],
    "kotlin": ["build.gradle", "build.gradle.kts"],
    "r": ["DESCRIPTION", "tests/testthat"],
    "matlab": ["runtests.m"],
}

LINT_CONFIG_FILES = {
    "python": [".flake8", "pyproject.toml", "ruff.toml", ".pylintrc"],
    "javascript": [".eslintrc.js", "eslint.config.mjs", ".eslintignore"],
    "typescript": [".eslintrc.js", "tsconfig.json", "eslint.config.mjs"],
    "java": ["checkstyle.xml", "spotbugs.xml", "pmd.xml"],
    "c": [".clang-tidy", ".clang-format"],
    "cpp": [".clang-tidy", ".clang-format"],
    "csharp": [".editorconfig", ".stylecop.json"],
    "go": ["golangci.yml", ".golangci.yml"],
    "rust": ["clippy.toml"],
    "php": ["phpstan.neon", ".php-cs-fixer.php"],
    "ruby": [".rubocop.yml", ".rubocop.yaml"],
    "swift": [".swiftlint.yml"],
    "kotlin": ["detekt.yml"],
    "r": [".lintr"],
    "matlab": [],
}

def detect_language(path: str) -> str:
    """Detect language from file extension."""
    ext = Path(path).suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return "unknown"

def fail(msg, details=None):
    print("BLOCKED: pre_write_language_compliance violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"  • {d}", file=sys.stderr)
    sys.exit(2)

def check_config_files(repo_root: Path, lang: str, file_types: Dict[str, List[str]]) -> bool:
    """Check if any required config file exists for the language."""
    if lang not in file_types:
        return True
    
    config_files = file_types[lang]
    for cfg in config_files:
        cfg_path = repo_root / cfg
        if cfg_path.exists():
            return True
    
    return False

def main():
    # Load policy
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    # Infer repo root from edit paths
    repo_root = Path.cwd()
    
    violations = []
    languages_touched = set()
    
    for e in edits:
        path = e.get("path", "unknown")
        lang = detect_language(path)
        
        if lang != "unknown":
            languages_touched.add(lang)
    
    if not languages_touched:
        sys.exit(0)
    
    # Check each language touched
    for lang in languages_touched:
        # Check test configuration exists
        if not check_config_files(repo_root, lang, TEST_CONFIG_FILES):
            violations.append(
                f"Missing test configuration for {lang}. "
                f"Required: one of {TEST_CONFIG_FILES.get(lang, [])}"
            )
        
        # Check lint configuration exists
        if not check_config_files(repo_root, lang, LINT_CONFIG_FILES):
            # MATLAB doesn't require config, it's built-in
            if lang != "matlab":
                violations.append(
                    f"Missing linting configuration for {lang}. "
                    f"Required: one of {LINT_CONFIG_FILES.get(lang, [])}"
                )
    
    if violations:
        fail(
            "Language compliance check failed: missing test/lint configuration",
            violations
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
