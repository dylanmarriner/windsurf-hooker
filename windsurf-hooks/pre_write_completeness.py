#!/usr/bin/env python3
"""
pre_write_completeness: Enforce 100% Implementation (No TODOs, Stubs, Placeholders)

Core Invariant:
- All code must be 100% implemented
- No TODO, FIXME, XXX, HACK comments (any case variant)
- No stub functions (pass, NotImplementedError, ...)
- No placeholder returns (None, {}, [], etc. as full function body)
- All control paths must have real executable code
- No unimplemented features or deferred work

This hook enforces COMPLETENESS at the IDE level BEFORE reaching ATLAS-GATE.
Code must be done, not sketched.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

# Patterns that indicate incomplete code (comprehensive list for all languages)
INCOMPLETENESS_PATTERNS = {
    "todo_comments": [
        r"#\s*(TODO|FIXME|XXX|HACK|BUG|TEMP|LATER|SOMEDAY|BROKEN)\b",  # Python/shell/Ruby/#R/MATLAB
        r"//\s*(TODO|FIXME|XXX|HACK|BUG|TEMP|LATER|SOMEDAY|BROKEN)\b",  # JS/TS/C/C++/Go/Rust/Java/C#/Swift/Kotlin/PHP
        r"/\*\s*(TODO|FIXME|XXX|HACK|BUG|TEMP|LATER|SOMEDAY|BROKEN)\b",  # Block comments (all C-like)
        r"--\s*(TODO|FIXME|XXX|HACK|BUG|TEMP|LATER|SOMEDAY|BROKEN)\b",  # SQL/Lua
        r"%\s*(TODO|FIXME|XXX|HACK|BUG|TEMP|LATER|SOMEDAY|BROKEN)\b",  # MATLAB
    ],
    "note_comments": [
        r"#\s*(NOTE|REMEMBER|IMPORTANT):\s*implement",  # Masked TODO
        r"//\s*(NOTE|REMEMBER|IMPORTANT):\s*implement",
        r"%\s*(NOTE|REMEMBER|IMPORTANT):\s*implement",
    ],
    "stub_keywords": [
        # Python
        r"\bpass\s*$",  # Python pass (only in empty except)
        r"^\s*\.\.\.\s*$",  # Python ellipsis
        # Universal errors
        r"\bNotImplementedError",  # Python stub error
        r"\bNotImplementedException",  # C# stub error
        r"\bUnsupportedOperationException",  # Java stub error
        # Rust
        r"\bunimplemented!\s*\(",  # Rust unimplemented!
        r"\btodo!\s*\(",  # Rust todo!
        # Go
        r"\bpanic\s*\(\s*['\"].*not\s+implemented",  # Go panic("not implemented")
        r"\bpanic\s*\(\s*['\"].*TODO",  # Go panic("TODO")
        # C/C++ - catch runtime_error for "not implemented" or "implement"
        r"std::runtime_error\s*\(\s*['\"].*implement",  # C++ throw runtime_error("...implement...")
        r"throw\s+std::runtime_error",  # Any std::runtime_error throw (often stub)
        # Java/C#
        r"\bthrow\s+new\s+(NotImplementedException|UnsupportedOperationException)",
        # Swift
        r"\bfatalError\s*\(\s*['\"].*implement",  # Swift fatalError
    ],
    "empty_returns": [
        r"^\s*return\s*;?\s*$",  # return with no value (C/C++/Java/C#/Rust/Go/Swift/Kotlin/PHP)
        r"^\s*return\s+(None|nil|null)\s*;?\s*$",  # return None/nil/null
    ],
    "placeholder_returns": [
        r"^\s*return\s+\{\}\s*;?\s*$",  # return {}
        r"^\s*return\s+\[\]\s*;?\s*$",  # return []
        r'^\s*return\s+(""|\'\')\s*;?\s*$',  # return ""
        r"^\s*return\s+(0|false|False)\s*;?\s*$",  # return 0/false
        r"^\s*return\s+vec!\[\]\s*;?\s*$",  # Rust empty vec
    ],
}

# Allowed contexts where pass is OK (empty except blocks)
ALLOWED_PASS_CONTEXTS = [
    r"except\s*.*:\s*pass",  # except: pass
    r"except\s+\w+\s*:\s*pass",  # except Exception: pass
]


def block(msg: str, details: List[str] = None):
    """Block incomplete code."""
    print("BLOCKED: pre_write_completeness - Code is incomplete", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def detect_todo_comments(code: str, path: str = "unknown") -> List[Dict]:
    """Find TODO, FIXME, XXX, HACK comments."""
    violations = []
    
    for category, patterns in {
        "todo_comments": INCOMPLETENESS_PATTERNS["todo_comments"],
        "note_comments": INCOMPLETENESS_PATTERNS["note_comments"],
    }.items():
        for pattern in patterns:
            for match in re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE):
                line_num = code[:match.start()].count("\n") + 1
                line_text = code.split("\n")[line_num - 1].strip()
                violations.append({
                    "type": category,
                    "line": line_num,
                    "file": path,
                    "snippet": match.group(0),
                    "full_line": line_text[:80],  # First 80 chars
                })
    
    return violations


def detect_stub_functions(code: str, path: str = "unknown") -> List[Dict]:
    """Find stub functions (pass, NotImplementedError, ...) and exception stubs."""
    violations = []
    lines = code.split("\n")
    
    # Check for stub keywords using the comprehensive patterns
    for pattern in INCOMPLETENESS_PATTERNS["stub_keywords"]:
        for match in re.finditer(pattern, code, re.MULTILINE | re.IGNORECASE):
            line_num = code[:match.start()].count("\n") + 1
            line_text = code.split("\n")[line_num - 1].strip()
            violations.append({
                "type": "stub_function",
                "line": line_num,
                "file": path,
                "snippet": match.group(0)[:60],
                "reason": f"Stub or incomplete marker: {match.group(0)[:40]}",
            })
    
    # Check for bare pass statements (only in except/try contexts)
    for i, line in enumerate(lines, 1):
        if re.match(r"^\s*pass\s*$", line):
            # Check if it's in an allowed context
            in_except_block = False
            for j in range(max(0, i - 5), i):  # Look back up to 5 lines
                if re.search(r"except\s*(\w+\s*)?:", lines[j]):
                    in_except_block = True
                    break
            
            if not in_except_block:
                violations.append({
                    "type": "stub_function",
                    "line": i,
                    "file": path,
                    "snippet": "pass",
                    "reason": "bare 'pass' outside of except block indicates unfinished code",
                })
    
    return violations


def detect_placeholder_returns(code: str, path: str = "unknown") -> List[Dict]:
    """Find placeholder return statements."""
    violations = []
    
    for pattern_type, patterns in {
        "empty_return": INCOMPLETENESS_PATTERNS["empty_returns"],
        "placeholder_return": INCOMPLETENESS_PATTERNS["placeholder_returns"],
    }.items():
        for pattern in patterns:
            for match in re.finditer(pattern, code, re.MULTILINE):
                line_num = code[:match.start()].count("\n") + 1
                violations.append({
                    "type": "placeholder_return",
                    "line": line_num,
                    "file": path,
                    "snippet": match.group(0),
                    "reason": f"Placeholder {pattern_type}: {match.group(0)}",
                })
    
    return violations


def detect_incomplete_functions(code: str, path: str = "unknown") -> List[Dict]:
    """Find functions with only comments/docstrings (no implementation)."""
    violations = []
    
    # Simple heuristic: look for function definitions followed only by docstring/comments
    # This is a conservative check to avoid false positives
    
    # JavaScript/TypeScript/Python function patterns
    patterns = [
        (r"^\s*(def|function|async function)\s+\w+\s*\([^)]*\)\s*[{:]?\s*$", "function_definition"),
    ]
    
    lines = code.split("\n")
    for i, line in enumerate(lines):
        for pattern, match_type in patterns:
            if re.match(pattern, line):
                # Check next 3 lines for actual code
                has_code = False
                for j in range(i + 1, min(i + 4, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith("#") and not next_line.startswith("//"):
                        if '"""' not in next_line and "'''" not in next_line:
                            has_code = True
                            break
                
                # If no code found, it might be incomplete
                # But be conservative—only flag if it's super obvious
                if not has_code and i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if next_line == "pass" or next_line == "..." or next_line == "":
                        violations.append({
                            "type": "incomplete_function",
                            "line": i + 1,
                            "file": path,
                            "snippet": line.strip()[:80],
                            "reason": "Function appears to be defined but not implemented",
                        })
    
    return violations


