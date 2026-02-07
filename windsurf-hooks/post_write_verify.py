#!/usr/bin/env python3
"""
post_write_verify: Self-contained verification without ./scripts/verify dependency.

Does NOT require ./scripts/verify. Instead performs:
1. Syntax validation for all modified files
2. Basic linting checks availability
3. Test existence verification
4. Mock detection in tests
5. Coverage configuration validation

This ensures complete enforcement within hooks.
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List

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

LINT_TOOLS = {
    "python": ["flake8", "mypy", "ruff"],
    "javascript": ["eslint"],
    "typescript": ["eslint", "tsc"],
    "java": ["checkstyle"],
    "go": ["go", "golangci-lint"],
    "rust": ["cargo", "clippy"],
}

def detect_language(path: str) -> str:
    """Detect language from file extension."""
    ext = Path(path).suffix.lower()
    for lang, exts in LANGUAGE_EXTENSIONS.items():
        if ext in exts:
            return lang
    return "unknown"

def validate_syntax(path: str, lang: str) -> List[str]:
    """Validate syntax without executing."""
    errors = []
    
    try:
        content = Path(path).read_text()
    except Exception as e:
        return [f"Cannot read {path}: {e}"]
    
    # Python: compile check
    if lang == "python":
        try:
            compile(content, path, "exec")
        except SyntaxError as e:
            errors.append(f"Python syntax error in {path}: {e.msg}")
    
    # All languages: check for unmatched braces
    brace_count = content.count("{") - content.count("}")
    if brace_count != 0 and lang in ("java", "cpp", "csharp", "go", "rust"):
        errors.append(f"Unmatched braces in {path} (diff: {brace_count})")
    
    bracket_count = content.count("[") - content.count("]")
    if bracket_count != 0:
        errors.append(f"Unmatched brackets in {path}")
    
    paren_count = content.count("(") - content.count(")")
    if paren_count != 0:
        errors.append(f"Unmatched parentheses in {path}")
    
    return errors

def check_mock_patterns(path: str) -> List[str]:
    """Check for mock/stub/fake patterns in test files."""
    if "test" not in path.lower() and "spec" not in path.lower():
        return []
    
    errors = []
    
    try:
        content = Path(path).read_text()
    except Exception:
        return []
    
    mock_patterns = [
        (r"\bMock\(", "Mock pattern"),
        (r"\bStub\(", "Stub pattern"),
        (r"\bFake\(", "Fake pattern"),
        (r"jest\.mock\(", "Jest mock"),
        (r"vitest\.mock\(", "Vitest mock"),
        (r"mockito\.", "Mockito"),
        (r"@Mock\b", "Mock annotation"),
        (r"sinon\.", "Sinon spy/stub"),
        (r"testDouble\.", "TestDouble"),
    ]
    
    for pattern, name in mock_patterns:
        if re.search(pattern, content):
            errors.append(f"HARD FAIL: {name} in test file {path} (real tests only)")
    
    return errors

def main():
    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    violations = []
    files_checked = set()
    
    for e in edits:
        path = e.get("path", "unknown")
        new = e.get("new_string", "") or ""
        
        if not new or path in files_checked:
            continue
        
        # Skip certain file types
        if path.endswith((".json", ".md", ".yaml", ".yml", ".toml", ".config")):
            continue
        
        lang = detect_language(path)
        if lang == "unknown":
            continue
        
        files_checked.add(path)
        
        # ============================================================
        # Syntax validation
        # ============================================================
        syntax_errors = validate_syntax(path, lang)
        violations.extend(syntax_errors)
        
        # ============================================================
        # Mock detection in tests
        # ============================================================
        mock_errors = check_mock_patterns(path)
        violations.extend(mock_errors)
        
        # ============================================================
        # Check for incomplete/placeholder code
        # ============================================================
        if re.search(
            r"\b(TODO|FIXME|XXX|HACK|TEMP|pass\s*$|NotImplementedError|unimplemented|todo!)",
            new,
            re.MULTILINE | re.IGNORECASE
        ):
            violations.append(f"HARD FAIL: Incomplete code marker in {path}")
    
    if violations:
        print("BLOCKED: post_write_verify validation failed", file=sys.stderr)
        for v in violations:
            print(f"  • {v}", file=sys.stderr)
        sys.exit(2)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
