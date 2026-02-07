#!/usr/bin/env python3
"""
pre_filesystem_write_enforcement_protection: Protect enforcement system files.

Enforces:
1. /usr/local/share/windsurf-hooks/ - READ-ONLY (no direct writes)
2. /etc/windsurf/policy/policy.json - READ-ONLY (no direct writes)
3. ~/.local/share/windsurf-hooks/ - READ-ONLY (no direct writes)

All modifications must go through atlas_gate.write tool only.

This prevents tampering with the enforcement system itself.
"""

import json
import sys
from pathlib import Path

PROTECTED_PATHS = [
    "/usr/local/share/windsurf-hooks/",
    "/etc/windsurf/policy/",
    "/.local/share/windsurf-hooks/",
]

def fail(msg, details=None):
    print("BLOCKED: Enforcement system protection violation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for d in details:
            print(f"  • {d}", file=sys.stderr)
    sys.exit(2)

def main():
    payload = json.load(sys.stdin)
    
    # Check if write is going through atlas_gate tool
    tool_info = payload.get("tool_info", {}) or {}
    tool_name = tool_info.get("tool_name", "")
    
    # Only atlas_gate.write is allowed
    if tool_name != "atlas_gate.write":
        # Check if any protected paths are being modified
        edits = tool_info.get("edits", []) or []
        
        violations = []
        for e in edits:
            path = e.get("path", "")
            
            # Check if this is a protected enforcement system file
            for protected in PROTECTED_PATHS:
                if path.startswith(protected):
                    violations.append(
                        f"HARD FAIL: Cannot write to protected enforcement system file: {path}\n"
                        f"          All modifications to enforcement system must use atlas_gate.write tool"
                    )
        
        if violations:
            fail(
                "Enforcement system protection active: direct writes forbidden",
                violations
            )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
