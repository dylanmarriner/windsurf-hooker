#!/usr/bin/env python3
"""
post_session_entropy_check: Detect degradation in session coherence.

Experimental hook to detect:
- Repeated failed attempts (circular retries)
- Degenerate edits (changes that undo previous changes)
- Conversation drift (intent changing repeatedly)
- Resource exhaustion patterns

Actions:
- WARN: Log degradation signal
- ESCALATE: Force PLAN mode or require explicit override
- ALERT: If entropy exceeds threshold

Invariant:
- Entropy increases with time; detect reversals
- Circular patterns indicate lost context
- Escalation is advisory, not blocking
"""

import json
import sys
from typing import Dict, List
from collections import defaultdict
import re

# Threshold for circular retry detection
CIRCULAR_RETRY_THRESHOLD = 3
ENTROPY_THRESHOLD = 0.7  # % of previous edits being undone


def detect_circular_edits(conversation: str) -> Dict[str, any]:
    """
    Detect patterns where edits undo previous changes.
    
    Looks for:
    - Same file edited >N times in short sequence
    - old_string in one edit == new_string in previous
    - Similar error patterns repeating
    """
    patterns = {
        "repeated_edits_same_file": defaultdict(int),
        "undo_patterns": 0,
        "repeated_errors": defaultdict(int),
    }

    # Parse conversation for edit patterns
    # Look for file edit sequences
    file_edits = re.findall(r"file:\s*([^\s]+)", conversation, re.IGNORECASE)
    for file in file_edits:
        patterns["repeated_edits_same_file"][file] += 1

    # Look for error repetition
    errors = re.findall(r"(?:error|failed|blocked):\s*([^\n]+)", conversation, re.IGNORECASE)
    for error in errors:
        # Normalize error message
        normalized = re.sub(r"[0-9]+", "N", error)[:50]
        patterns["repeated_errors"][normalized] += 1

    # Count undo patterns (heuristic)
    undo_count = len(re.findall(r"(?:undo|revert|rollback|replace with original)", conversation, re.IGNORECASE))
    patterns["undo_patterns"] = undo_count

    return patterns


def detect_conversation_drift(conversation_turns: List[str]) -> Dict[str, any]:
    """
    Detect if user intent is drifting or changing.
    
    Indicators:
    - Intent keywords changing between turns
    - Mode flags changing
    - Scope expanding/contracting unexpectedly
    """
    intents = []
    modes = []

    for turn in conversation_turns:
        # Extract intent keywords
        intent_keywords = re.findall(
            r"\b(implement|fix|audit|review|explore|explain|test|deploy)\b",
            turn,
            re.IGNORECASE,
        )
        intents.append(intent_keywords)

        # Extract mode flags
        mode_flags = re.findall(r"\[MODE:([A-Z_]+)\]", turn)
        modes.extend(mode_flags)

    # Check for intent instability
    intent_changes = 0
    for i in range(1, len(intents)):
        if intents[i] and intents[i-1]:
            if intents[i][0].lower() != intents[i-1][0].lower():
                intent_changes += 1

    # Check for mode thrashing
    mode_changes = len(set(modes))

    return {
        "intent_changes": intent_changes,
        "unique_modes": mode_changes,
        "is_drifting": intent_changes > 2 or mode_changes > 2,
    }


def analyze_entropy(payload: Dict) -> Dict[str, any]:
    """Analyze session entropy and coherence."""
    context = payload.get("conversation_context", "") or ""
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])

    if not context:
        return {
            "entropy_level": "unknown",
            "alerts": [],
            "recommendations": [],
        }

    # Detect circular patterns
    circular = detect_circular_edits(context)

    # Check for problematic patterns
    alerts = []
    recommendations = []

    # Check for repeated edits to same file
    for file, count in circular["repeated_edits_same_file"].items():
        if count >= CIRCULAR_RETRY_THRESHOLD:
            alerts.append(
                f"File '{file}' edited {count} times in sequence "
                f"(possible circular retry pattern)"
            )
            recommendations.append(
                f"Consider: 'Use a PLAN to scope edits to {file}' or 'Break this task into steps'"
            )

    # Check for undo patterns
    if circular["undo_patterns"] >= 2:
        alerts.append(
            f"Multiple undo/revert patterns detected ({circular['undo_patterns']} times) "
            f"(possible lost context)"
        )
        recommendations.append("Consider: 'Start fresh with a clear PLAN'")

    # Check conversation drift
    turns = context.split("\n---\n")  # Heuristic turn boundary
    if len(turns) >= 3:
        drift = detect_conversation_drift(turns[-5:])  # Look at recent turns
        if drift["is_drifting"]:
            alerts.append(
                f"Conversation is drifting "
                f"(intent changes: {drift['intent_changes']}, mode changes: {drift['unique_modes']})"
            )
            recommendations.append("Consider: 'Refocus on original goal with explicit PLAN'")

    # Calculate entropy score
    entropy_score = min(1.0, (len(alerts) / 3))  # Normalize

    return {
        "entropy_level": "high" if entropy_score > ENTROPY_THRESHOLD else "normal",
        "entropy_score": round(entropy_score, 2),
        "alerts": alerts,
        "recommendations": recommendations,
        "metrics": {
            "circular_edits": dict(circular["repeated_edits_same_file"]),
            "undo_patterns": circular["undo_patterns"],
            "repeated_errors": dict(circular["repeated_errors"]),
        },
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print(json.dumps({"entropy_level": "unknown"}))
        sys.exit(0)

    analysis = analyze_entropy(payload)
    context = payload.get("conversation_context", "") or ""

    # Escalate if high entropy and not already in PLAN mode
    should_escalate = (
        analysis["entropy_level"] == "high" and "[MODE:PLAN]" not in context
    )

    if should_escalate:
        print("ESCALATION: High session entropy detected", file=sys.stderr)
        print("Recommendation: Enter PLAN mode to restore coherence", file=sys.stderr)
        for rec in analysis["recommendations"]:
            print(f"  > {rec}", file=sys.stderr)

    # Emit analysis for logging
    print(json.dumps(analysis))

    # Always exit 0: this is advisory, non-blocking
    sys.exit(0)


if __name__ == "__main__":
    main()
