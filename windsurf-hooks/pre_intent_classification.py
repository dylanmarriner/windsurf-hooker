#!/usr/bin/env python3
"""
pre_intent_classification: Classify user intent with confidence scoring.

Separates WHAT (intent) from HOW (mode/approach).
Emits structured intent classification for downstream hooks.

Invariant:
- Intent must be monotonic: later hooks may narrow, never widen
- No blocking: this hook is purely informational
"""

import json
import sys
import re
from typing import Dict, Literal

# Intent patterns with confidence weights
INTENT_PATTERNS = {
    "code_write": [
        (r"\b(implement|write|generate|create|add|refactor|edit|patch|change|fix code)\b", 0.9),
        (r"(?:can you|please)\s+(implement|write|create)\b", 0.85),
        (r"modify.*file|update.*code", 0.8),
    ],
    "repair": [
        (r"\b(fix|debug|repair|resolve|troubleshoot|error|bug)\b", 0.85),
        (r"why.*fail|not.*work|broken", 0.8),
        (r"\[MODE:REPAIR", 0.95),
    ],
    "audit": [
        (r"\b(review|audit|check|verify|test|analyze)\b", 0.85),
        (r"\[MODE:AUDIT", 0.95),
        (r"(?:is this|does this)\s+\w+", 0.7),
    ],
    "explore": [
        (r"\b(explore|understand|explain|show|diagram|walk.*through|how.*work)\b", 0.85),
        (r"what.*architecture|find.*pattern|locate.*code", 0.8),
        (r"show me|describe|tell me about", 0.75),
    ],
}


def classify_intent(prompt: str) -> Dict[str, any]:
    """
    Classify intent with confidence scores.
    
    Returns:
        {
            "primary_intent": "code_write|repair|audit|explore",
            "confidence": 0.0-1.0,
            "matched_patterns": ["pattern1", ...],
            "is_high_confidence": bool
        }
    """
    if not prompt:
        return {
            "primary_intent": "explore",
            "confidence": 0.5,
            "matched_patterns": [],
            "is_high_confidence": False,
        }

    scores = {}
    matched = {}

    # Score each intent category
    for intent, patterns in INTENT_PATTERNS.items():
        max_score = 0
        matched_patterns = []

        for pattern, confidence in patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                max_score = max(max_score, confidence)
                matched_patterns.append(pattern)

        scores[intent] = max_score
        matched[intent] = matched_patterns

    # Determine primary intent
    primary = max(scores, key=scores.get)
    confidence = scores[primary]
    is_high_conf = confidence >= 0.80

    return {
        "primary_intent": primary,
        "confidence": round(confidence, 2),
        "matched_patterns": matched[primary],
        "is_high_confidence": is_high_conf,
        "all_scores": {k: round(v, 2) for k, v in scores.items()},
    }


def main():
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON input", file=sys.stderr)
        sys.exit(1)

    prompt = (payload.get("tool_info", {}) or {}).get("prompt", "") or ""
    classification = classify_intent(prompt)

    # Emit classification to stdout (as JSON)
    print(json.dumps(classification))

    # Always exit 0: this hook never blocks
    sys.exit(0)


if __name__ == "__main__":
    main()
