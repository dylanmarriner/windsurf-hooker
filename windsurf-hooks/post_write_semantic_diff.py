#!/usr/bin/env python3
"""
post_write_semantic_diff: Verify that code matches intent.

Semantic trust, not syntax:
- Did implementation reflect plan?
- Did function names match description?
- Were required files actually modified?
- Was scope respected?

Invariant:
- Check AFTER code exists (post-write)
- Failure → alert, not block (semantic mismatches are warnings)
- Use plan context if available
- Compare intent language against actual changes
"""

import json
import sys
import re
from typing import Dict, List, Optional

# Keywords that suggest certain semantic expectations
SEMANTIC_KEYWORDS = {
    "function": [r"\bdef\s+\w+|function\s+\w+"],
    "class": [r"\bclass\s+\w+"],
    "test": [r"def test_|function test_|\.test\.|spec\."],
    "config": [r"(config|Config|CONFIG)", r"\{\s*[\"']?\w+[\"']?:\s*"],
    "documentation": [r"#\s+", r"^\s*\*\*", r'"""', "'''"],
}


def extract_identifiers(code: str) -> List[str]:
    """Extract defined functions, classes, variables from code."""
    identifiers = []

    # Functions
    for match in re.finditer(r"(?:def|function)\s+(\w+)", code):
        identifiers.append(match.group(1))

    # Classes
    for match in re.finditer(r"class\s+(\w+)", code):
        identifiers.append(match.group(1))

    # Variable assignments (at module level)
    for match in re.finditer(r"^(\w+)\s*=", code, re.MULTILINE):
        identifiers.append(match.group(1))

    return list(set(identifiers))


def extract_intent_keywords(prompt: str) -> List[str]:
    """Extract keywords that describe what should be implemented."""
    keywords = []

    # Look for function/class names mentioned in prompt
    for match in re.finditer(r"(?:create|implement|add|define|build)\s+(?:a\s+)?([a-zA-Z_]\w+)", prompt, re.IGNORECASE):
        keywords.append(match.group(1))

    # Look for quoted names
    for match in re.finditer(r'[`"\']([a-zA-Z_]\w+)[`"\']', prompt):
        keywords.append(match.group(1))

    return keywords


def semantic_check(
    prompt: str, edits: List[Dict], plan_scope: Optional[List[str]] = None
) -> Dict[str, any]:
    """
    Perform semantic verification.
    
    Returns:
        {
            "semantic_match": bool,
            "warnings": [str],
            "intent_coverage": {
                "mentioned": [...],
                "implemented": [...],
                "missing": [...]
            },
            "scope_compliance": bool,
            "scope_violations": [str]
        }
    """
    intent_keywords = extract_intent_keywords(prompt)
    all_identifiers = set()
    all_files = []
    scope_violations = []

    for edit in edits:
        new_code = edit.get("new_string", "") or ""
        path = edit.get("path", "")

        identifiers = extract_identifiers(new_code)
        all_identifiers.update(identifiers)
        all_files.append(path)

    # Check intent coverage
    implemented = [kw for kw in intent_keywords if any(
        kw.lower() in str(ident).lower() for ident in all_identifiers
    )]
    missing = [kw for kw in intent_keywords if kw not in implemented]

    # Check scope compliance if plan exists
    semantic_match = True
    warnings = []

    if plan_scope:
        for file in all_files:
            if not any(
                file.startswith(scope) or scope in file for scope in plan_scope
            ):
                scope_violations.append(
                    f"Edited file outside declared scope: {file}"
                )
                semantic_match = False

    # Warn about missing intent keywords
    if missing:
        warnings.append(
            f"Intent keywords not found in implementation: {', '.join(missing)}"
        )

    # Warn about multiple files if intent suggests single file
    if len(all_files) > 3 and "single file" in prompt.lower():
        warnings.append(
            f"Intent suggests single-file change, but {len(all_files)} files edited"
        )

    return {
        "semantic_match": semantic_match,
        "warnings": warnings,
        "intent_coverage": {
            "mentioned": intent_keywords,
            "implemented": list(all_identifiers),
            "missing_from_intent": missing,
        },
        "scope_compliance": len(scope_violations) == 0,
        "scope_violations": scope_violations,
        "files_modified": all_files,
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"semantic_match": True, "warnings": []}))
        sys.exit(0)

    prompt = (payload.get("tool_info", {}) or {}).get("prompt", "") or ""
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    context = payload.get("conversation_context", "") or ""

    # Extract plan scope if available from context
    plan_scope = None
    plan_match = re.search(r"PLAN_SCOPE:\s*\[(.*?)\]", context)
    if plan_match:
        plan_scope = [s.strip() for s in plan_match.group(1).split(",")]

    analysis = semantic_check(prompt, edits, plan_scope)

    # In STRICT mode, fail on scope violations
    in_strict_mode = "[MODE:STRICT]" in context
    if in_strict_mode and not analysis["scope_compliance"]:
        print("BLOCKED: semantic check failed - scope violation in STRICT mode", file=sys.stderr)
        for violation in analysis["scope_violations"]:
            print(f"  - {violation}", file=sys.stderr)
        sys.exit(2)

    # Otherwise, emit analysis for logging
    print(json.dumps(analysis))

    sys.exit(0)


if __name__ == "__main__":
    main()
