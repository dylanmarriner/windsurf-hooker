# Failure Structure & Strategy

**Windsurf must fail fast, loud, and structured.**

## Failure Strategy

```
FAIL FAST    → Do not attempt recovery
FAIL LOUD    → Return full error details
FAIL STRUCTURED → Use deterministic error format
```

## Standard Failure Response

All failures return this structure:

```json
{
  "status": "failed",
  "step_id": "<index or name>",
  "tool": "<tool_name>",
  "error": "<error message>",
  "error_type": "<TransientError|PermanentError|ValidationError>",
  "plan_hash": "<hash of executed plan>",
  "session_id": "<session_id>",
  "timestamp": "ISO8601",
  
  "context": {
    "expected_arguments": {...},
    "actual_arguments": {...},
    "step_definition": {...}
  },
  
  "audit_trail": [
    {
      "step": 0,
      "tool": "begin_session",
      "status": "success",
      "timestamp": "..."
    },
    ...
  ]
}
```

## Failure Categories

### 1. Validation Error
```json
{
  "error_type": "ValidationError",
  "reason": "Arguments do not match tool schema"
}
```

**Examples:**
- Missing required field
- Type mismatch (expected string, got int)
- Value out of allowed range
- Path validation failed

**Action:** Return immediately. Do not proceed.

### 2. Permanent Error
```json
{
  "error_type": "PermanentError",
  "reason": "Operation cannot succeed (file not found, permission denied, etc.)"
}
```

**Examples:**
- File does not exist
- Permission denied
- Resource exhausted (disk full)
- Invalid operation

**Action:** Return immediately. Do not retry.

### 3. Transient Error
```json
{
  "error_type": "TransientError",
  "reason": "Temporary failure (network timeout, busy, etc.)"
}
```

**Examples:**
- Network timeout
- Service temporarily unavailable
- Lock contention
- Temporary resource shortage

**Action:** Do NOT retry. Return to caller. Antigravity decides retry policy.

### 4. Boundary Violation
```json
{
  "error_type": "BoundaryViolation",
  "reason": "Attempted to violate separation invariant"
}
```

**Examples:**
- Attempted tool not in whitelist
- Attempted write to protected path
- Plan hash mismatch
- Session state violation

**Action:** Return immediately with full audit trail. Alert operator.

## No Partial Success

Windsurf must NOT:

```python
# REJECTED
steps = [s1, s2, s3]
results = []
for step in steps:
  try:
    result = execute_step(step)
    results.append(success)
  except:
    results.append(failure)
    # Continue to next step!

return {"step_results": results}  # WRONG
```

**Correct:**

```python
# RIGHT
for step in steps:
  try:
    result = execute_step(step)
  except Exception as e:
    return {
      "status": "failed",
      "step": step.id,
      "error": str(e),
      "audit_trail": [...]
    }
```

Stop immediately on first failure.

Exception: If plan explicitly says `continue_on_error: true` for a step, then continue. But this must be declared in the plan.

## Deterministic Error Messages

Error messages must be:

- **Factual** (no speculation)
- **Specific** (include actual vs expected)
- **Reproducible** (same error → same message)
- **Traceable** (reference step ID, tool name)

Example:

```json
{
  "error": "write_file: path validation failed",
  "details": {
    "path": "/etc/passwd",
    "reason": "Protected path",
    "step_id": 3
  }
}
```

## Audit Trail Preservation

**Never discard audit data.**

Even on failure, preserve:

```json
{
  "audit_trail": [
    {
      "step_id": 0,
      "tool": "begin_session",
      "status": "success",
      "response": {...}
    },
    {
      "step_id": 1,
      "tool": "read_file",
      "status": "success",
      "arguments": {...},
      "response": {...}
    },
    {
      "step_id": 2,
      "tool": "write_file",
      "status": "failed",
      "arguments": {...},
      "error": "...",
      "plan_hash": "..."
    }
  ]
}
```

This enables:
- Root cause analysis
- Replay for recovery
- Compliance audit
- Debugging

## No Automatic Recovery

Windsurf CANNOT:

- Retry on failure
- Skip failed step and continue
- Attempt alternative tool
- Repair arguments and retry
- Backtrack and redo earlier step

**Only Antigravity can decide recovery.**

## Escalation Example

Failure at step 3:

```
Windsurf: FAILED (step 3)
  ↓
Return full context to Antigravity
  ↓
Antigravity options:
  - Retry with same plan
  - Retry with modified plan
  - Skip this step (requires new plan)
  - Abort entire execution
  - Rollback previous steps
```

Windsurf waits for direction.
