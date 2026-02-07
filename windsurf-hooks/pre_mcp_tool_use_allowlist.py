#!/usr/bin/env python3
"""
pre_mcp_tool_use_allowlist: ATLAS-GATE MCP tool enforcement

Enforces:
1. Only ATLAS-GATE tools are permitted (all mcp_atlas-gate-mcp_*)
2. Session initialization order (begin_session must be first)
3. Plan hash presence on write_file (never validates, only ensures presence)

Design: Windsurf enforces sandbox constraints; ATLAS-GATE enforces authority.
"""

import json
import sys
from pathlib import Path
from typing import Optional, List

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()


def block(msg: str, details: Optional[List[str]] = None):
    """Hard block: no fallback, no warning, no proceed."""
    print(f"BLOCKED: {msg}", file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def load_policy() -> dict:
    """Load policy from /etc/windsurf/policy/policy.json"""
    if not POLICY_PATH.exists():
        return {}
    try:
        return json.loads(POLICY_PATH.read_text())
    except json.JSONDecodeError:
        return {}


def main():
    """Enforce ATLAS-GATE MCP tool access."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Invalid JSON input")

    policy = load_policy()
    allowed_tools = set(policy.get("mcp_tool_allowlist", []))

    tool = payload.get("tool_info", {}) or {}
    tool_name = (
        tool.get("tool_name")
        or tool.get("name")
        or tool.get("method")
        or ""
    ).strip()

    # Rule 1: Tool must be specified
    if not tool_name:
        block("No tool specified in payload")

    # Rule 2: Tool must be in allowlist (only ATLAS-GATE tools)
    if allowed_tools and tool_name not in allowed_tools:
        block(
            f"Tool '{tool_name}' is not permitted",
            [
                f"Only ATLAS-GATE tools are allowed",
                f"Tool must begin with 'mcp_atlas-gate-mcp_'",
                f"Allowed tools: {len(allowed_tools)} configured in policy",
            ],
        )

    # Rule 3: Session initialization enforcement
    conversation_context = payload.get("conversation_context", "") or ""
    
    if tool_name == "mcp_atlas-gate-mcp_begin_session":
        # This is the first call, always allowed
        sys.exit(0)

    # For all other tools: session must be initialized
    if "ATLAS_SESSION_OK" not in conversation_context:
        block(
            "ATLAS session not initialized",
            [
                "Must call mcp_atlas-gate-mcp_begin_session first",
                "Current tool: " + tool_name,
            ],
        )

    # Rule 4: read_prompt must be called before writes
    if tool_name == "mcp_atlas-gate-mcp_write_file":
        # Enforce prompt unlock
        if "ATLAS_PROMPT_UNLOCKED" not in conversation_context:
            block(
                "Prompt not read before write",
                [
                    "Must call mcp_atlas-gate-mcp_read_prompt before write_file",
                ],
            )

        # Enforce plan hash presence
        # We do NOT validate it; ATLAS-GATE does that
        plan_hash = tool.get("plan") or ""
        if not plan_hash or not plan_hash.strip():
            block(
                "write_file requires plan hash (BLAKE3)",
                [
                    "Plan hash must be supplied in 'plan' field",
                    "Windsurf does not validate hashes; ATLAS-GATE does",
                    "If you don't have a plan hash, call mcp_atlas-gate-mcp_list_plans",
                ],
            )

    # All checks passed
    sys.exit(0)


if __name__ == "__main__":
    main()
