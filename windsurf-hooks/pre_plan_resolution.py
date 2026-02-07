#!/usr/bin/env python3
"""
pre_plan_resolution: Dynamically discover and attach plan metadata to context.

Separates code from structure. Plans grant capability; absence never removes it.

Invariant:
- If plan exists → annotate (PLAN_OK=true, plan_path, declared_scope)
- If not → silently no-op (PLAN_OK=false)
- Never block on missing plan
- Plans are monotonic: discovered early, used late

Rules:
1. Search common plan locations (README.md, PLAN.md, .plan/, docs/PLAN/)
2. Extract scope declaration (files, directories, modules)
3. Validate references point to real files (no false positives)
4. Return structured metadata for downstream hooks
"""

import json
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional

# Common plan file locations and patterns
PLAN_SEARCH_PATHS = [
    "PLAN.md",
    ".plan/PLAN.md",
    "docs/PLAN.md",
    "docs/architecture/PLAN.md",
    ".github/PLAN.md",
    "README.md",  # May contain inline plan
]

PLAN_MARKERS = [
    r"^#+\s+(?:Plan|Implementation Plan|Task Plan|Scope)",
    r"^##\s+Files?(?:\s+to\s+(?:modify|edit|create))?:",
    r"^##\s+Scope:",
    r"^-\s+\[x\]\s+",  # Checklist items
]

SCOPE_PATTERNS = [
    r"(?:files?|paths?|modules?|directories?):\s*(.+?)(?:\n\n|$)",
    r"(?:scope|coverage|affects?):\s*(.+?)(?:\n\n|$)",
    r"(?:directory|dir):\s*(.+?)(?:\n\n|$)",
]


def find_plan_file() -> Optional[Path]:
    """Search for plan file in common locations."""
    for path in PLAN_SEARCH_PATHS:
        p = Path(path)
        if p.exists() and p.is_file():
            return p
    return None


def extract_scope(plan_text: str) -> List[str]:
    """
    Extract declared scope from plan text.
    
    Returns list of file paths/directories mentioned in plan.
    Only returns paths that exist in the repo.
    """
    scope = []

    # Look for explicit scope sections
    for pattern in SCOPE_PATTERNS:
        matches = re.finditer(pattern, plan_text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            content = match.group(1)
            # Extract file paths and directories
            items = re.findall(r"[`\*]?([^\s`,\*]+(?:\.py|\.ts|\.js|\.md|/))[`\*]?", content)
            scope.extend(items)

    # Look for file lists (paths in code blocks or lists)
    file_pattern = r"(?:^|\n)\s*[-*]\s+(?:`)?([^\s`]+(?:\.py|\.ts|\.js|\.md|\.sh|\.json)(?:`)?)"
    matches = re.finditer(file_pattern, plan_text, re.MULTILINE)
    for match in matches:
        scope.append(match.group(1).strip("`"))

    # Validate that files/dirs exist, remove false positives
    validated = []
    for item in scope:
        p = Path(item)
        if p.exists():
            validated.append(str(p))

    return list(set(validated))  # Deduplicate


def resolve_plan() -> Dict[str, any]:
    """
    Resolve plan metadata.
    
    Returns:
        {
            "plan_ok": bool,
            "plan_path": str | null,
            "declared_scope": [str, ...],
            "plan_text_preview": str | null,
            "has_scope_declaration": bool
        }
    """
    plan_file = find_plan_file()

    if not plan_file:
        return {
            "plan_ok": False,
            "plan_path": None,
            "declared_scope": [],
            "plan_text_preview": None,
            "has_scope_declaration": False,
        }

    try:
        plan_text = plan_file.read_text()
    except Exception as e:
        return {
            "plan_ok": False,
            "plan_path": str(plan_file),
            "error": f"Could not read plan: {str(e)}",
            "declared_scope": [],
            "plan_text_preview": None,
            "has_scope_declaration": False,
        }

    # Check if plan contains recognizable markers
    has_markers = any(
        re.search(marker, plan_text, re.MULTILINE | re.IGNORECASE)
        for marker in PLAN_MARKERS
    )

    # Extract scope
    scope = extract_scope(plan_text)
    has_scope = len(scope) > 0

    # Generate preview (first 500 chars)
    preview = plan_text[:500] + "..." if len(plan_text) > 500 else plan_text

    return {
        "plan_ok": True,
        "plan_path": str(plan_file),
        "declared_scope": scope,
        "plan_text_preview": preview,
        "has_scope_declaration": has_scope,
        "has_plan_markers": has_markers,
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If input is malformed, emit neutral response
        print(json.dumps({"plan_ok": False, "error": "Invalid JSON input"}))
        sys.exit(0)

    resolution = resolve_plan()

    # Emit plan metadata to stdout
    print(json.dumps(resolution))

    # Always exit 0: this hook never blocks
    sys.exit(0)


if __name__ == "__main__":
    main()
