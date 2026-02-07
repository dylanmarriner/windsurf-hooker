#!/usr/bin/env python3
"""
pre_mcp_tool_use_atlas_gate: ATLAS-GATE Primary Gate (Hard Choke Point)

Core Invariant (Non-Negotiable):
- If a capability is not routed through ATLAS-GATE MCP tools, it is impossible
- No soft allow + warning
- No fallback paths
- No silent success

Behavior:
1. Reject any tool that is not an ATLAS-GATE MCP tool
2. Enforce policy allowlist when configured
3. Enforce panic-lock mode (execution_profile=locked)

Note:
- Windsurf-side hook validates routing/safety boundaries
- ATLAS-GATE MCP server validates payload schema and authority
"""

import json
import sys
from pathlib import Path
from typing import List, Optional

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

ATLAS_GATE_PREFIX = "mcp_atlas-gate-mcp_"

# ATLAS-GATE MCP bare tool names (from server.js)
ATLAS_GATE_BARE_TOOLS = {
    "begin_session",
    "write_file",
    "read_file",
    "read_audit_log",
    "read_prompt",
    "list_plans",
    "replay_execution",
    "verify_workspace_integrity",
    "generate_attestation_bundle",
    "verify_attestation_bundle",
    "export_attestation_bundle",
    "bootstrap_create_foundation_plan",
    "lint_plan",
}


def block(msg: str, details: Optional[List[str]] = None):
    """Hard block: no fallback, no warning, no proceed."""
    print(f"BLOCKED: {msg}", file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def main():
    """
    Primary gate: Only ATLAS-GATE tools permitted.

    Hard enforcement: no exceptions, no warnings, no fallbacks.
    Accepts both naming conventions: mcp_atlas-gate-mcp_* and bare ATLAS-GATE tool names.
    """
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Invalid JSON input")

    # Check execution profile for locked mode
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}
    execution_profile = policy.get("execution_profile", "standard")

    # In locked mode: ALL MCP tools blocked
    if execution_profile == "locked":
        block(
            "System is in LOCKED mode (panic button activated).",
            ["All MCP tool access is revoked.", "Contact administrator to unlock."],
        )

    tool = payload.get("tool_info", {}) or {}
    tool_name = (
        tool.get("tool_name")
        or tool.get("name")
        or tool.get("method")
        or ""
    )

    # Rule 1: Tool must exist
    if not tool_name:
        block("No tool specified in payload")

    # Rule 2: Tool must be ATLAS-GATE (either prefixed or bare name)
    is_prefixed = tool_name.startswith(ATLAS_GATE_PREFIX)
    is_bare = tool_name in ATLAS_GATE_BARE_TOOLS
    
    if not (is_prefixed or is_bare):
        block(
            "Only ATLAS-GATE tools are permitted",
            [
                f"Tool requested: {tool_name}",
                f"Tool must be ATLAS-GATE MCP (prefixed with '{ATLAS_GATE_PREFIX}' or be a known ATLAS-GATE tool)",
                "Direct filesystem, command execution, and native tools are disabled",
                "Route all requests through ATLAS-GATE",
            ],
        )

    # Rule 3: Tool should be in policy allowlist when configured
    allowed_tools = set(policy.get("mcp_tool_allowlist", []))
    if allowed_tools and tool_name not in allowed_tools:
        block(
            f"ATLAS-GATE tool not in allowlist: {tool_name}",
            [
                f"Allowed tools configured: {len(allowed_tools)}",
                "Update policy.mcp_tool_allowlist if this is intentional",
            ],
        )

    # Success: This tool is authorized
    sys.exit(0)


if __name__ == "__main__":
    main()
