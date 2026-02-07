# Hook Architecture: Complete Reference

**windsurf-hooker Phase 2 Implementation**

This document describes the complete 7-phase hook architecture implementing structured constraint-enforcement for AI code modification.

---

## Mental Model

Perfect windsurf behavior emerges when:

```
intent → plan → scoped capability → enforcement → verification
```

Not from more blocking, but from better placement of constraints.

---

## The 7 Phases

### Phase 1: Prompt & Intent Classification (Before Code Exists)

These hooks shape what windsurf believes it is being asked to do.

#### 1.1 `pre_intent_classification` (NEW)

**Purpose:** Separate WHAT from HOW. Classify user intent with confidence scoring.

**File:** `windsurf-hooks/pre_intent_classification.py`

**Input:** User prompt

**Output (JSON):**
```json
{
  "primary_intent": "code_write|repair|audit|explore",
  "confidence": 0.92,
  "matched_patterns": [...],
  "is_high_confidence": true,
  "all_scores": { ... }
}
```

**Key Rules:**
- No blocking: this hook is purely informational
- Intent must be monotonic: later hooks may narrow, never widen
- Confidence scoring guides downstream gating

**Invariant:** Plans grant capability; absence never removes it

#### 1.2 `pre_user_prompt_gate` (REFACTORED)

**Purpose:** Intent-aware policy token enforcement.

**File:** `windsurf-hooks/pre_user_prompt_gate.py`

**Changes from previous version:**
- Now consumes `pre_intent_classification` results
- Checks confidence threshold before requiring tokens
- Separates code_write intent from shipping intent
- More precise gating (not every prompt needs tokens)

