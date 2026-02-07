# Hook Quick Reference

**Cheat sheet for understanding windsurf hook behavior**

---

## What Gets Blocked

### ❌ Will Always Block

| Condition | Hook | Fix |
|-----------|------|-----|
| Writes outside repo root | `pre_filesystem_write` | Keep changes in repo |
| Binary files (.exe, .dll, .so) | `pre_filesystem_write` | Don't create binaries |
| >50 new files created | `pre_filesystem_write` | Break into smaller changes |
| Test failure | `post_write_verify` | Fix failing tests |
| Policy token missing (code write) | `pre_user_prompt_gate` | Include `[AUDIT_OK]` token |
| Policy token missing (ship) | `pre_user_prompt_gate` | Include `[SHIP:GATES_OK]` token |
| Prohibited pattern (TODO, FIXME, mock data) | `pre_write_code` | Remove placeholder patterns |
| Logic completely removed | `pre_write_code` | Preserve executable code |

### ⚠️ Will Warn (Normal Mode) / Block (SHIP Mode)

| Condition | Hook | Notes |
|-----------|------|-------|
| Missing logging in large change | `post_write_observability` | Add print/logger calls |
| Missing metrics | `post_write_observability` | Add metric collection |
| Large diff (>100 lines) | `pre_write_diff_quality` | Break into smaller edits |
| Too many files edited | `pre_write_diff_quality` | Separate concerns |
| Intent/implementation mismatch | `post_write_semantic_diff` | Match code to description |

### ℹ️ Will Warn Only

| Condition | Hook | Action |
|-----------|------|--------|
| No PLAN.md found | `pre_plan_resolution` | Informational only |
| Circular edit pattern | `post_session_entropy_check` | Suggest PLAN mode |
| Verification script missing | `post_write_verify` | Still runs if it exists |

---

## Operational Modes

### 🎯 PLAN Mode
**When:** Explicit plan provided in PLAN.md

**Benefits:**
- Scope enforcement enabled
- All tools available
- Plan-aware validation

**What to include in PLAN.md:**
```markdown
## Objective
Brief description of what you're building

## Scope
Files to modify:
- src/main.ts
- src/utils/helpers.ts

Directories:
- docs/api/

## Steps
1. Modify main.ts
2. Add tests
3. Update docs
```

**Activation:**
```
I will implement: [AUDIT_OK]

PLAN.md contains the complete plan. Proceed.
```

### 🔧 REPAIR Mode
**When:** Fixing bugs or failures

**Restrictions:**
- Mock patterns forbidden
- Logic must be preserved
- No placeholder text allowed

**Activation:**
```
Fix the broken test [AUDIT_OK] [REPAIR_OK]
```

### 🔍 AUDIT Mode
**When:** Reviewing changes

**Characteristics:**
- Pure analysis, no execution
- Observability checks relaxed
- Good for code reviews

**Activation:**
```
Audit the changes I made [AUDIT_OK]
```

### 🚀 SHIP Mode
**When:** Production deployment

**Enforcement:**
- ALL quality gates applied
- Observability required
- Scope strictly validated
- Diff quality enforced

**Activation:**
```
Ship this to production [AUDIT_OK] [SHIP:GATES_OK]
```

---

## Token Reference

### Required Tokens

| Token | Usage | Reason |
|-------|-------|--------|
| `[AUDIT_OK]` | Any code write or modification | Ensure audit gate is passed |
| `[SHIP:GATES_OK]` | Shipping/deployment intent | Production safety gate |

### Optional Context Markers

| Marker | Effect | Example |
|--------|--------|---------|
| `[MODE:PLAN]` | Enable plan-based scope | Forces scope validation |
| `[MODE:REPAIR]` | Enable repair mode | Forbids mocks, enforces logic |
| `[MODE:AUDIT]` | Audit mode | Pure analysis |
| `[MODE:SHIP]` | Enforce all gates | Production deployment |
| `[MODE:STRICT]` | Strict validation | Strict scope compliance |

---

## Common Hook Interactions

### Scenario 1: Implementing a Feature

```
I will implement the user authentication module [AUDIT_OK]

PLAN.md specifies:
- src/auth/index.ts
- src/auth/token.ts
- tests/auth.test.ts

↓ Hook Execution ↓

1. pre_intent_classification → "code_write" (high confidence)
2. pre_plan_resolution → PLAN_OK=true, scope=["src/auth/"]
3. pre_user_prompt_gate → ✓ Token present
4. pre_write_diff_quality → ✓ Quality checks pass
5. pre_write_code → ✓ No prohibited patterns
6. pre_filesystem_write → ✓ Only creating planned files
7. post_write_semantic_diff → ✓ Intent matched
8. post_write_observability → ⚠️ Add logging
9. post_write_verify → ✓ Tests pass
```

### Scenario 2: Fixing a Bug

