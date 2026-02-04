#!/usr/bin/env python3
import json, re, sys
from pathlib import Path

POLICY_PATH = Path("/etc/windsurf/policy/policy.json")

INTENT = re.compile(
    r"\b(implement|write code|generate|edit|refactor|add feature|create file|change code|patch)\b",
    re.I
)

def block(msg: str):
    print(msg, file=sys.stderr)
    sys.exit(2)

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    tokens = policy.get("tokens", {})
    audit_ok = tokens.get("audit_ok")
    ship_ok = tokens.get("ship_ok")

    if not audit_ok or not ship_ok:
        block("BLOCKED: policy.tokens.audit_ok and ship_ok must be defined")

    payload = json.load(sys.stdin)
    prompt = (payload.get("tool_info", {}) or {}).get("prompt", "") or ""

    if INTENT.search(prompt):
        if audit_ok not in prompt:
            block(f"BLOCKED: audit required. Include token {audit_ok}")
        if ship_ok not in prompt and "proceed" in prompt.lower():
            block(f"BLOCKED: shipping gate required. Include token {ship_ok}")

    sys.exit(0)

if __name__ == "__main__":
    main()
