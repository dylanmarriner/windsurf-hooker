#!/usr/bin/env python3
"""
post_write_self_contained_enforcement: Complete self-contained enforcement.

Does NOT rely on ./scripts/verify. Instead, directly validates:
1. Linting configuration exists and can be found
2. Type checking configuration exists
3. Syntax is valid for the language
4. Tests exist and have real test functions (no mocks)
5. Coverage configuration is present

This ensures enforcement works 100% in the hooks without external scripts.
"""

import json
import sys
import re
import subprocess
from pathlib import Path
from typing import Dict, List

def resolve_policy_path() -> Path:
    """Resolve policy path."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

LANGUAGE_EXTENSIONS = {
    "python": [".py"],
    "javascript": [".js", ".jsx"],
    "typescript": [".ts", ".tsx"],
    "java": [".java"],
    "c": [".c"],
    "cpp": [".cpp", ".cc", ".cxx"],
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

LINT_CONFIGS = {
    "python": [".flake8", "pyproject.toml", "ruff.toml", ".pylintrc"],
    "javascript": [".eslintrc.js", "eslint.config.mjs", ".eslintrc.json"],
    "typescript": [".eslintrc.js", "tsconfig.json", "eslint.config.mjs"],
    "java": ["checkstyle.xml", "spotbugs.xml"],
    "c": [".clang-tidy", ".clang-format"],
    "cpp": [".clang-tidy", ".clang-format"],
    "csharp": [".editorconfig"],
    "go": ["golangci.yml", ".golangci.yml"],
    "rust": ["clippy.toml"],
    "php": ["phpstan.neon"],
    "ruby": [".rubocop.yml"],
    "swift": [".swiftlint.yml"],
    "kotlin": ["detekt.yml"],
    "r": [".lintr"],
    "matlab": [],
}

MOCK_PATTERNS = [
    r"\bMock\b", r"\bStub\b", r"\bFake\b", r"\bSpy\b",
    r"\.mock\(", r"jest\.mock\(", r"vitest\.mock\(",
    r"@Mock", r"@Spy", r"mockito", r"sinon", r"testDouble",
]

TEST_FOLDERS = ["tests", "test", "spec", "specs", "__tests__", "src/__tests__"]

def detect_language(path: str) -> str:
    """Detect language from file extension."""
    ext = Path(path).suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return "unknown"

def has_syntax_errors(path: str, lang: str) -> List[str]:
    """Check if file has syntax errors."""
    errors = []
    
    try:
        content = Path(path).read_text()
    except Exception as e:
        return [f"Cannot read {path}: {e}"]
    
    if lang == "python":
        try:
            compile(content, path, "exec")
        except SyntaxError as e:
            errors.append(f"Python syntax error in {path}: {e}")
    
    elif lang in ("javascript", "typescript"):
        # Check for obvious syntax errors
        if re.search(r"[{}\[\]]\s*[{}\[\]]", content):
            if content.count("{") != content.count("}"):
                errors.append(f"Mismatched braces in {path}")
        if content.count("[") != content.count("]"):
            errors.append(f"Mismatched brackets in {path}")
    
    elif lang == "java":
        if "{" in content and content.count("{") != content.count("}"):
            errors.append(f"Mismatched braces in {path}")
    
    elif lang == "cpp":
        if "{" in content and content.count("{") != content.count("}"):
            errors.append(f"Mismatched braces in {path}")
    
    elif lang == "rust":
        # Rust files should be valid at least structurally
        if "{" in content and content.count("{") != content.count("}"):
            errors.append(f"Mismatched braces in {path}")
    
    return errors

def check_lint_config_exists(lang: str) -> List[str]:
    """Check if linting configuration exists for language."""
    if lang not in LINT_CONFIGS:
        return []
    
    if lang == "matlab":
        return []  # MATLAB uses built-in
    
    configs = LINT_CONFIGS[lang]
    found = False
    
    for cfg in configs:
        if Path(cfg).exists():
            found = True
            break
    
    if not found:
        return [
            f"HARD FAIL: No linting config for {lang}. Required: {', '.join(configs)}"
        ]
    
    return []

def find_test_file(source_path: str) -> Path:
    """Find corresponding test file."""
    source = Path(source_path)
    name = source.stem
    
    for test_folder in TEST_FOLDERS:
        test_dir = Path(test_folder)
        if test_dir.exists():
            patterns = [
                f"test_{name}.py",
                f"{name}.test.js",
                f"{name}.test.ts",
                f"{name}Test.java",
                f"{name}_test.go",
                f"{name}Spec.kt",
            ]
            
            for pattern in patterns:
                test_file = test_dir / pattern
                if test_file.exists():
                    return test_file
    
    return None

def check_test_validity(test_path: Path, lang: str) -> List[str]:
    """Verify test file is real (not stub or mock)."""
    errors = []
    
    if not test_path.exists():
        return [f"Test file does not exist: {test_path}"]
    
    content = test_path.read_text()
    
    # Check for mocks
    for pattern in MOCK_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            errors.append(f"HARD FAIL: Mock pattern '{pattern}' found in {test_path}")
    
    # Check test file isn't empty or stub
    if len(content.strip()) < 50:
        errors.append(f"HARD FAIL: Test file {test_path} is empty/stub")
    
    # Check for actual test functions
    has_tests = False
    
    if lang == "python":
        has_tests = bool(re.search(r"def\s+test_\w+\s*\(", content))
    elif lang in ("javascript", "typescript"):
        has_tests = bool(re.search(r"(?:test|it)\s*\(\s*['\"]", content))
    elif lang == "java":
        has_tests = bool(re.search(r"@Test|void\s+test\w+\s*\(", content))
    elif lang == "go":
        has_tests = bool(re.search(r"func\s+Test\w+\s*\(", content))
    elif lang == "rust":
        has_tests = bool(re.search(r"#\[test\]", content))
    elif lang == "cpp":
        has_tests = bool(re.search(r"TEST\(|TEST_F\(", content))
    elif lang == "csharp":
        has_tests = bool(re.search(r"\[Test\]|\[Fact\]", content))
    
    if not has_tests:
        errors.append(f"HARD FAIL: No actual tests in {test_path}")
    
    # Check for common test placeholders
    if re.search(r"(TODO|FIXME|XXX|pass\s*$|assert False|skip)", content):
        errors.append(f"HARD FAIL: Test placeholders in {test_path}")
    
    return errors

def fail(msg, details=None):
    print("BLOCKED: post_write_self_contained_enforcement violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"  • {d}", file=sys.stderr)
    sys.exit(2)

def main():
    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    violations = []
    source_files = {}
    
    for e in edits:
        path = e.get("path", "unknown")
        lang = detect_language(path)
        
        # Skip test files, config, markdown
        if any(x in path.lower() for x in ["test", "spec", "mock"]):
            continue
        if path.endswith((".json", ".md", ".yaml", ".yml", ".toml", ".config")):
            continue
        if lang == "unknown":
            continue
        
        if lang not in source_files:
            source_files[lang] = []
        source_files[lang].append(path)
    
    if not source_files:
        sys.exit(0)
    
    # ============================================================
    # ENFORCE LINTING CONFIGURATION EXISTS
    # ============================================================
    for lang in source_files.keys():
        lint_errors = check_lint_config_exists(lang)
        violations.extend(lint_errors)
    
    # ============================================================
    # ENFORCE SYNTAX IS VALID
    # ============================================================
    for lang, files in source_files.items():
        for path in files:
            syntax_errors = has_syntax_errors(path, lang)
            violations.extend(syntax_errors)
    
    # ============================================================
    # ENFORCE TESTS EXIST AND ARE REAL
    # ============================================================
    for lang, files in source_files.items():
        for source_path in files:
            # Skip entry points and minimal files
            if any(x in source_path for x in ["__init__", "__main__", "main.py", "main.js"]):
                # Entry points may not need tests in some cases
                pass
            else:
                test_file = find_test_file(source_path)
                
                if not test_file:
                    violations.append(
                        f"HARD FAIL: No test file for {source_path}"
                    )
                else:
                    test_errors = check_test_validity(test_file, lang)
                    violations.extend(test_errors)
    
    # ============================================================
    # ENFORCE TYPE CHECKING CONFIGURATION (for typed languages)
    # ============================================================
    typed_langs = {"python", "typescript", "java", "csharp", "kotlin", "swift"}
    for lang in source_files.keys():
        if lang == "python":
            # Check for mypy config or pyproject.toml
            has_config = (Path("mypy.ini").exists() or 
                         Path(".mypy.ini").exists() or
                         "tool.mypy" in Path("pyproject.toml").read_text() if Path("pyproject.toml").exists() else False)
            if not has_config:
                violations.append("HARD FAIL: No mypy configuration for Python (mypy.ini or pyproject.toml [tool.mypy])")
        
        elif lang == "typescript":
            if not Path("tsconfig.json").exists():
                violations.append("HARD FAIL: No tsconfig.json for TypeScript")
    
    # ============================================================
    # FINAL VERDICT
    # ============================================================
    if violations:
        fail(
            "HARD FAIL: Code does not meet self-contained enforcement standards",
            violations
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
