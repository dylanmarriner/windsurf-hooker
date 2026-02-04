#!/usr/bin/env python3
import json, sys
from pathlib import Path

POLICY_PATH = Path("/etc/windsurf/policy/policy.json")

def fail(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(2)

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    allow = set(policy.get("mcp_tool_allowlist", []))

    payload = json.load(sys.stdin)
    tool = payload.get("tool_info", {}) or {}

    tool_name = (
        tool.get("tool_name")
        or tool.get("name")
        or tool.get("method")
        or ""
    )

    if allow and tool_name and tool_name not in allow:
        fail(f"BLOCKED: MCP tool not allowed: {tool_name}")

    sys.exit(0)

if __name__ == "__main__":
    main()
