#!/usr/bin/env python3
"""
pre_filesystem_write_atlas_enforcement: Critical Filesystem Boundary

This is where most "execution-only" systems fail.

Core Rule (Non-Negotiable):
The agent never touches the filesystem directly.
It only asks ATLAS-GATE to do so.

In execution-only mode:
- All filesystem writes must go through atlas_gate.write
- Direct open() calls are blocked at pre_write_code_escape_detection
- This hook validates that no direct writes escape into code

Why separate from pre_filesystem_write?

The generic hook checks new file count and patterns.
This hook enforces the execution-only boundary:
- No writes to sensitive paths (.ssh, /etc, /proc, etc.)
- No binary blobs
- No escape attempts via file paths
- No build artifacts outside temp

Invariant:
If execution_profile is execution_only:
- Zero direct filesystem writes allowed
- All file operations must be requested via atlas_gate.write
- Violations block immediately, no fallback
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()

# Forbidden paths even in standard mode
FORBIDDEN_PATHS = {
    ".ssh": "SSH keys/config",
    ".aws": "AWS credentials",
    ".env": "Environment variables",
    ".git/config": "Git config",
    "/etc": "System configuration",
    "/proc": "System processes",
    "/sys": "System kernel",
    "/root": "Root home",
    "/var/log": "System logs",
    "build/": "Build artifacts",
    "dist/": "Distribution artifacts",
    "node_modules/": "Dependencies",
}

# File extensions that should never be written
FORBIDDEN_EXTENSIONS = {
    ".exe": "Executable",
    ".dll": "Dynamic library",
    ".so": "Shared object",
    ".bin": "Binary",
    ".pyc": "Compiled Python",
    ".o": "Object file",
    ".a": "Static library",
    ".iso": "Disk image",
    ".dmg": "macOS image",
    ".jar": "Java archive",
    ".whl": "Python wheel (pre-built)",
}


def block(msg: str, details: Optional[List[str]] = None):
    """Block filesystem write attempt."""
    print("BLOCKED: pre_filesystem_write_atlas_enforcement", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def is_forbidden_path(path: str) -> Optional[str]:
    """Check if path is in forbidden list."""
    path_lower = path.lower()

    for forbidden, reason in FORBIDDEN_PATHS.items():
        if forbidden in path_lower or path_lower.startswith(forbidden):
            return f"{reason} ({forbidden})"

    return None


def is_forbidden_extension(path: str) -> Optional[str]:
    """Check if file extension is in forbidden list."""
    for ext, reason in FORBIDDEN_EXTENSIONS.items():
        if path.endswith(ext):
            return f"{reason} ({ext})"

    return None


def is_escape_attempt(path: str) -> bool:
    """Detect obvious escape attempts in path."""
    # Path traversal
    if "../" in path or "..\\" in path:
        return True

    # Absolute paths
    if path.startswith("/") or path.startswith("\\\\"):
        return True

    # Home directory expansion (might be legitimate, but suspicious)
    if path.startswith("~"):
        return True

    return False


def analyze_filesystem_writes(edits: List[Dict], execution_profile: str) -> Dict:
    """Analyze filesystem write safety."""
    if not edits:
        return {"safe": True, "violations": []}

    violations = []
    new_files = []

    for edit in edits:
        path = edit.get("path", "")
        content = edit.get("new_string", "") or ""
        old_content = edit.get("old_string", "") or ""

        if not path:
            continue

        # Track new files
        if not old_content and content:
            new_files.append(path)

        # Check forbidden paths
        forbidden_reason = is_forbidden_path(path)
        if forbidden_reason:
            violations.append(
                {
                    "type": "forbidden_path",
                    "path": path,
                    "reason": forbidden_reason,
                }
            )

        # Check forbidden extensions
        ext_reason = is_forbidden_extension(path)
        if ext_reason:
            violations.append(
                {
                    "type": "forbidden_extension",
                    "path": path,
                    "reason": ext_reason,
                }
            )

        # Check escape attempts
        if is_escape_attempt(path):
            violations.append(
                {
                    "type": "escape_attempt",
                    "path": path,
                    "reason": "Path escape detected (../, absolute path, or ~)",
                }
            )

        # In execution_only mode: no direct writes at all
        if execution_profile == "execution_only" and path and content:
            # This file write is happening directly, not via ATLAS-GATE
            violations.append(
                {
                    "type": "execution_only_violation",
                    "path": path,
                    "reason": "Direct filesystem write not allowed in execution-only mode (use atlas_gate.write)",
                }
            )

    return {
        "safe": len(violations) == 0,
        "violations": violations,
        "new_files": len(new_files),
    }


def main():
    """Enforce filesystem write boundary."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        block("Invalid JSON input")

    # Check execution profile
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}

    execution_profile = policy.get("execution_profile", "standard")

    # In locked mode: ALL filesystem writes blocked
    if execution_profile == "locked":
        block(
            "System is in LOCKED mode (panic button activated).",
            ["All filesystem writes are revoked.", "Contact administrator to unlock."],
        )

    edits = (payload.get("tool_info", {}) or {}).get("edits", [])

    analysis = analyze_filesystem_writes(edits, execution_profile)

    if not analysis["safe"]:
        details = []
        for v in analysis["violations"]:
            details.append(f"{v['path']}: {v['reason']} ({v['type']})")

        block("Filesystem write policy violation", details)

    # Success
    sys.exit(0)


if __name__ == "__main__":
    main()