```
Fix the authentication token bug [AUDIT_OK] [REPAIR_OK]

↓ Hook Execution ↓

1. pre_write_code → ✓ No mock patterns allowed
2. pre_write_code → ✓ Logic preserved (bug fix)
3. post_write_verify → ✓ Test suite passes
4. post_write_semantic_diff → ✓ Intent: fix bug, action: fix bug ✓
```

### Scenario 3: Large Refactoring (5+ files)

```
Refactor the logging module [AUDIT_OK]

PLAN.md:
## Scope
- src/logging/
- tests/logging/

↓ Hook Execution ↓

1. pre_write_diff_quality → ⚠️ Many files (emit warnings)
2. (In SHIP mode, would BLOCK)

Fix: Break into smaller changes or provide PLAN with explicit scope
```

---

## Error Messages: Decoding

### `BLOCKED: code write requires audit token`
**Meaning:** You're modifying code but forgot token

**Fix:** Add `[AUDIT_OK]` to your prompt

---

### `BLOCKED: Prohibited pattern in src/main.ts: TODO`
**Meaning:** Your code contains a placeholder

**Fix:** Remove the TODO comment or replace with implementation

---

### `BLOCKED: Executable logic reduced`
**Meaning:** You removed working code and replaced it with comments

**Fix:** Preserve the logic or explain why it should be removed

---

### `BLOCKED: verification failed (tests or checks failed)`
**Meaning:** `./scripts/verify` returned non-zero exit code

**Fix:** Run `./scripts/verify` locally and fix failing tests

---

### `BLOCKED: Large single edit: 200 lines`
**Meaning:** Single edit exceeds 100 lines (SHIP mode)

**Fix:** Break change into smaller, focused edits

---

### `WARNING: No logging instrumentation in large change(s)`
**Meaning:** You added 50+ lines of code without logging (SHIP mode)

**Fix:** Add logging/debug output to your code

---

### `WARNING: Plan found at PLAN.md / Declared scope: ...`
**Meaning:** Plan was auto-discovered (informational)

**Fix:** None needed. Plan will be used for scope validation

---

## File Structure Reference

```
windsurf-hooker/
├── windsurf-hooks/                  # Hook implementations
│   ├── pre_intent_classification.py
│   ├── pre_plan_resolution.py
│   ├── pre_user_prompt_gate.py
│   ├── pre_write_code_policy.py
│   ├── pre_write_diff_quality.py
│   ├── pre_filesystem_write.py
│   ├── pre_mcp_tool_use_allowlist.py
│   ├── pre_run_command_blocklist.py
│   ├── post_write_verify.py
│   ├── post_write_semantic_diff.py
│   ├── post_write_observability.py
│   ├── post_refusal_audit.py
│   └── post_session_entropy_check.py
├── windsurf/
│   ├── hooks.json                   # Hook registry (execution order)
│   └── policy/
│       └── policy.json              # Runtime configuration
├── PLAN.md                          # (Your plan for current work)
├── HOOK_ARCHITECTURE.md             # Full architecture doc
├── MIGRATION_GUIDE.md               # Upgrade instructions
└── HOOK_QUICK_REFERENCE.md          # This file
```

---

## Policy Tuning

Edit `policy.json` to customize behavior:

```json
{
  "intent_classification": {
    "code_write_confidence_threshold": 0.80  // Lower = more gating
  },
  "diff_quality": {
    "max_lines_per_edit": 100,      // Reduce for smaller edits
    "max_total_lines": 500,
    "max_files_per_pass": 10        // Reduce for single-concern edits
  },
  "filesystem_write": {
    "max_new_files": 50             // Reduce to prevent file explosion
  },
  "observability": {
    "min_lines_for_logging": 10,    // Raise to require more logging
    "enforce_in_ship_mode": true    // Enforced in production
  }
}
```

---

## Debugging Hooks

### Run Hook Locally

```bash
# Create test input
echo '{"tool_info": {"prompt": "implement a function"}}' > test.json

# Run hook
python3 windsurf-hooks/pre_intent_classification.py < test.json
```

### Add Debug Output

Hooks output JSON on success. On failure, check stderr:

```bash
python3 hook.py < test.json 2>&1 | grep -i "error\|blocked\|warning"
```

### Check Hook Execution Order

See `hooks.json` for registration order. Hooks execute in order they're listed.

---

## Best Practices

### ✅ DO

- Include `[AUDIT_OK]` for any code modifications
- Create PLAN.md before large refactoring
- Keep edits focused on single concern
- Add logging to new code (especially in SHIP mode)
- Run tests locally before shipping
- Break large changes into smaller PRs

### ❌ DON'T

- Commit TODO/FIXME comments
- Remove working code without explaining
- Edit 10+ files in one pass without a plan
- Create many new files without a plan
- Skip verification in SHIP mode
- Use mock data in production code

---

## See Also

- `HOOK_ARCHITECTURE.md` — Full design
- `MIGRATION_GUIDE.md` — Upgrade process
- `windsurf-hooks/*.py` — Individual hook source
- `policy.json` — Configuration
