#!/usr/bin/env python3
"""
pre_write_code_policy: Code policy enforcement (escape primitives, mocks, logic preservation)

This hook checks:
1. Prohibited patterns (placeholders, mocks, hacks, escape attempts)
2. Logic preservation (don't remove executable code)
3. REPAIR mode constraints (no mocks)

Design: Defense-in-depth code quality checks.
ATLAS-GATE is the authoritative source for plan/write validation.
This hook does NOT check plan correctness (that's ATLAS-GATE's job).
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

    # Detect operational modes from context
    in_repair_mode = "[MODE:REPAIR]" in context
    in_plan_mode = "[MODE:PLAN]" in context
    plan_ok = "PLAN_OK=true" in context or "[PLAN_OK]" in context

    violations = []

    for e in edits:
        old = e.get("old_string", "") or ""
        new = e.get("new_string", "") or ""
        path = e.get("path", "unknown")

        old_exec = count_exec(old)
        new_exec = count_exec(new)

        # Check for prohibited patterns in new code
        for pat in patterns:
            if re.search(pat, new, re.IGNORECASE):
                violations.append(f"Prohibited pattern in {path}: {pat}")

        # In REPAIR mode, mock patterns are forbidden
        if in_repair_mode:
            for pat in MOCK_PATTERNS:
                if re.search(pat, new):
                    violations.append(f"Mock usage forbidden in REPAIR mode: {pat}")

        # Check executable logic preservation (strong rule)
        if old_exec > 0 and new_exec < old_exec and new.strip():
            violations.append(f"Logic reduction in {path}: {old_exec} → {new_exec} lines")

        if old_exec > 0 and new_exec == 0 and new.strip():
            violations.append(f"Logic removed in {path} (replaced by text/comments)")

    if violations:
        fail("Code policy violation detected.", violations)

    sys.exit(0)

if __name__ == "__main__":
    main()
