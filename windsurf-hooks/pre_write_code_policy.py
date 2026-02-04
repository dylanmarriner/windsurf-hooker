#!/usr/bin/env python3
import json, sys, re
from pathlib import Path

POLICY_PATH = Path("/etc/windsurf/policy/policy.json")

COMMENT_PREFIXES = ("#", "//", "/*", "*", "--")

MOCK_PATTERNS = [
    r"\bunittest\.mock\b",
    r"\bMock\b",
    r"\bMagicMock\b",
    r"\bpytest\.mock\b",
    r"\bmock\.",
]

def is_comment(line: str) -> bool:
    s = line.strip()
    return not s or s.startswith(COMMENT_PREFIXES)

def is_executable(line: str) -> bool:
    s = line.strip()
    if not s or is_comment(s):
        return False
    if re.fullmatch(r"[{}();,]+", s):
        return False
    return True

def count_exec(code: str) -> int:
    return sum(1 for l in code.splitlines() if is_executable(l))

def fail(msg, details=None):
    print("BLOCKED: pre_write_code policy violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"- {d}", file=sys.stderr)
    sys.exit(2)

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    prohibited = policy.get("prohibited_patterns", {})
    patterns = sum(prohibited.values(), []) if isinstance(prohibited, dict) else []

    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    context = payload.get("conversation_context", "") or ""

    in_repair_mode = "[MODE:AUDITOR_OK]" in context and "[MODE:REPAIR_OK]" not in context

    violations = []

    for e in edits:
        old = e.get("old_string", "") or ""
        new = e.get("new_string", "") or ""

        old_exec = count_exec(old)
        new_exec = count_exec(new)

        for pat in patterns:
            if re.search(pat, new, re.IGNORECASE):
                violations.append(f"Prohibited pattern: {pat}")

        if in_repair_mode:
            for pat in MOCK_PATTERNS:
                if re.search(pat, new):
                    violations.append(f"Mock usage in REPAIR MODE: {pat}")

        if old_exec > 0 and new_exec < old_exec and new.strip():
            violations.append(f"Executable logic reduced ({old_exec} → {new_exec})")

        if old_exec > 0 and new_exec == 0 and new.strip():
            violations.append("Executable logic replaced by comments/text")

    if violations:
        fail("Illegal REPAIR behavior detected.", violations)

    sys.exit(0)

if __name__ == "__main__":
    main()