def main():
    """Check code for completeness violations."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    
    # Check execution profile
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}
    
    execution_profile = policy.get("execution_profile", "standard")
    
    # In locked mode: ALL code writes blocked
    if execution_profile == "locked":
        block(
            "System is in LOCKED mode (panic button activated).",
            ["All code writes are revoked.", "Contact administrator to unlock."],
        )
    
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    all_violations = []
    
    for edit in edits:
        new_code = edit.get("new_string", "") or ""
        path = edit.get("path", "unknown")
        
        # Skip test files and mock files (they are allowed to have stubs sometimes)
        if "test" in path.lower() or "mock" in path.lower():
            continue
        
        # Check for TODOs
        all_violations.extend(detect_todo_comments(new_code, path))
        
        # Check for stub functions
        all_violations.extend(detect_stub_functions(new_code, path))
        
        # Check for placeholder returns
        all_violations.extend(detect_placeholder_returns(new_code, path))
        
        # Check for incomplete functions
        all_violations.extend(detect_incomplete_functions(new_code, path))
    
    if all_violations:
        details = []
        for v in all_violations:
            line_info = f"{v['file']}:{v['line']}"
            snippet = v.get("snippet", "").replace("\n", " ")[:60]
            reason = v.get("reason", v["type"])
            details.append(f"{line_info} - {reason}")
            if snippet:
                details.append(f"     {snippet}")
        
        block(
            "Code contains incomplete markers or stub implementations. "
            "All code must be 100% implemented, no TODOs, FIXMEs, or placeholder returns.",
            details,
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
