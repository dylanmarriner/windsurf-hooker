# Anti-Patterns: Windsurf Execution Violations

**These behaviors violate the separation invariant and must be blocked.**

Windsurf MUST NOT:

## 1. Improve / Polish Code
**FORBIDDEN:** Reading file → improving content → writing back

Example:
```python
# REJECTED
read_file("src/main.py")
→ improve formatting, add docstrings, refactor
→ write_file("src/main.py", improved_content)
```

**Why:** Violates execution-only constraint. Adding value requires decisions.

**Correct:** Plan should specify exact transformations:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "src/main.py",
    "content": "..."
  },
  "intent": "Update main.py with changes"
}
```

---

## 2. Fill In Missing Parameters
**FORBIDDEN:** Inferring parameter values not in plan

Example:
```python
# REJECTED
plan says: write_file(path="/tmp/file.txt", content="...")
windsurf infers: encoding="utf-8", mode="0644"
→ adds them automatically
```

**Why:** Decisions belong to Antigravity, not Windsurf.

**Correct:** Plan must specify ALL parameters:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "/tmp/file.txt",
    "content": "...",
    "encoding": "utf-8",
    "mode": "0644"
  }
}
```

---

## 3. Silent Retry on Transient Failure
**FORBIDDEN:** Automatically retrying failed steps

Example:
```python
# REJECTED
try:
  invoke_tool(...)
except TransientError:
  sleep(1)
  retry()  # WINDSURF CANNOT DO THIS
```

**Why:** Recovery decisions belong to Antigravity.

**Correct:** Fail fast and loud:
```python
try:
  invoke_tool(...)
except Exception as e:
  return {
    "status": "failed",
    "step": current_step,
    "error": str(e),
    "plan_hash": plan_hash
  }
```

Antigravity decides: retry, skip step, abort, etc.

---

## 4. Merge Multiple Steps
**FORBIDDEN:** Combining steps that should be separate

Example:
```python
# REJECTED
plan has: step1=read_file, step2=write_file
windsurf optimizes: read_and_write_in_one_call
```

**Why:** Plan defines the execution contract. Step merging breaks audit trail.

**Correct:** Execute steps exactly as defined, even if redundant.

---

## 5. Inject Commentary into Writes
**FORBIDDEN:** Adding explanations to write_file content

Example:
```python
# REJECTED
plan says: write_file(path="index.js", content="...")
windsurf adds: "// Note: Updated to add feature X"
```

**Why:** Content mutations require decision-making. Only execute what's in the plan.

**Correct:** If commentary is needed, include it in the plan:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "index.js",
    "content": "// Note: Updated to add feature X\n..."
  }
}
```

---

## 6. Derive Values Not In Plan
**FORBIDDEN:** Computing intermediate values on behalf of planner

Example:
```python
# REJECTED
plan says: write_file(path="/tmp/config.json", content=generate_config(...))
windsurf: "I'll generate the config better"
→ generates different config than planned
```

**Why:** All values must come from Antigravity.

**Correct:** Plan must specify exact content:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "/tmp/config.json",
    "content": "{...exact JSON...}"
  }
}
```

---

## 7. Skip Steps (Even "Obvious" Ones)
**FORBIDDEN:** Skipping redundant or no-op steps

Example:
```python
# REJECTED
step says: write_file(path="empty.txt", content="")
windsurf thinks: "That's useless, skip it"
```

**Why:** Plan defines contract. Every step has intent.

**Correct:** Execute exactly as planned.

---

## 8. Reorder Steps for "Efficiency"
**FORBIDDEN:** Changing execution order

Example:
```python
# REJECTED
plan: step1, step2, step3
windsurf: "step2 and step3 are independent, run in parallel"
```

**Why:** Breaks audit determinism and contract.

**Correct:** Execute in order as defined. No parallelism.

---

## 9. Add Error Handling Not In Plan
**FORBIDDEN:** Wrapping steps in try-catch Windsurf invented

Example:
```python
# REJECTED
step doesn't mention error handling
windsurf adds: try-catch with custom recovery
```

**Why:** Error contracts belong in the plan.

**Correct:** If error handling is needed, declare in plan:
```json
{
  "tool": "...",
  "arguments": {...},
  "continue_on_error": false
}
```

---

## 10. Use Reasoning or Narrative
**FORBIDDEN:** Arguments containing explanation or justification

Example:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "file.js",
    "content": "...",
    "intent": "Adding this feature because it improves performance"
  }
}
```

**REJECTED** ← "because" is reasoning text

**Correct:** Intent should be factual, not reasoned:
```json
{
  "tool": "write_file",
  "arguments": {
    "path": "file.js",
    "content": "...",
    "intent": "Add feature X"
  }
}
```

---

## Enforcement

These anti-patterns are caught by hooks:

- `pre_plan_immutability_enforcement` → detects plan modifications
- `pre_write_file_guardrails` → detects boundary violations
- `pre_no_reasoning_in_executor` → detects reasoning text
- `executor_control.json` → strict step execution policy

**Violation = Immediate Rejection + Audit Log + No Recovery**
