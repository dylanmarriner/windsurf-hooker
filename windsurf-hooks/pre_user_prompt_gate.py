#!/usr/bin/env python3
"""
pre_user_prompt_gate: Intent detection and plan reference extraction.

Phase 1 of the hook pipeline (ATLAS-GATE model):
- Detect mutation intent (code write)
- Extract plan references (hash or alias) from prompt
- Emit markers to conversation context
- Never block on plan correctness (ATLAS-GATE validates)

Invariant:
- Never validate BLAKE3 hashes (ATLAS-GATE does)
- Never compute BLAKE3 (Windsurf is pass-through only)
- Annotation only: emit intent/plan markers
- No blocking on missing plans (ATLAS enforcement is upstream)
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()


def detect_mutation_intent(prompt: str) -> bool:
    """
    Detect if user intends to mutate code.
    
    High-confidence mutation keywords:
    - implement, write, generate, edit, refactor, add, create, patch, modify
    """
    mutation_keywords = [
        r"\b(implement|write|generate|edit|refactor|add|create|patch|modify|change|update)\b",
    ]
    
    for pattern in mutation_keywords:
        if re.search(pattern, prompt, re.IGNORECASE):
            return True
    
    return False


def extract_plan_reference(prompt: str) -> Optional[str]:
    """
    Extract plan reference from prompt.
    
    Supports:
    - Full BLAKE3 hash: plan=abc123... (64 hex chars)
    - Friendly alias: plan: auth-refactor, plan=auth-refactor
    - Path hint: /docs/plans/auth-refactor.md (extracted as alias)
    
    Returns: hash/alias string, or None if not found
    Note: We never validate the hash; ATLAS-GATE does.
    """
    # Pattern 1: plan=<hash or alias>
    match = re.search(r"plan\s*=\s*([a-zA-Z0-9_\-\.]+)", prompt)
    if match:
        return match.group(1)
    
    # Pattern 2: plan: <hash or alias>
    match = re.search(r"plan\s*:\s*([a-zA-Z0-9_\-\.]+)", prompt)
    if match:
        return match.group(1)
    
    # Pattern 3: /docs/plans/<name>.md (extract <name>)
    match = re.search(r"/docs/plans/([a-zA-Z0-9_\-]+)\.md", prompt)
    if match:
        return match.group(1)
    
    # Pattern 4: .kaiza/plans/<name> or similar
    match = re.search(r"\.kaiza/plans/([a-zA-Z0-9_\-]+)", prompt)
    if match:
        return match.group(1)
    
    return None


def main():
    """Extract intent and plan reference from prompt."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(1)

    prompt = (payload.get("tool_info", {}) or {}).get("prompt", "") or ""

    # Detect mutation intent
    is_mutation = detect_mutation_intent(prompt)
    
    # Extract plan reference (if any)
    plan_ref = extract_plan_reference(prompt)

    # Emit markers for conversation context
    output = {}
    
    if is_mutation:
        output["mutation_requested"] = True
        if plan_ref:
            output["plan_reference"] = plan_ref
            output["conversation_context_marker"] = f"ATLAS_PLAN_REQUESTED={plan_ref}"
        else:
            output["plan_reference"] = None
            output["conversation_context_marker"] = "ATLAS_MUTATION_NO_PLAN"
    else:
        output["mutation_requested"] = False

    # Emit markers to context (Windsurf appends to conversation_context)
    # This helps downstream hooks (pre_mcp_tool_use checks for these markers)
    print(json.dumps(output))
    sys.exit(0)


if __name__ == "__main__":
    main()
