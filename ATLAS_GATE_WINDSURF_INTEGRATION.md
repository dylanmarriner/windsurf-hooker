# ATLAS-GATE + Windsurf Integration (Updated)

**All existing hooks updated to work with ATLAS-GATE MCP-only sandbox model.**

---

## What Changed

All hooks remain in place but have been evolved to match the ATLAS-GATE architecture:

### Updated Hooks (In Place)

| Hook | Change | Purpose |
|------|--------|---------|
| `pre_user_prompt_gate.py` | Now extracts plan references (hash/alias) | Intent detection + plan annotation |
| `pre_mcp_tool_use_allowlist.py` | Added session state + plan hash enforcement | ATLAS tools only + plan presence |
| `pre_run_command_blocklist.py` | Changed to unconditional kill | Shell always disabled |
| `pre_write_code_policy.py` | Added docstring (no logic change) | Escape primitives + mocks + logic checks |

### Unchanged Hooks (Still Working)

All other 7-phase hooks remain unchanged:
- Phase 1: `pre_intent_classification.py`
- Phase 2: `pre_plan_resolution.py`
- Phase 3: `pre_write_diff_quality.py`, `pre_filesystem_write.py`
- Phase 5: `post_write_verify.py`, `post_write_semantic_diff.py`, `post_write_observability.py`
- Phase 6: `post_refusal_audit.py`
- Phase 7: `post_session_entropy_check.py`

---

## Architecture: Windsurf + ATLAS-GATE

```
User Intent
    ↓
Windsurf (MCP-only sandbox)
    ├─→ pre_user_prompt_gate: Extract plan reference (no validation)
    ├─→ pre_mcp_tool_use_allowlist: Enforce ATLAS tools + session + plan presence
    ├─→ pre_run_command_blocklist: BLOCK all shell (unconditional kill)
    ├─→ pre_write_code_policy: Check escapes, mocks, logic preservation
    └─→ pre_write_diff_quality, pre_filesystem_write: Code quality gates
    ↓
ATLAS-GATE (Authority)
    ├─→ Validate BLAKE3 hash
    ├─→ Reality Lock enforcement
    ├─→ Plan authority verification
    └─→ Audit log capture
    ↓
Result (Deterministic, Auditable)
```

**Key insight:** Windsurf enforces sandbox constraints; ATLAS-GATE enforces execution authority.

---

## Hook Responsibilities (Updated)

### pre_user_prompt_gate.py
**Purpose:** Extract intent and plan reference (informational, never blocks)

```python
def main():
    # Detect mutation intent
    is_mutation = detect_mutation_intent(prompt)
    
    # Extract plan reference (hash or alias)
    plan_ref = extract_plan_reference(prompt)
    
    # Emit markers to conversation context
    # Downstream hooks (pre_mcp_tool_use) check for these markers
    print(json.dumps({
        "mutation_requested": is_mutation,
        "plan_reference": plan_ref,
    }))
    # Always pass - this hook is informational
    sys.exit(0)
```

**Key:**
- Never validates BLAKE3 hashes
- Never blocks on missing plans
- Emits markers for downstream hooks
- Supports multiple reference formats (hash, alias, path)

### pre_mcp_tool_use_allowlist.py
**Purpose:** Enforce ATLAS tools + session state + plan hash presence

```python
def main():
    # Rule 1: Only ATLAS-GATE tools
    if tool_name not in allowed_tools:
        BLOCK("Only ATLAS-GATE tools permitted")
    
    # Rule 2: begin_session must be first
    if tool_name != "mcp_atlas-gate-mcp_begin_session":
        if "ATLAS_SESSION_OK" not in conversation_context:
            BLOCK("Must call begin_session first")
    
    # Rule 3: read_prompt before writes
    if tool_name == "mcp_atlas-gate-mcp_write_file":
        if "ATLAS_PROMPT_UNLOCKED" not in conversation_context:
            BLOCK("Must call read_prompt before write_file")
        
        # Rule 4: Plan hash REQUIRED (never validated, only presence)
        plan = tool.get("plan", "").strip()
        if not plan:
            BLOCK("write_file requires plan hash (BLAKE3)")
    
    sys.exit(0)  # All checks passed
```

**Key:**
- Enforces presence, not correctness
- Plan hash is MANDATORY for writes
- Session state is enforced via markers
- This is the primary gate

### pre_run_command_blocklist.py
**Purpose:** Unconditional kill switch for shell execution

```python
def main():
    # No heuristics, no fallbacks, no "safe" commands
    BLOCK("Direct shell execution disabled. Use ATLAS-GATE tools.")
```

**Key:**
- Always blocks - no configuration
- This is a sandbox invariant
- ATLAS tools are the only authority

### pre_write_code_policy.py
**Purpose:** Defense-in-depth code quality (escapes, mocks, logic preservation)

```python
def main():
    # Check prohibited patterns (includes escape primitives)
    for pattern in policy_patterns:
        if pattern found in code:
            BLOCK("Prohibited pattern detected")
    
    # Check mocks in REPAIR mode
    # Check logic preservation
    # DOES NOT check plan correctness
```

**Key:**
- Works alongside escape detection from prohibited patterns
- ATLAS-GATE is the authoritative source for write validation
- This hook is defense-in-depth, not primary authority

---

## Policy Configuration

