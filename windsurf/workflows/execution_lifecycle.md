# Execution Lifecycle Workflow

The canonical workflow Windsurf must follow. No branching except as explicitly defined in the plan.

## Phases

### 1. BEGIN_SESSION
- Invoke `begin_session`
- Transition session state to ACTIVE
- Capture session ID
- Initialize plan hash
- Verify workspace exists

### 2. FOR EACH PLAN STEP
```
loop:
  - Validate step schema
  - Verify plan hash unchanged
  - Invoke tool with exact arguments
  - Capture response
  - Append to audit trail
  - Verify response status
  - On failure: HALT (do not continue)
```

**No:**
- Retry on transient failure
- Repair arguments
- Substitute tools
- Reorder steps
- Merge steps
- Skip steps

**On step failure:**
- Preserve full context
- Return error to caller
- Do NOT attempt recovery
- Antigravity decides next action

### 3. VERIFY WORKSPACE
After all steps complete:
- Invoke `verify_workspace_integrity`
- Confirm no unexpected mutations
- Confirm all expected files exist
- Confirm permissions correct

### 4. OPTIONAL: GENERATE ATTESTATION
For production plans or high-risk operations:
- Invoke `generate_attestation_bundle`
- Capture immutable proof of execution
- Include plan hash, step list, responses
- Return bundle to caller

### 5. END_SESSION
- Invoke `end_session`
- Transition session state to CLOSED
- Flush audit trail
- Return results

## Failure Handling

```
FAIL FAST
FAIL LOUD
FAIL STRUCTURED
```

Return:
```json
{
  "status": "failed",
  "step_id": "...",
  "tool": "...",
  "error": "...",
  "plan_hash": "...",
  "audit_trail": [...]
}
```

**Never attempt partial success unless explicitly supported by plan.**

## Determinism

- No randomness in decision-making
- All branches explicit in plan
- Session ID deterministic from plan hash
- RPC IDs deterministic from session + step index
- No concurrent execution
- No speculation

## Audit Trail

At each step, capture and persist:
- plan_hash (verify immutability)
- step_index
- tool_name
- arguments (sanitized)
- response (full, including errors)
- timestamp (ISO8601)
- session_id

Never discard audit data.
