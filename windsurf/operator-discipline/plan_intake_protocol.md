# Plan Intake Protocol

**Before Windsurf touches a plan, validate it.**

This is the operator's responsibility. Implement in your planning/orchestration layer.

## Validation Checklist

### 1. Plan Schema Validation
```
✓ Plan is valid JSON or YAML
✓ Root object has "steps" key (array)
✓ Each step has:
    - tool: string (in whitelist)
    - arguments: object
    - intent: string (non-empty)
    - optional: scope, timeout, continue_on_error
✓ No unknown keys allowed
```

### 2. Plan Hash Confirmation
```
✓ Compute SHA256(plan content)
✓ Compare against expected hash (if provided)
✓ Persist hash in session context
```

### 3. Plan Approval Confirmation
```
✓ Plan has been reviewed and approved
✓ (Optional) Get explicit go/no-go signal
✓ (Optional) Signature verification if required
```

### 4. Workspace Scope Matching
```
✓ Plan scope (if declared) matches workspace root
✓ All paths in plan steps are within workspace
✓ No protected paths in write operations
```

### 5. Tool Whitelist Confirmation
```
✓ Each tool in plan is in /etc/windsurf/policy/tool_whitelist.conf
✓ No disallowed tools
✓ No reasoning or planning tools
```

### 6. Step Validation
```
For each step:
  ✓ Tool is in whitelist
  ✓ Arguments are fully specified (no inferred values)
  ✓ Intent is clear and non-empty
  ✓ No ambiguity in step definition
  ✓ Single tool per step (no merged operations)
```

### 7. Determinism Check
```
✓ Plan is deterministic (no if/else branches unless explicit)
✓ All randomness and variation is represented in plan
✓ Execution order is fixed
```

## Rejection Criteria

Reject plan if:
- Schema invalid
- Hash mismatch
- Contains disallowed tools
- Ambiguous step definitions
- Paths outside workspace
- Writes to protected paths
- Missing intents
- Non-deterministic structure

## Approval Signal

Only when ALL checks pass:
```json
{
  "status": "approved",
  "plan_hash": "...",
  "validated_at": "...",
  "validator": "...",
  "scope": "..."
}
```

Pass this to Windsurf executor.

## No Plan Modifications

Once approved and passed to Windsurf:
- Plan is immutable
- Windsurf will verify hash at each step
- Any modification is detected and rejected
- Audit trail is preserved

This ensures execution determinism.
