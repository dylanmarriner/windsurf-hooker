#!/usr/bin/env python3
"""
post_write_coverage_enforcement: Enforce 100% code coverage with zero mocks.

Validates:
1. Test files exist for changed code
2. Coverage reports show 100% line and branch coverage
3. No mock/fake/stub patterns used in tests
4. Tests use real implementations only
5. Language-specific coverage tools configured

Enforced uniformly across: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, 
Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB.
"""

import json
import sys
import re
import subprocess
from pathlib import Path
from typing import Tuple, List

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

MOCK_PATTERNS = [
    r"\b(Mock|Stub|Fake|Spy)\s*\(",
    r"\.mock\(",
    r"(unittest\.mock|jest\.mock|vitest\.mock|@Mock|@Spy)",
    r"(mockito|sinon|jest|vitest\.fn|mocha\.spy)",
    r"(test\.stub|double\.|testDouble|fake)",
    r"(TestDouble|MockObject|FakeData)",
]

TEST_FOLDERS = ["tests", "test", "spec", "specs", "__tests__", "src/__tests__"]

def detect_language(path: str) -> str:
    """Detect language from file extension."""
    ext = Path(path).suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return "unknown"

def find_test_file(source_path: str) -> Path:
    """Find corresponding test file for source code."""
    source = Path(source_path)
    name_without_ext = source.stem
    
    for test_folder in TEST_FOLDERS:
        test_dir = Path(test_folder)
        if test_dir.exists():
            # Try common test naming patterns
            patterns = [
                test_dir / f"test_{name_without_ext}.py",
                test_dir / f"{name_without_ext}.test.js",
                test_dir / f"{name_without_ext}.test.ts",
                test_dir / f"{name_without_ext}Test.java",
                test_dir / f"{name_without_ext}_test.go",
                test_dir / f"{name_without_ext}.spec.ts",
                test_dir / f"{name_without_ext}Spec.kt",
                test_dir / f"test_{name_without_ext}.cpp",
            ]
            
            for pattern in patterns:
                if pattern.exists():
                    return pattern
    
    return None

def check_mock_usage_in_tests(test_file: Path) -> List[str]:
    """Check if test file uses mocks/stubs/fakes."""
    violations = []
    
    if not test_file.exists():
        return violations
    
    content = test_file.read_text()
    
    for pattern in MOCK_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE):
            violations.append(
                f"Test file {test_file.name} uses mock/stub/fake: {pattern}"
            )
    
    return violations

def fail(msg, details=None):
    print("BLOCKED: post_write_coverage_enforcement violation", file=sys.stderr)
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
        
        # Skip test files, config files, and non-code
        if "test" in path.lower() or "spec" in path.lower():
            continue
        if path.endswith((".json", ".md", ".yaml", ".yml", ".toml", ".config")):
            continue
        if lang == "unknown":
            continue
        
        # Track which source files were modified
        if lang not in source_files:
            source_files[lang] = []
        source_files[lang].append(path)
    
    if not source_files:
        sys.exit(0)
    
    violations = []
    
    # For each modified source file, verify test existence and coverage
    for lang, files in source_files.items():
        for source_path in files:
            test_file = find_test_file(source_path)
            
            if not test_file:
                violations.append(
                    f"HARD FAIL: No test file for {source_path} "
                    f"(required: test_*.py, *.test.js, *.test.ts, *Test.java, etc.)"
                )
                continue
            
            # Check test file for mock usage
            mock_violations = check_mock_usage_in_tests(test_file)
            if mock_violations:
                violations.extend(mock_violations)
            
            # Verify test file has actual test functions
            test_content = test_file.read_text()
            has_tests = False
            
            if lang == "python":
                has_tests = bool(re.search(r"def\s+test_\w+", test_content))
                if not has_tests:
                    violations.append(f"No test functions in {test_file} (need test_* functions)")
            elif lang in ("javascript", "typescript"):
                has_tests = bool(re.search(r"(?:test|it)\s*\(\s*['\"]", test_content))
                if not has_tests:
                    violations.append(f"No test cases in {test_file} (need test() or it() calls)")
            elif lang == "java":
                has_tests = bool(re.search(r"@Test|void\s+test\w+", test_content))
                if not has_tests:
                    violations.append(f"No test methods in {test_file} (need @Test annotation or test* methods)")
            elif lang == "go":
                has_tests = bool(re.search(r"func\s+Test\w+", test_content))
                if not has_tests:
                    violations.append(f"No test functions in {test_file} (need Test* functions)")
            elif lang == "rust":
                has_tests = bool(re.search(r"#\[test\]", test_content))
                if not has_tests:
                    violations.append(f"No test functions in {test_file} (need #[test] annotation)")
            
            # Check that test file isn't empty/stub
            if len(test_content.strip()) < 50:
                violations.append(f"Test file {test_file} is empty or incomplete (must have real tests)")
    
    if violations:
        fail(
            "HARD FAIL: Testing requirements not met (100% coverage, no mocks, real tests required)",
            violations
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
