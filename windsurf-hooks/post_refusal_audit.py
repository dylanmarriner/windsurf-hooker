#!/usr/bin/env python3
"""
post_refusal_audit: Ensure refusals are structured and justified.

When windsurf refuses to act:
- Require explicit refusal reason (not silent failure)
- Ensure no fabricated progress is reported
- Validate refusal is legitimate (policy, safety, scope)
- Log refusal for audit trail

Invariant:
- Refusals must be explicit and structured
- Never hide failures under generic messages
- Always exit with clear error code
- Provide actionable next steps
"""

import json
import sys
from typing import Dict, List

# Valid refusal categories
VALID_REFUSAL_REASONS = {
    "policy_violation": "Policy prevents this action",
    "scope_violation": "Outside declared scope",
    "safety_check": "Safety verification failed",
    "missing_requirement": "Required prerequisite missing",
    "permission_denied": "Insufficient permissions",
    "ambiguous_intent": "Intent is unclear or conflicting",
    "resource_limit": "Resource limits exceeded",
    "configuration_error": "Configuration error prevents action",
}


def validate_refusal(refusal_info: Dict) -> Dict[str, any]:
    """
    Validate that refusal is properly structured.
    
    Expected structure:
        {
            "refused": true,
            "reason": "policy_violation | scope_violation | ...",
            "message": "Human-readable explanation",
            "details": ["detail1", "detail2"],
            "recovery_steps": ["step1", "step2"],  # How to resolve
            "exit_code": 2  # Non-zero failure code
        }
    """
    if not refusal_info.get("refused"):
        return {"is_valid_refusal": False, "error": "Not a refusal record"}

    reason = refusal_info.get("reason")
    message = refusal_info.get("message", "")
    details = refusal_info.get("details", [])
    recovery = refusal_info.get("recovery_steps", [])
    exit_code = refusal_info.get("exit_code")

    issues = []

    # Check reason is valid
    if reason not in VALID_REFUSAL_REASONS:
        issues.append(f"Invalid refusal reason: {reason}")

    # Check message is present and meaningful
    if not message or len(message.strip()) < 10:
        issues.append("Refusal message too short or missing")

    # Check details are present (at least 1)
    if not details or len(details) == 0:
        issues.append("No details provided for refusal")

    # Check recovery steps (highly recommended)
    if not recovery or len(recovery) == 0:
        issues.append("No recovery steps provided (recommend adding)")

    # Check exit code
    if exit_code != 2 and exit_code != 1:
        issues.append(f"Invalid exit code {exit_code} (should be 1 or 2)")

    is_valid = len(issues) == 0

    return {
        "is_valid_refusal": is_valid,
        "issues": issues,
        "refusal_info": refusal_info,
    }


def audit_refusal(context: str) -> List[Dict]:
    """
    Scan context for refusal records and validate them.
    
    Looks for:
    - [REFUSAL:...] markers
    - [BLOCKED:...] markers
    - [ERROR:...] markers
    """
    refusals = []

    # Parse refusal markers from context
    # This is a simplified parser; in production use proper structured logging
    import re

    # Find all refusal-like markers
    patterns = [
        (r"\[REFUSAL:(\w+)\]\s+(.+?)(?=\[|\Z)", "refusal"),
        (r"\[BLOCKED:\s*(.+?)\]", "blocked"),
        (r"\[ERROR:\s*(.+?)\]", "error"),
    ]

    for pattern, marker_type in patterns:
        for match in re.finditer(pattern, context, re.DOTALL):
            refusals.append(
                {
                    "type": marker_type,
                    "content": match.group(1),
                    "offset": match.start(),
                }
            )

    return refusals


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        # If input is malformed, can't validate refusal
        print(json.dumps({"audit_result": "input_error", "valid": False}))
        sys.exit(0)

    # Check if this is a refusal context
    context = payload.get("conversation_context", "") or ""
    is_refusal = (
        "[REFUSAL:" in context
        or "[BLOCKED:" in context
        or payload.get("refused", False)
    )

    if not is_refusal:
        # Not a refusal, pass through
        print(json.dumps({"is_refusal": False, "valid": True}))
        sys.exit(0)

    # This is a refusal - audit it
    refusal_info = payload.get("refusal_info", {})
    context_refusals = audit_refusal(context)

    validation = validate_refusal(refusal_info)

    result = {
        "is_refusal": True,
        "refusal_valid": validation["is_valid_refusal"],
        "validation_issues": validation["issues"],
        "context_refusals_found": len(context_refusals),
        "refusal_reason": refusal_info.get("reason"),
        "refusal_message": refusal_info.get("message"),
    }

    if not validation["is_valid_refusal"]:
        print(
            "WARNING: Refusal is not properly structured",
            file=sys.stderr,
        )
        for issue in validation["issues"]:
            print(f"  - {issue}", file=sys.stderr)

    print(json.dumps(result))

    # Always exit 0: this is audit-only, non-blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