**Key Rules:**
- Code write + high confidence → require `[AUDIT_OK]`
- Shipping intent → require `[SHIP:GATES_OK]`
- No blocking on missing plans (plans annotate, they don't restrict)

---

### Phase 2: Planning & Structure (Resource Allocation)

These hooks discover plans and attach metadata to context.

#### 2.1 `pre_plan_resolution` (NEW, CRITICAL)

**Purpose:** Dynamically discover plans. Attach scope metadata. Never block.

**File:** `windsurf-hooks/pre_plan_resolution.py`

**Input:** Repo state (looks for PLAN.md, .plan/, etc.)

**Output (JSON):**
```json
{
  "plan_ok": true,
  "plan_path": "PLAN.md",
  "declared_scope": ["src/main.ts", "src/utils/"],
  "plan_text_preview": "...",
  "has_scope_declaration": true,
  "has_plan_markers": true
}
```

**Key Rules:**
- If plan exists → PLAN_OK=true, extract scope
- If not → PLAN_OK=false, silently no-op
- Validation: only return files/dirs that exist
- Never block on missing plan

**Discovery Logic:**
1. Search: `PLAN.md`, `.plan/PLAN.md`, `docs/PLAN.md`, `.github/PLAN.md`
2. Parse: Look for sections ("## Files to modify", "## Scope", etc.)
3. Extract: File paths, directory patterns
4. Validate: Only return paths that exist in repo

**Scope Declaration Markers:**
```markdown
## Scope:
- src/main.ts
- src/utils/

## Files to modify:
- `config/app.ts`
- `docs/README.md`
```

---

### Phase 3: Code Write Enforcement (The Power Zone)

#### 3.1 `pre_write_diff_quality` (NEW)

**Purpose:** Enforce diff hygiene, not correctness. Reduce entropy in changes.

**File:** `windsurf-hooks/pre_write_diff_quality.py`

**Checks:**
- Diff too large? (>100 lines per edit → warn)
- Total changes too much? (>500 lines → warn)
- Multiple files edited? (>10 files → warn)
- Multiple concerns mixed? (testing + logic + docs → warn)
- Generated code without comments? (require ≥10% comment ratio)

**Behavior:**
- Normal mode: WARN (emit analysis to context)
- SHIP mode: BLOCK if quality fails

**Invariant:** Quality gates reduce entropy; they don't enforce correctness

#### 3.2 `pre_write_code` (REFACTORED)

**Purpose:** Policy enforcement for code changes.

**File:** `windsurf-hooks/pre_write_code_policy.py`

**Checks:**
1. Prohibited patterns: FIXME, TODO, mock data, hacks
2. Logic preservation: don't remove executable logic
3. Mock rejection in REPAIR mode

**Changes from v1:**
- Better mode detection (REPAIR vs PLAN vs normal)
- Clearer error messages with file paths
- Support for PLAN_OK context

**Invariant:** Executable logic is precious; never reduce it

#### 3.3 `pre_filesystem_write` (NEW)

**Purpose:** Prevent pathological file creation.

**File:** `windsurf-hooks/pre_filesystem_write.py`

**Checks:**
- File explosion (>50 new files → BLOCK)
- Escape attempts (writes outside repo root → BLOCK)
- Binary blobs (.exe, .dll, .pyc → BLOCK)
- Suspicious patterns (node_modules, .git, .env → BLOCK)

**Invariant:** Codegen should be surgical, not expansive

---

### Phase 4: Tool & Command Execution

#### 4.1 `pre_mcp_tool_use` (EXISTING)

**File:** `windsurf-hooks/pre_mcp_tool_use_allowlist.py`

**Enhancement opportunity:** Context-dependent allowlisting
- PLAN mode → more tools allowed
- REPAIR mode → fewer tools allowed
- SHIP mode → restricted set

#### 4.2 `pre_run_command` (EXISTING)

**File:** `windsurf-hooks/pre_run_command_blocklist.py`

**Enhancement opportunity:** Repo-aware checks
- Disallow `rm -rf` outside temp dirs
- Block network access unless explicitly allowed

---

### Phase 5: Post-Write Verification (Trust & Quality)

#### 5.1 `post_write_code` (REFACTORED: `post_write_verify`)

**Purpose:** Run verification script if it exists.

**File:** `windsurf-hooks/post_write_verify.py`

**Key change:** Inverted logic
- Script exists → RUN it (enforce tests)
- Script missing → WARN, don't block
- Failure → BLOCK

**Invariant:** Verify on negative signal (tests fail), never on absence

#### 5.2 `post_write_semantic_diff` (NEW)

**Purpose:** Ensure code matches intent (semantic trust).

**File:** `windsurf-hooks/post_write_semantic_diff.py`

**Checks:**
- Did implementation reflect plan?
- Do function names match description?
- Were required files actually modified?
- Scope respected?

**Behavior:**
- Normal mode: WARN if intent/implementation mismatch
- STRICT mode: BLOCK on scope violation
- Logs implemented vs. intended identifiers

#### 5.3 `post_write_observability` (NEW)

**Purpose:** Enforce Definition of Done (logging, metrics, traces).

**File:** `windsurf-hooks/post_write_observability.py`

**Checks:**
- Logging instrumentation (for debugging)
- Metrics collection (for monitoring)
- Distributed traces (for observability)

**Behavior:**
- WARN in DEV/AUDIT modes
- BLOCK in SHIP mode if missing
- Skips checks for small changes (<10 lines)

---

### Phase 6: Error Handling & Auditing

#### 6.1 `post_refusal_audit` (NEW)

**Purpose:** Ensure refusals are structured and justified.

**File:** `windsurf-hooks/post_refusal_audit.py`

**Validates:**
```json
{
  "refused": true,
  "reason": "policy_violation|scope_violation|safety_check|...",
  "message": "Human-readable explanation",
  "details": ["detail1", "detail2"],
  "recovery_steps": ["step1", "step2"],
  "exit_code": 2
}
```

**Key Rule:** No silent failures. Refusals must be explicit.

**Invariant:** No fabricated progress reported

---

### Phase 7: Meta Hooks (Self-Correction)

#### 7.1 `post_session_entropy_check` (NEW, EXPERIMENTAL)

**Purpose:** Detect degradation in session coherence.

**File:** `windsurf-hooks/post_session_entropy_check.py`

**Detects:**
- Circular edit patterns (same file edited >3 times)
- Conversation drift (intent changing repeatedly)
- Repeated error patterns
- Resource exhaustion

**Actions:**
- WARN: Log degradation signal
- ESCALATE: Suggest entering PLAN mode
- ALERT: Force explicit operator override

**Invariant:** Entropy increases; detect reversals as signal

---

## Configuration: policy.json

All thresholds and patterns are policy-driven:

```json
{
  "tokens": { ... },
  "prohibited_patterns": { ... },
  "intent_classification": {
    "code_write_confidence_threshold": 0.80,
    "high_confidence_gates": true
  },
  "plan_resolution": {
    "search_paths": [...],
    "auto_enforce_scope": false,
    "require_scope_declaration": false
  },
  "diff_quality": {
    "max_lines_per_edit": 100,
    "max_total_lines": 500,
    "max_files_per_pass": 10,
    "ship_mode_enforces_quality": true
  },
  "filesystem_write": {
    "max_new_files": 50,
    "suspicious_patterns": [...],
    "suspicious_extensions": [...]
  },
  "observability": {
    "min_lines_for_logging": 10,
    "min_lines_for_metrics": 20,
    "enforce_in_ship_mode": true
  },
  "session_entropy": {
    "circular_retry_threshold": 3,
    "entropy_alert_threshold": 0.7,
    "escalation_mode": "plan"
  }
}
```

---

## Hook Execution Order

```
User Prompt
    ↓
1. pre_intent_classification        (emit intent class)
    ↓
2. pre_plan_resolution              (emit plan metadata)
    ↓
3. pre_user_prompt_gate             (enforce tokens)
    ↓
    [Intent identified, plan attached]
    ↓
4. pre_write_diff_quality           (check diff size/coherence)
    ↓
5. pre_write_code                   (enforce policy)
    ↓
6. pre_filesystem_write             (prevent pathological writes)
    ↓
    [Code written]
    ↓
7. post_write_semantic_diff         (verify intent match)
    ↓
8. post_write_observability         (check logging/metrics)
    ↓
9. post_write_code (verify script)  (run tests if they exist)
    ↓
10. post_refusal_audit              (if failed, audit refusal)
    ↓
11. post_session_entropy_check      (detect degradation)
```

---

## Operational Modes

### PLAN Mode
- User provides explicit plan
- `PLAN_OK=true` in context
- Scope enforcement enabled
- All tools available

### REPAIR Mode
- User fixing existing code
- Mock patterns forbidden
- Logic preservation enforced
- Reduced tool scope

### AUDIT Mode
- User reviewing changes
- Pure analysis, no execution
- Full observability required
- Shipping forbidden

### SHIP Mode
- Production deployment
- All quality gates enforced
- Observability required
- Scope strictly validated

---

## Absolute Rules (Invariants)

1. ❌ **No hook blocks on missing optional structure**
   - Missing plan → WARN, don't block
   - Missing tests → WARN, don't block
   - Missing logs → WARN in SHIP, WARN in DEV

2. ❌ **No correctness checks before code exists**
   - `pre_write_code` checks policy, not logic
   - Semantic checks happen post-write

3. ❌ **No global policy for runtime artifacts**
   - Each phase has its own thresholds
   - Configuration is policy-driven

4. ✅ **Plans grant power, they don't restrict it**
   - Plan existence → enables scoped enforcement
   - Plan absence → enables free editing (with tokens)

5. ✅ **Enforcement happens at the richest context point**
   - Intent classification happens first (richest info)
   - Plan enforcement happens post-discovery
   - Semantic checks happen post-write

6. ✅ **Negative signals block; absence doesn't**
   - Test failure → BLOCK
   - Verification failure → BLOCK
   - Prohibited pattern found → BLOCK
   - But absence of tests → WARN only

---

## Debugging & Testing

### Test Hooks Locally

```bash
# Test intent classification
echo '{"tool_info": {"prompt": "implement a new function"}}' | \
  python3 windsurf-hooks/pre_intent_classification.py

# Test plan resolution
echo '{}' | python3 windsurf-hooks/pre_plan_resolution.py

# Test diff quality
echo '{"tool_info": {"edits": [...]}}' | \
  python3 windsurf-hooks/pre_write_diff_quality.py
```

### Enable Debug Output

Add to policy.json:
```json
{
  "debug": {
    "emit_all_classifications": true,
    "verbose_errors": true,
    "log_plan_discovery": true
  }
}
```

---

## Future Extensions

1. **Contextual Tool Allowlisting:** PLAN mode grants more tools
2. **Multi-System Rollout:** Ansible integration for team coordination
3. **Rolling Deployments:** Canary + progressive delivery
4. **Health Checks:** Continuous verification of deployed files
5. **Policy Versioning:** Track and audit policy changes

---

## See Also

- `ARCHITECTURE.md` — Deployment & system design
- `policy/policy.json` — Runtime configuration
- `hooks.json` — Hook registry
- Individual hook files in `windsurf-hooks/`