```json
{
  "profile": "atlas_windsurf_exec_mutation",
  "mcp_tool_allowlist": [
    "mcp_atlas-gate-mcp_begin_session",
    "mcp_atlas-gate-mcp_read_prompt",
    "mcp_atlas-gate-mcp_list_plans",
    "mcp_atlas-gate-mcp_read_file",
    "mcp_atlas-gate-mcp_write_file",
    "mcp_atlas-gate-mcp_read_audit_log",
    "mcp_atlas-gate-mcp_verify_workspace_integrity",
    "mcp_atlas-gate-mcp_replay_execution",
    "mcp_atlas-gate-mcp_generate_attestation_bundle",
    "mcp_atlas-gate-mcp_verify_attestation_bundle",
    "mcp_atlas-gate-mcp_export_attestation_bundle"
  ],
  "block_commands_regex": [".*"],
  "filesystem": {
    "direct_read": false,
    "direct_write": false,
    "direct_exec": false
  },
  "prohibited_patterns": {
    "placeholders": ["TODO", "FIXME", "XXX", "pass", "...", "unimplemented", "stub"],
    "mock_artifacts": ["mock data", "fake data", "demo data", "hardcoded test"],
    "assumptions_and_hacks": ["assume", "temporary", "for now", "hack", "workaround"],
    "escape_attempts": [
      "os\\.system",
      "subprocess",
      "exec\\(",
      "eval\\(",
      "\\bopen\\("
    ]
  }
}
```

---

## Design Rules (Non-Negotiable)

### Rule 1: Windsurf Never Computes BLAKE3
```python
# ❌ WRONG
import hashlib
blake3_hash = hashlib.blake3(plan_content).hexdigest()

# ✅ CORRECT
plan_hash = tool.get("plan")  # Pass through unchanged
```

Why: Different normalizations = different hash. You risk blocking valid plans.

### Rule 2: Windsurf Only Ensures Presence, Not Correctness
```python
# ✅ CORRECT
if not plan:
    BLOCK("write_file requires plan hash")

# ❌ WRONG
if len(plan) != 64:
    BLOCK("invalid hash length")  # ATLAS-GATE's job
```

Why: ATLAS-GATE validates against actual plan content.

### Rule 3: Session Must Initialize First
```
1. begin_session (mandatory first call)
2. read_prompt (unlock writes)
3. write_file (requires plan hash)
4. verify_workspace_integrity (optional but recommended)
```

Why: Ensures clean context and prevents state pollution.

### Rule 4: Shell Execution Unconditionally Blocked
```python
# Always block - no heuristics, no configuration
BLOCK("Direct shell execution disabled. Use ATLAS-GATE tools.")
```

Why: Sandbox invariant.

---

## Plan Hash Model (BLAKE3)

### What is a Plan Hash?
A BLAKE3 hash (64 hex characters) that uniquely identifies a plan's content.

### Example
```
plan_hash = "3f2a1b9c8e7d6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f"
```

### How Windsurf Handles Hashes
1. **Accept** plan reference from user prompt
2. **Extract** (hash, alias, or path hint)
3. **Pass through** to ATLAS-GATE unchanged
4. **Never validate** or compute

### How ATLAS-GATE Handles Hashes
1. **Validate** hash against plan content
2. **Enforce** Reality Lock
3. **Log** the hash in audit trail
4. **Replay** using the hash as deterministic handle

---

## Integration with Existing 7-Phase Hook System

The ATLAS-GATE model **coexists** with the existing 7-phase system:

- **Phase 1:** `pre_intent_classification.py` (unchanged), `pre_user_prompt_gate.py` (updated)
- **Phase 2:** `pre_plan_resolution.py` (unchanged)
- **Phase 3:** `pre_write_diff_quality.py` (unchanged), `pre_write_code_policy.py` (updated), `pre_filesystem_write.py` (unchanged)
- **Phase 4:** `pre_mcp_tool_use_allowlist.py` (updated), `pre_run_command_blocklist.py` (updated)
- **Phase 5:** Post-write hooks (unchanged)
- **Phase 6-7:** Audit and meta hooks (unchanged)

All deployment scripts continue to work unchanged:
- `deploy.sh` — Copies all `.py` files to `/usr/local/share/windsurf-hooks/`
- `validate-implementation.sh` — Validates hook syntax and policy.json

---

## Migration Path

### If You Currently Have Old Windsurf Setup
1. Update `policy.json` with ATLAS-GATE tool list
2. Run `deploy.sh` (copies updated hooks)
3. Existing tests continue to pass

### If You're Starting Fresh
1. Copy updated repo
2. Run `deploy.sh`
3. Use ATLAS-GATE tools exclusively

---

## Verification

All hooks can be tested in isolation:

```bash
# Test pre_user_prompt_gate
echo '{"tool_info": {"prompt": "implement plan=abc123"}}' | \
  python3 windsurf-hooks/pre_user_prompt_gate.py

# Test pre_mcp_tool_use_allowlist
echo '{
  "tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file", "plan": "abc123"},
  "conversation_context": "ATLAS_SESSION_OK ATLAS_PROMPT_UNLOCKED"
}' | python3 windsurf-hooks/pre_mcp_tool_use_allowlist.py

# Test pre_run_command_blocklist (should always block)
echo '{"tool_info": {"command": "ls"}}' | \
  python3 windsurf-hooks/pre_run_command_blocklist.py
```

---

## See Also

- [ATLAS_GATE.md](ATLAS_GATE.md) — Complete ATLAS-GATE documentation
- [HOOK_ARCHITECTURE.md](HOOK_ARCHITECTURE.md) — 7-phase hook system
- [policy.json](windsurf/policy/policy.json) — Runtime configuration
- [deploy.sh](deploy.sh) — Deployment script
- [validate-implementation.sh](validate-implementation.sh) — Validation script
