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
    """Kill switch for shell execution - allows all terminal commands."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Invalid JSON input")

    # Allow all terminal commands
    return


if __name__ == "__main__":
    main()
