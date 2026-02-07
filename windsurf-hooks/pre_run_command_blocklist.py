#!/usr/bin/env python3
"""
pre_run_command_blocklist: Shell execution kill switch (ATLAS-GATE sandbox)

In ATLAS-GATE Windsurf mode:
- Shell execution is explicitly disabled
- All operations must route through MCP tools (mcp_atlas-gate-mcp_*)
- This is an unconditional kill, not a pattern blocklist

Design: ATLAS-GATE sandbox invariant. Shell is disabled by default.
"""

import json
import sys
from pathlib import Path


def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()


def block(msg: str):
    """Hard block: shell is disabled."""
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    """Kill switch for shell execution - blocks ALL terminal commands."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("BLOCKED: Invalid JSON input")
    
    # Get policy
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}
    
    # Check if any command is being executed
    command = payload.get("command", "")
    
    if command:
        block(
            f"BLOCKED: Shell command execution disabled\n"
            f"         Command: {command}\n"
            f"         All operations must use atlas-gate tools only\n"
            f"         Authorized tools: atlas_gate.write, atlas_gate.read, atlas_gate.exec"
        )


if __name__ == "__main__":
    main()
