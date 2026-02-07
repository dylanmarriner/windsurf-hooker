#!/usr/bin/env python3
"""
pre_filesystem_write: Prevent pathological file creation.

Checks:
- File explosion (too many new files)
- Writes outside repo root
- Binary blobs being written
- Suspicious patterns (node_modules, .git, cache dirs)

Invariant:
- Codegen should be surgical, not expansive
- Never block legitimate writes; detect anomalies
- Fail-open: if can't verify, allow (don't guess)
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict

# Patterns that should trigger warnings
SUSPICIOUS_PATTERNS = [
    r"node_modules",
    r"\.git",
    r"\.env",
    r"__pycache__",
    r"dist",
    r"build",
    r"\.cache",
    r"\.tmp",
    r"venv",
]

# Extensions that are suspicious for creation (not typical code)
SUSPICIOUS_EXTENSIONS = [
    ".exe",
    ".dll",
    ".so",
    ".bin",
    ".pyc",
    ".o",
    ".a",
    ".iso",
    ".dmg",
]

# Max new files in single write pass
MAX_NEW_FILES = 50

# Binary file signatures
BINARY_SIGNATURES = [
    b"\x89PNG",  # PNG
    b"\xff\xd8\xff",  # JPEG
    b"GIF8",  # GIF
    b"%PDF",  # PDF
    b"PK\x03\x04",  # ZIP
    b"\x50\x4b\x03\x04",  # ZIP (alt)
]


def is_binary_file(path_str: str) -> bool:
    """Detect if file path suggests binary content."""
    p = Path(path_str)

    # Extension-based check
    if p.suffix.lower() in SUSPICIOUS_EXTENSIONS:
        return True

    # Path-based heuristics
    if any(
        re.search(pattern, path_str, re.IGNORECASE)
        for pattern in [r"\.jar$", r"\.whl$", r"\.tar\.gz$", r"\.zip$", r"\.rar$"]
    ):
        return True

    return False


def is_outside_repo(path_str: str) -> bool:
    """Check if path would escape repo root."""
    try:
        p = Path(path_str).resolve()
        repo_root = Path.cwd().resolve()

        # Check if path is under repo root
        return not str(p).startswith(str(repo_root))
    except Exception:
        # If we can't determine, err on side of caution
        return "/../" in path_str or path_str.startswith("/")


def is_suspicious_path(path_str: str) -> bool:
    """Check if path matches suspicious patterns."""
    return any(
        re.search(pattern, path_str, re.IGNORECASE) for pattern in SUSPICIOUS_PATTERNS
    )


def analyze_filesystem_writes(edits: List[Dict]) -> Dict[str, any]:
    """Analyze filesystem write safety."""
    if not edits:
        return {"fs_write_safe": True, "warnings": []}

    warnings = []
    new_files = []
    outside_repo = []
    binary_files = []
    suspicious = []

    for edit in edits:
        path = edit.get("path", "")
        if not path:
            continue

        # Check if file already existed
        file_exists = Path(path).exists()
        if not file_exists:
            new_files.append(path)

        # Check for escape attempts
        if is_outside_repo(path):
            outside_repo.append(path)
            warnings.append(f"Path escapes repo root: {path}")

        # Check for binary files
        if is_binary_file(path):
            binary_files.append(path)
            warnings.append(f"Suspicious binary file creation: {path}")

        # Check for suspicious patterns
        if is_suspicious_path(path):
            suspicious.append(path)
            warnings.append(f"Suspicious path pattern: {path}")

    # Check new file explosion
    if len(new_files) > MAX_NEW_FILES:
        warnings.append(
            f"Too many new files ({len(new_files)} > {MAX_NEW_FILES}) - "
            f"possible file explosion (codegen should be surgical)"
        )

    # Safety status
    fs_write_safe = (
        len(outside_repo) == 0
        and len(binary_files) == 0
        and len(suspicious) == 0
        and len(new_files) <= MAX_NEW_FILES
    )

    return {
        "fs_write_safe": fs_write_safe,
        "warnings": warnings,
        "metrics": {
            "new_files": len(new_files),
            "new_files_list": new_files,
            "outside_repo": len(outside_repo),
            "binary_files": len(binary_files),
            "suspicious_paths": len(suspicious),
        },
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"fs_write_safe": True, "warnings": []}))
        sys.exit(0)

    edits = (payload.get("tool_info", {}) or {}).get("edits", [])

    analysis = analyze_filesystem_writes(edits)

    # Always block if fs_write_safe is False
    if not analysis["fs_write_safe"]:
        print("BLOCKED: filesystem write safety violation", file=sys.stderr)
        for warning in analysis["warnings"]:
            print(f"  - {warning}", file=sys.stderr)
        sys.exit(2)

    # Otherwise, emit analysis for logging
    print(json.dumps(analysis))

    sys.exit(0)


if __name__ == "__main__":
    main()
