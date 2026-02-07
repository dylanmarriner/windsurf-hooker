#!/usr/bin/env python3
"""
pre_run_command_kill_switch: Absolute Kill Switch for Direct Command Execution

Execution-Only Mode Enforcement

This hook must be trivial but absolute:
- Direct command execution is disabled
- Period. No exceptions.
- No regex needed, no policy lookup, no heuristics

If this hook ever allows execution → system is compromised.

Why separate from pre_run_command_blocklist?

The blocklist uses regex patterns — inherently permissive.
This hook is: deny by default, no exceptions.

Invariant:
If execution profile is "execution_only" → all commands blocked.
No fallback. No "safe" commands. No shell workarounds.
"""

import json
import sys
from pathlib import Path

POLICY_PATH = Path("/etc/windsurf/policy/policy.json")


def block(msg: str):
    """Hard block: execution disabled in this mode."""
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    """Unconditional kill switch for direct command execution."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("BLOCKED: Invalid JSON input")

    # Check execution profile
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    execution_profile = policy.get("execution_profile", "standard")

    # In locked mode: ALL capabilities revoked
    if execution_profile == "locked":
        block(
            "BLOCKED: System is in LOCKED mode (panic button activated).\n"
            "  All shell execution and capabilities are revoked.\n"
            "  Contact administrator to unlock."
        )

    # In execution_only mode: no direct commands ever
    if execution_profile == "execution_only":
        tool = payload.get("tool_info", {}) or {}
        command = (tool.get("command") or "").strip()

        block(
            "BLOCKED: Direct command execution is disabled.\n"
            "  Reason: Execution-only mode (ATLAS-GATE enforced)\n"
            f"  Command requested: {command}\n"
            "  Solution: Use atlas_gate.exec to request execution"
        )

    # In standard mode: fall back to pattern blocklist
    # (Let pre_run_command_blocklist handle it)
    sys.exit(0)


if __name__ == "__main__":
    main()
