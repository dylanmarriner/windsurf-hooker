#!/usr/bin/env python3
"""
pre_write_code_escape_detection: Prevent Capability Re-Introduction

Even in execution-only mode, the AI may try to write code that:
- Uses subprocess, os.system, open()
- Invokes socket/network APIs
- Creates shell wrappers
- Restores deleted execution primitives

This hook must block code that introduces execution primitives
even if not executed yet.

Why separate from pre_write_code_policy?

The main hook checks patterns from policy.json (configurable).
This hook enforces hardcoded escape patterns in execution-only mode.

Invariant:
If execution_profile is execution_only:
- No subprocess
- No os.system, os.popen
- No open() file operations (writes via ATLAS-GATE only)
- No socket, urllib, requests, httpx
- No exec, eval, compile, __import__
- No ctypes, cffi (direct system access)
- No shell wrappers (bash -c, sh -c, cmd /c)

These patterns are not configurable — they are hardcoded enforcement.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

# Hardcoded escape patterns (non-negotiable in execution_only mode)
ESCAPE_PATTERNS = {
    "subprocess": [
        r"subprocess\.",
        r"import subprocess",
        r"from subprocess",
    ],
    "os_execution": [
        r"os\.system",
        r"os\.popen",
        r"os\.execv",
        r"os\.spawn",
    ],
    "direct_execution": [
        r"exec\(",
        r"eval\(",
        r"compile\(",
        r"__import__\(",
    ],
    "file_operations": [
        r"open\(",
        r"\.write\(",
        r"\.read\(",
        r"Path.*write",
        r"Path.*read",
    ],
    "network": [
        r"socket\.",
        r"import socket",
        r"urllib\.",
        r"import urllib",
        r"requests\.",
        r"import requests",
        r"httpx\.",
        r"import httpx",
    ],
    "system_access": [
        r"ctypes\.",
        r"cffi\.",
        r"ffi\.",
    ],
    "shell_wrappers": [
        r"bash -c",
        r"sh -c",
        r"cmd /c",
        r"powershell -Command",
    ],
}


def block(msg: str, details: List[str] = None):
    """Block code that attempts to re-introduce execution."""
    print("BLOCKED: pre_write_code_escape_detection", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def detect_escape_patterns(code: str, path: str = "unknown") -> List[Dict]:
    """Scan code for escape attempt patterns."""
    violations = []

    for category, patterns in ESCAPE_PATTERNS.items():
        for pattern in patterns:
            matches = list(re.finditer(pattern, code, re.IGNORECASE | re.MULTILINE))
            if matches:
                for match in matches:
                    line_num = code[:match.start()].count("\n") + 1
                    violations.append(
                        {
                            "category": category,
                            "pattern": pattern,
                            "line": line_num,
                            "snippet": match.group(0),
                            "file": path,
                        }
                    )

    return violations


def main():
    """Scan code edits for escape attempts in execution-only mode."""
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

    # In execution_only mode: enforce hardcoded escape detection
    if execution_profile == "execution_only":
        edits = (payload.get("tool_info", {}) or {}).get("edits", [])

        all_violations = []
        for edit in edits:
            new_code = edit.get("new_string", "") or ""
            path = edit.get("path", "unknown")

            violations = detect_escape_patterns(new_code, path)
            all_violations.extend(violations)

        if all_violations:
            details = []
            for v in all_violations:
                details.append(
                    f"{v['file']}:{v['line']} ({v['category']}) → {v['snippet']}"
                )

            block(
                "Code contains escape attempts (execution primitives forbidden in execution_only mode)",
                details,
            )

    # In standard mode: apply configurable pattern enforcement
    # (Fall through to pre_write_code_policy)
    sys.exit(0)


if __name__ == "__main__":
    main()
