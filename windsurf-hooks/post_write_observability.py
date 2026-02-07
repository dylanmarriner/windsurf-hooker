#!/usr/bin/env python3
"""
post_write_observability: Enforce Definition of Done (Enterprise-grade).

Checks that code modifications include:
- Logs/debug output (for debugging)
- Metrics (for monitoring)
- Traces (for observability)

Invariant:
- Only blocks in SHIP mode
- In DEV/AUDIT modes, warns but allows
- Failure → alert on reduced observability
"""

import json
import sys
import re
from typing import Dict, List

# Patterns indicating observability instrumentation
LOG_PATTERNS = [
    r"\bprint\(",
    r"\blogger\.(debug|info|warn|error)",
    r"\bconsole\.(log|debug|warn|error)",
    r"\bsys\.stderr\.write",
    r"logging\.log",
    r"console\.(log|debug)",
]

METRIC_PATTERNS = [
    r"\bmetrics\.",
    r"\bincrement\(",
    r"\brecord\(",
    r"\bcounter\.",
    r"\bgauge\.",
    r"\bhistogram\.",
    r"\bobserve\(",
]

TRACE_PATTERNS = [
    r"\bspan\.",
    r"\btrace\.",
    r"\b@trace",
    r"\bwith_trace",
    r"context\.with_",
]

# Minimum thresholds for code size
MIN_LINES_FOR_LOGGING = 10  # Don't require logging for tiny changes
MIN_LINES_FOR_METRICS = 20  # Don't require metrics for tiny changes


def count_lines(text: str) -> int:
    """Count executable lines (excluding comments/blanks)."""
    return len(
        [
            l
            for l in text.splitlines()
            if l.strip() and not l.strip().startswith("#")
        ]
    )


def check_observability(edits: List[Dict]) -> Dict[str, any]:
    """Check that code includes observability instrumentation."""
    if not edits:
        return {
            "observability_ok": True,
            "warnings": [],
            "metrics": {},
        }

    warnings = []
    total_lines = 0
    has_logging = False
    has_metrics = False
    has_tracing = False
    large_changes = 0

    for edit in edits:
        new_code = edit.get("new_string", "") or ""
        path = edit.get("path", "")

        lines = count_lines(new_code)
        total_lines += lines

        # Check for large changes
        if lines > MIN_LINES_FOR_LOGGING:
            large_changes += 1

            # Check observability instrumentation
            if any(re.search(pattern, new_code, re.IGNORECASE) for pattern in LOG_PATTERNS):
                has_logging = True

            if any(re.search(pattern, new_code, re.IGNORECASE) for pattern in METRIC_PATTERNS):
                has_metrics = True

            if any(re.search(pattern, new_code, re.IGNORECASE) for pattern in TRACE_PATTERNS):
                has_tracing = True

    # Generate warnings based on what's missing
    if large_changes > 0 and total_lines > MIN_LINES_FOR_LOGGING:
        if not has_logging:
            warnings.append(
                f"No logging instrumentation in {large_changes} large change(s) "
                f"({total_lines} lines total)"
            )

    if large_changes > 0 and total_lines > MIN_LINES_FOR_METRICS:
        if not has_metrics:
            warnings.append(
                f"No metrics instrumentation in {large_changes} large change(s) "
                f"({total_lines} lines total)"
            )

    if large_changes > 0 and not has_tracing:
        warnings.append(
            f"No distributed tracing instrumentation in {large_changes} large change(s)"
        )

    observability_ok = has_logging or total_lines <= MIN_LINES_FOR_LOGGING

    return {
        "observability_ok": observability_ok,
        "warnings": warnings,
        "metrics": {
            "total_lines": total_lines,
            "large_changes": large_changes,
            "has_logging": has_logging,
            "has_metrics": has_metrics,
            "has_tracing": has_tracing,
        },
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"observability_ok": True, "warnings": []}))
        sys.exit(0)

    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    context = payload.get("conversation_context", "") or ""

    analysis = check_observability(edits)

    # Only block in SHIP mode
    in_ship_mode = "[MODE:SHIP]" in context or "[MODE:SHIP_OK]" in context
    if in_ship_mode and not analysis["observability_ok"]:
        print("BLOCKED: observability check failed in SHIP mode", file=sys.stderr)
        for warning in analysis["warnings"]:
            print(f"  - {warning}", file=sys.stderr)
        sys.exit(2)

    # Otherwise, emit analysis for context
    print(json.dumps(analysis))

    sys.exit(0)


if __name__ == "__main__":
    main()
