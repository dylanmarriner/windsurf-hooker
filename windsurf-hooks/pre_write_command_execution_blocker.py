#!/usr/bin/env python3
"""
pre_write_command_execution_blocker: Block all command execution and bypass attempts.

Enforces:
1. No shell commands (sh, bash, cmd, powershell, etc.)
2. No subprocess/process execution (subprocess, Popen, fork, etc.)
3. No code execution bypasses (__import__, eval, compile, etc.)
4. No tool bypass attempts (direct file access, disabled enforcement, etc.)
5. No network command execution (curl, wget, ssh piped to shell, etc.)

All operations must go through atlas-gate tools only.
"""

import json
import sys
import re
from pathlib import Path

def resolve_policy_path() -> Path:
    """Resolve policy path."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

def fail(msg, details=None):
    print("BLOCKED: Command execution detected - policy violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"  • {d}", file=sys.stderr)
    sys.exit(2)

def main():
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    # Get all execution-related prohibitions
    prohibited_dict = policy.get("prohibited_patterns", {})
    
    command_patterns = prohibited_dict.get("command_execution_patterns", [])
    code_bypass_patterns = prohibited_dict.get("code_execution_bypass", [])
    tool_bypass_patterns = prohibited_dict.get("tool_bypass_patterns", [])
    network_patterns = prohibited_dict.get("network_command_execution", [])
    
    all_patterns = command_patterns + code_bypass_patterns + tool_bypass_patterns + network_patterns

    payload = json.load(sys.stdin)
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    violations = []

    for e in edits:
        new = e.get("new_string", "") or ""
        path = e.get("path", "unknown")
        
        # Skip test files, config files
        if any(x in path.lower() for x in ["test", "spec", "mock"]):
            continue
        if path.endswith((".json", ".md", ".yaml", ".yml", ".toml")):
            continue
        
        # ============================================================
        # COMMAND EXECUTION CHECK
        # ============================================================
        for pat in command_patterns:
            matches = list(re.finditer(pat, new, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = new[:match.start()].count("\n") + 1
                violations.append(
                    f"HARD FAIL: Command execution pattern '{pat}' in {path}:{line_num} "
                    f"(Use atlas_gate.write or atlas_gate.exec tools only)"
                )
        
        # ============================================================
        # CODE EXECUTION BYPASS CHECK
        # ============================================================
        for pat in code_bypass_patterns:
            matches = list(re.finditer(pat, new, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = new[:match.start()].count("\n") + 1
                violations.append(
                    f"HARD FAIL: Code execution bypass '{pat}' in {path}:{line_num} "
                    f"(Dynamic code execution forbidden)"
                )
        
        # ============================================================
        # TOOL BYPASS CHECK
        # ============================================================
        for pat in tool_bypass_patterns:
            matches = list(re.finditer(pat, new, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = new[:match.start()].count("\n") + 1
                violations.append(
                    f"HARD FAIL: Tool bypass attempt '{pat}' in {path}:{line_num} "
                    f"(All operations must use atlas-gate tools)"
                )
        
        # ============================================================
        # NETWORK COMMAND EXECUTION CHECK
        # ============================================================
        for pat in network_patterns:
            matches = list(re.finditer(pat, new, re.IGNORECASE | re.MULTILINE))
            for match in matches:
                line_num = new[:match.start()].count("\n") + 1
                violations.append(
                    f"HARD FAIL: Network command execution '{pat}' in {path}:{line_num} "
                    f"(Use atlas_gate.exec for authorized operations)"
                )
    
    if violations:
        fail(
            "HARD FAIL: Command/code execution attempt blocked\n"
            "All operations must use atlas-gate tools (atlas_gate.write, atlas_gate.exec, etc.)",
            violations
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
