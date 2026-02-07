#!/usr/bin/env python3
"""
pre_write_code_policy: Comprehensive code policy enforcement across 15 languages.

Enforces:
1. Zero-tolerance prohibitions (placeholders, mocks, stubs, incomplete code)
2. Logic preservation (no removal of executable code)
3. Implementation completeness (all paths handled, no undefined behavior)
4. Language-specific constraints

Applies uniformly across: Python, JavaScript, TypeScript, Java, C, C++, C#, Go, 
Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB.
"""

import json
import sys
import re
from pathlib import Path

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

COMMENT_PREFIXES = ("#", "//", "/*", "*", "--", "<!--", "%")

def is_comment(line: str) -> bool:
    s = line.strip()
    return not s or s.startswith(COMMENT_PREFIXES)

def is_executable(line: str) -> bool:
    s = line.strip()
    if not s or is_comment(s):
        return False
    if re.fullmatch(r"[{}();,\[\]]+", s):
        return False
    return True

def count_exec(code: str) -> int:
    return sum(1 for l in code.splitlines() if is_executable(l))

def fail(msg, details=None):
    print("BLOCKED: pre_write_code policy violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"  • {d}", file=sys.stderr)
    sys.exit(2)

def detect_language(path: str) -> str:
    """Detect language from file extension."""
    ext = Path(path).suffix.lower()
    ext_map = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".java": "java",
        ".c": "c",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".go": "go",
        ".rs": "rust",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".kt": "kotlin",
        ".r": "r",
        ".m": "matlab",
    }
    return ext_map.get(ext, "unknown")

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    # Flatten all prohibited patterns
    prohibited_dict = policy.get("prohibited_patterns", {})
    all_prohibited = []
    if isinstance(prohibited_dict, dict):
        all_prohibited = sum(prohibited_dict.values(), [])

    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    context = payload.get("conversation_context", "") or ""

    violations = []

    for e in edits:
        old = e.get("old_string", "") or ""
        new = e.get("new_string", "") or ""
        path = e.get("path", "unknown")
        lang = detect_language(path)

        # Skip test files, config files
        if "test" in path.lower() or "spec" in path.lower() or path.endswith((".json", ".md", ".yaml", ".yml")):
            continue

        old_exec = count_exec(old)
        new_exec = count_exec(new)

        # ============================================================
        # ABSOLUTE ZERO-TOLERANCE PROHIBITION CHECKS
        # ============================================================
        
        # Check for absolute prohibitions (every single pattern)
        for pat in all_prohibited:
            matches = list(re.finditer(pat, new, re.IGNORECASE))
            for match in matches:
                line_num = new[:match.start()].count("\n") + 1
                violations.append(
                    f"HARD FAIL: Absolute prohibition '{pat}' found in {path}:{line_num}"
                )

        # ============================================================
        # IMPLEMENTATION COMPLETENESS CHECKS
        # ============================================================

        # No empty/stub implementations
        if lang == "python":
            # Check for stub/skeleton functions
            if re.search(r"def\s+\w+\s*\([^)]*\)\s*:\s*(?:pass|\.\.\.|\.\.\.|return|raise NotImplementedError)", new, re.MULTILINE):
                violations.append(f"Stub/skeleton function in {path} (not fully implemented)")
            # Check for unimplemented return paths
            if re.search(r"return\s*#.*comment only", new):
                violations.append(f"Return with comment-only value in {path}")

        if lang == "javascript":
            # Check for empty functions or stubs
            if re.search(r"(function\s+\w+|=>\s*)\s*\{\s*\}", new):
                violations.append(f"Empty function in {path} (not fully implemented)")
            if re.search(r"(function|const)\s+\w+.*\{\s*(?:throw new Error|return|console\.log|undefined)\s*\}", new):
                violations.append(f"Stub function in {path}")

        if lang in ("java", "cpp", "csharp"):
            # Check for empty bodies
            if re.search(r"(?:public|private|protected)\s+\w+.*\{\s*\}", new):
                violations.append(f"Empty method in {path} (not fully implemented)")

        if lang == "go":
            # Check for stub implementations
            if re.search(r"func\s+\w+.*\{\s*(?:return|panic|log\.Fatal)", new):
                violations.append(f"Stub function in {path}")

        if lang == "rust":
            # Check for unimplemented/todo macros
            if re.search(r"(?:unimplemented|todo)!\s*\(", new):
                violations.append(f"unimplemented!() or todo!() macro in {path}")

        # ============================================================
        # LOGIC PRESERVATION AND COMPLETENESS
        # ============================================================

        # No logic removal
        if old_exec > 0 and new_exec < old_exec and new.strip():
            violations.append(
                f"HARD FAIL: Logic removal in {path} ({old_exec} → {new_exec} lines)"
            )

        # No wholesale code deletion
        if old.strip() and not new.strip():
            violations.append(f"HARD FAIL: Code completely removed in {path}")

        # Check for unhandled branches/undefined behavior
        if lang == "python":
            # Missing exception handling
            funcs = re.finditer(r"def\s+(\w+)\s*\([^)]*\)\s*:", new)
            for func in funcs:
                func_start = func.end()
                # Find next function or EOF
                next_func = re.search(r"\ndef\s+\w+", new[func_start:])
                func_body_end = func_start + next_func.start() if next_func else len(new)
                func_body = new[func_start:func_body_end]
                
                # Check if function that calls external code has try/except
                if re.search(r"(?:open|requests\.|urllib\.|json\.load|os\.)", func_body) and \
                   not re.search(r"try:|except", func_body):
                    violations.append(
                        f"Missing error handling in {path} function {func.group(1)}"
                    )

        # ============================================================
        # REAL WORKING IMPLEMENTATION CHECKS
        # ============================================================

        # Check for placeholder code
        if re.search(r"(pass|None|0|\[\]|\{\}|\"\")\s*#.*real", new, re.IGNORECASE):
            violations.append(f"Placeholder code in {path}")

        # Check for hardcoded test/demo values
        if re.search(r"(demo_data|test_data|fake_|sample_|mock_)", new, re.IGNORECASE):
            violations.append(f"Hardcoded test/demo data in {path} (not production code)")

        # Check for conditional disabling
        if re.search(r"if\s+(False|0|None|\"\")\s*:|if\s+(__debug__|DEBUG|TEST)\s*:", new):
            violations.append(f"Conditionally disabled code in {path}")

        # Check for magic numbers without validation
        if re.search(r"(timeout|max|limit|threshold)\s*=\s*[0-9]+\s*#.*", new):
            # Warn if no comments explaining the choice
            if not re.search(r"(timeout|max|limit|threshold)\s*=\s*[0-9]+\s*#.*(?:based|empirical|tested|requirement)", new):
                violations.append(f"Magic number without justification in {path}")

    if violations:
        fail(
            "HARD FAIL: Code does not meet specification (must be real, working implementation)\n"
            "Violations:",
            violations
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
