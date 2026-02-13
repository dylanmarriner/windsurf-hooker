#!/usr/bin/env python3
"""
Hook: pre_no_reasoning_in_executor

Windsurf is not allowed to reason. Scan tool arguments and payloads for reasoning artifacts.

Forbidden patterns:
  - "because", "should", "maybe", "could", "might"
  - "explanation", "reasoning", "strategy", "approach"
  - "I think", "I believe", "in my opinion"
  - Any narrative or justification text

This enforces the separation invariant:
  Antigravity decides.
  Windsurf executes.
  ATLAS enforces.

Windsurf must ONLY execute, never reason.
"""

import sys
import json
import re
from datetime import datetime

FORBIDDEN_PATTERNS = [
    r"\bbecause\b",
    r"\bshould\b",
    r"\bmaybe\b",
    r"\bcould\b",
    r"\bmight\b",
    r"\bprobably\b",
    r"\blikely\b",
    r"\bexplanation\b",
    r"\breasoning\b",
    r"\bstrategy\b",
    r"\bapproach\b",
    r"\bconsider\b",
    r"\bsuggest\b",
    r"\brecommend\b",
    r"best practice",
    r"for this reason",
    r"in my opinion",
    r"i think",
    r"i believe",
    r"think that",
    r"believe that",
    r"allows us to",
    r"enables us to"
]

# Compile patterns (case-insensitive)
COMPILED_PATTERNS = [re.compile(p, re.IGNORECASE) for p in FORBIDDEN_PATTERNS]

def scan_for_reasoning(text):
    """
    Scan text for reasoning artifacts.
    Returns: (found_reasoning, matched_patterns)
    """
    if not isinstance(text, str):
        return False, []
    
    matched = []
    for pattern in COMPILED_PATTERNS:
        if pattern.search(text):
            matched.append(pattern.pattern)
    
    return len(matched) > 0, matched

def scan_arguments(arguments):
    """
    Scan tool arguments dict for reasoning.
    Returns: (found_reasoning, evidence_list)
    """
    evidence = []
    
    if isinstance(arguments, dict):
        for key, value in arguments.items():
            if isinstance(value, str):
                found, patterns = scan_for_reasoning(value)
                if found:
                    evidence.append({"field": key, "matched_patterns": patterns})
    elif isinstance(arguments, str):
        found, patterns = scan_for_reasoning(arguments)
        if found:
            evidence.append({"field": "argument", "matched_patterns": patterns})
    
    return len(evidence) > 0, evidence

def audit_log(message):
    """Log to audit trail"""
    try:
        with open("/tmp/windsurf_reasoning_audit.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except:
        pass

def main():
    """
    Hook invocation.
    Receives: tool_name, arguments
    """
    
    try:
        input_data = json.loads(sys.stdin.read()) if sys.stdin.isatty() == False else {}
    except:
        input_data = {}
    
    tool_name = input_data.get("tool_name", "unknown")
    arguments = input_data.get("arguments", {})
    
    # Scan arguments for reasoning
    found_reasoning, evidence = scan_arguments(arguments)
    
    if found_reasoning:
        audit_log(
            f"REASONING DETECTED in {tool_name}: {json.dumps(evidence)}. REJECTING."
        )
        print(json.dumps({
            "status": "rejected",
            "reason": "Tool call contains reasoning or narrative text. Windsurf must only execute, not reason.",
            "tool": tool_name,
            "evidence": evidence
        }))
        sys.exit(1)
    
    # No reasoning detected
    print(json.dumps({
        "status": "allowed",
        "tool": tool_name
    }))
    sys.exit(0)

if __name__ == "__main__":
    main()
