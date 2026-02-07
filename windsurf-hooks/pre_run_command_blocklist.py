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


POLICY_PATH = Path("/etc/windsurf/policy/policy.json")


def block(msg: str):
    """Hard block: shell is disabled."""
    print(msg, file=sys.stderr)
    sys.exit(2)


def main():
    """Unconditional kill switch for shell execution."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Invalid JSON input")

    tool = payload.get("tool_info", {}) or {}
    command = (tool.get("command") or "").strip()

    block(
        "BLOCKED: Direct shell execution is disabled.\n"
        "  Reason: ATLAS-GATE sandbox mode (MCP-only enforcement)\n"
        f"  Command requested: {command}\n"
        "  Solution: Use mcp_atlas-gate-mcp_* tools instead"
    )


if __name__ == "__main__":
    main()
