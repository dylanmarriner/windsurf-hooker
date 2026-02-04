#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

POLICY_PATH = Path("/etc/windsurf/policy/policy.json")

def fail(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(2)

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    payload = json.load(sys.stdin)
    tool = payload.get("tool_info", {}) or {}
    cmd = (tool.get("command") or "").strip()

    for rx in policy.get("block_commands_regex", []):
        if re.search(rx, cmd, re.I):
            fail(f"BLOCKED: command matches prohibited pattern\nPattern: {rx}\nCommand: {cmd}")

    sys.exit(0)

if __name__ == "__main__":
    main()
