# Hook Implementation Index

**Complete guide to the 7-phase hook architecture implementation**

---

## What This Is

A production-ready, policy-driven hook system that enforces code quality, safety, and intent-alignment through 13 hooks across 7 phases of AI-assisted code modification.

**Status:** ✅ Complete, tested, and validated

**Version:** 2.0 (7-phase architecture)

---

## Quick Start

### For Developers Using windsurf

1. **Read this first:** [HOOK_QUICK_REFERENCE.md](HOOK_QUICK_REFERENCE.md)
   - What gets blocked vs. warned
   - How to use PLAN.md
   - Common error messages decoded
   - Operational modes (PLAN, REPAIR, AUDIT, SHIP)

2. **When something blocks:** Check the error message
   - Hooks output structured errors with solutions
   - See "Error Messages: Decoding" section in HOOK_QUICK_REFERENCE.md

3. **For advanced usage:** [HOOK_ARCHITECTURE.md](HOOK_ARCHITECTURE.md)
   - Full reference for all 7 phases
   - Each hook's purpose and invariants
   - Configuration reference

### For DevOps/Admins Deploying

1. **Read:** [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
   - Step-by-step deployment instructions
   - What changed from v1 to v2
   - Rollback procedure
   - Performance impact

2. **Run validation:** 
   ```bash
   bash validate-implementation.sh
   ```

3. **Customize:** Edit `windsurf/policy/policy.json`
   - All thresholds and patterns configurable
   - No code changes needed

### For Architecture Review

1. **Overview:** [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
   - What was built and why
   - Specification compliance
   - Design principles
   - Usage examples

2. **Deep dive:** [HOOK_ARCHITECTURE.md](HOOK_ARCHITECTURE.md)
   - Complete 7-phase system design
   - Each hook's responsibilities
   - Interaction patterns
   - Configuration details

---

## The 7 Phases (At a Glance)

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Intent Classification                              │
│ ├─ pre_intent_classification  → classify intent + confidence│
│ └─ pre_user_prompt_gate       → enforce policy tokens       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 2: Planning & Structure                               │
│ └─ pre_plan_resolution        → discover PLAN.md + scope    │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 3: Code Write Enforcement                             │
│ ├─ pre_write_diff_quality     → check diff hygiene          │
│ ├─ pre_write_code_policy      → enforce policy + logic      │
│ └─ pre_filesystem_write       → prevent pathological writes │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 4: Tool & Command Execution                           │
│ ├─ pre_mcp_tool_use           → allowlist enforcement       │
│ └─ pre_run_command            → blocklist enforcement       │
└────────────────────┬────────────────────────────────────────┘
                     ↓
                  [CODE WRITTEN]
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 5: Post-Write Verification                            │
│ ├─ post_write_semantic_diff   → verify intent match         │
│ ├─ post_write_observability   → check logging/metrics       │
│ └─ post_write_verify          → run verification script     │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 6: Error Handling & Auditing                          │
│ └─ post_refusal_audit         → validate refusal structure  │
└────────────────────┬────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────────┐
│ PHASE 7: Meta-Level Checks                                  │
│ └─ post_session_entropy_check → detect circular patterns    │
└─────────────────────────────────────────────────────────────┘
```

---

## Hook Files (13 Total)

### New Hooks (8)

| File | Phase | Purpose | Blocking |
|------|-------|---------|----------|
| `pre_intent_classification.py` | 1 | Classify intent with confidence | No |
| `pre_plan_resolution.py` | 2 | Discover plans & extract scope | No |
| `pre_write_diff_quality.py` | 3 | Check diff hygiene | SHIP only |
| `pre_filesystem_write.py` | 3 | Prevent pathological writes | Yes |
| `post_write_semantic_diff.py` | 5 | Verify intent match | STRICT only |
| `post_write_observability.py` | 5 | Check logging/metrics | SHIP only |
| `post_refusal_audit.py` | 6 | Audit refusal structure | No |
| `post_session_entropy_check.py` | 7 | Detect circular patterns | No |

### Refactored Hooks (3)

| File | Changes |
|------|---------|
| `pre_user_prompt_gate.py` | Intent-aware token gating |
| `pre_write_code_policy.py` | Better mode detection |
| `post_write_verify.py` | Inverted logic (warn on missing) |

### Existing Hooks (2)

| File | Notes |
|------|-------|
| `pre_mcp_tool_use_allowlist.py` | Compatible, can extend |
| `pre_run_command_blocklist.py` | Compatible, can extend |

---

## Key Files & Configuration

### Hook Implementation

```
windsurf-hooks/
├── Phase 1: Intent
│   ├── pre_intent_classification.py (95 lines)
│   └── pre_user_prompt_gate.py (refactored)
├── Phase 2: Planning
│   └── pre_plan_resolution.py (180 lines)
├── Phase 3: Code Write
│   ├── pre_write_diff_quality.py (175 lines)
│   ├── pre_write_code_policy.py (refactored)
│   └── pre_filesystem_write.py (165 lines)
├── Phase 4: Tools
│   ├── pre_mcp_tool_use_allowlist.py (existing)
│   └── pre_run_command_blocklist.py (existing)
├── Phase 5: Verification
│   ├── post_write_semantic_diff.py (170 lines)
│   ├── post_write_observability.py (140 lines)
│   └── post_write_verify.py (refactored)
├── Phase 6: Error Handling
│   └── post_refusal_audit.py (145 lines)
└── Phase 7: Meta
    └── post_session_entropy_check.py (180 lines)
```

### Configuration

```
windsurf/
├── hooks.json              # Hook registry & execution order
└── policy/
    └── policy.json         # Runtime configuration
                            # - tokens, patterns
                            # - intent classification thresholds
                            # - plan resolution settings
                            # - diff quality limits
                            # - filesystem write restrictions
                            # - observability requirements
                            # - session entropy detection
```

### Documentation

```
📚 Documentation/
├── HOOK_ARCHITECTURE.md        (650 lines) ← CORE REFERENCE
├── HOOK_QUICK_REFERENCE.md     (400 lines) ← DEVELOPER CHEAT SHEET
├── MIGRATION_GUIDE.md          (350 lines) ← DEPLOYMENT GUIDE
├── IMPLEMENTATION_SUMMARY.md   (500 lines) ← OVERVIEW
└── HOOK_IMPLEMENTATION_INDEX.md (this file) ← NAVIGATION
```

---

## Reading Guide

### By Role

**Software Developer:**
1. Start: HOOK_QUICK_REFERENCE.md (15 min read)
2. When blocked: Error message decoder section
3. Advanced: HOOK_ARCHITECTURE.md phases 1-5

**DevOps / System Admin:**
1. Start: MIGRATION_GUIDE.md (20 min read)
2. Then: windsurf/policy/policy.json (tune thresholds)
3. Reference: HOOK_ARCHITECTURE.md configuration section

**Architect / Tech Lead:**
1. Start: IMPLEMENTATION_SUMMARY.md (15 min read)
2. Deep dive: HOOK_ARCHITECTURE.md (full 7 phases)
3. Review: Individual hook files for design details

**Manager / Project Lead:**
1. Quick: This index file (5 min)
2. Overview: IMPLEMENTATION_SUMMARY.md (15 min)
3. FAQ: MIGRATION_GUIDE.md

### By Question

**"What's blocking my code?"**
→ HOOK_QUICK_REFERENCE.md: "Error Messages: Decoding"

**"How do I deploy this?"**
→ MIGRATION_GUIDE.md: "Step-by-Step Upgrade"

**"How do I create a PLAN.md?"**
→ HOOK_QUICK_REFERENCE.md: "Operational Modes"
→ HOOK_ARCHITECTURE.md: "Phase 2: Planning"

**"What are the policies?"**
→ windsurf/policy/policy.json (+ comments in file)
→ HOOK_ARCHITECTURE.md: "Configuration Reference"

**"How do the hooks interact?"**
→ HOOK_ARCHITECTURE.md: "Hook Execution Order"

**"Can I customize thresholds?"**
→ MIGRATION_GUIDE.md: "Policy Tuning"
→ windsurf/policy/policy.json

**"What if something breaks?"**
→ MIGRATION_GUIDE.md: "Rollback Procedure"
→ validate-implementation.sh (run to check)

---

## Validation & Testing

### Automated Validation

```bash
# Run comprehensive validation
bash validate-implementation.sh

# Expected output:
# ✓ All checks passed!
# Implementation is complete and ready for deployment.
```

### Manual Testing

```bash
# Test individual hook
echo '{"tool_info": {"prompt": "implement a function"}}' | \
  python3 windsurf-hooks/pre_intent_classification.py

# Run all hooks through test
python3 << 'EOF'
import json, subprocess
for hook in glob.glob("windsurf-hooks/*.py"):
    result = subprocess.run(["python3", hook], input=json.dumps({}))
    assert result.returncode in [0, 2], f"Hook {hook} failed"
EOF
```

---

## Key Concepts

### Operational Modes

| Mode | When | Gate Strength | Example |
|------|------|---------------|---------|
| PLAN | Explicit plan | High | Features, refactoring |
| REPAIR | Bug fixes | Medium | Fixing failing tests |
| AUDIT | Code review | Low | Pure analysis |
| SHIP | Production | Maximum | Deployment |

### Invariants (Never Violate)

1. ❌ Don't block on missing optional structure
2. ❌ Don't enforce correctness before code exists
3. ✅ Plans grant power, not restrict it
4. ✅ Negative signals block; absence doesn't
5. ✅ Intent precedes structure
6. ✅ Enforcement at richest context point

### Thresholds

| Component | Default | Tunable | Purpose |
|-----------|---------|---------|---------|
| Intent confidence | 0.80 | Yes | Gate trigger level |
| Max lines per edit | 100 | Yes | Diff size warning |
| Max new files | 50 | Yes | File explosion prevention |
| Min logging lines | 10 | Yes | Observability requirement |

---

## Common Workflows

### Feature Development
```
User writes: "Implement feature X [AUDIT_OK]"
PLAN.md specifies scope: src/feature/

Hooks check:
1. Intent → code_write (confidence 0.92)
2. Plan found → scope validation enabled
3. Tokens present → ✓
4. Code quality → ✓ (if <100 lines per edit)
5. Policy → ✓ (no TODOs, no mocks)
6. Scope → ✓ (only src/feature/* edited)
Result: ✓ Approved
```

### Bug Fix
```
User writes: "Fix token bug [AUDIT_OK] [REPAIR_OK]"

Hooks check:
1. Intent → repair
2. Mode → REPAIR (mocks forbidden, logic preserved)
3. No mock patterns → ✓
4. Logic preserved → ✓
5. Tests pass → ✓
Result: ✓ Approved
```

### Production Ship
```
User writes: "Ship to prod [AUDIT_OK] [SHIP:GATES_OK]"

Hooks apply MAXIMUM enforcement:
1. All quality gates → ✓
2. Logging required → ✓
3. Metrics required → ✓
4. Tests pass → ✓
5. Scope respected → ✓
Result: ✓ Approved for deployment
```

---

## Architecture Decision Records

### Why 7 Phases?

Phases follow the information richness of context:

1. **Prompt phase:** Only text, classify intent
2. **Planning phase:** Repo context available, discover plans
3. **Code write phase:** Rich context, full enforcement
4. **Execution phase:** Tools available, controlled execution
5. **Verification phase:** Code exists, semantic checks possible
6. **Error handling:** Failures logged, refusal audited
7. **Meta checks:** Session patterns detected

### Why Non-Blocking Hooks?

Plans, intent classification, and entropy checks don't block because:
- Absence of plan ≠ bad code
- High entropy ≠ always wrong
- Intent classification confidence < 1.0

They inform and warn, never restrict.

### Why Policy-Driven?

All thresholds in `policy.json` because:
- Teams have different standards
- Policies evolve over time
- No code changes for customization
- Centralized, auditable configuration

---

## Troubleshooting

### Hook Not Executing

1. Check file exists: `ls -l windsurf-hooks/hook_name.py`
2. Check syntax: `python3 -m py_compile windsurf-hooks/hook_name.py`
3. Check entry in hooks.json: `grep hook_name windsurf/hooks.json`
4. Check permissions: `chmod +x windsurf-hooks/*.py`

### Weird Error Messages

1. Ensure policy.json is valid JSON: `python3 -m json.tool windsurf/policy/policy.json`
2. Check hook_name.py for docstring: `head -20 windsurf-hooks/hook_name.py`
3. Run hook manually: `echo '{}' | python3 windsurf-hooks/hook_name.py`

### Too Many Warnings

1. Review policy.json thresholds
2. Adjust `max_lines_per_edit`, `max_new_files`, etc.
3. Create PLAN.md to enable scope validation
4. Re-read HOOK_QUICK_REFERENCE.md for operational modes

---

## Performance

Expected overhead per hook execution:

| Hook | Time | Notes |
|------|------|-------|
| pre_intent_classification | 5-10ms | Pattern matching |
| pre_plan_resolution | 5-20ms | Disk I/O (first time cached) |
| pre_write_diff_quality | 5-10ms | Line counting |
| pre_filesystem_write | 5ms | Path validation |
| post_write_semantic_diff | 20-50ms | Regex extraction |
| post_write_observability | 5-10ms | Pattern search |
| Others | 1-5ms | Simple checks |

**Total:** ~100-200ms per code edit (imperceptible)

---

## Support & Documentation

| Need | Resource | Time |
|------|----------|------|
| Quick overview | This file | 5 min |
| Developer how-to | HOOK_QUICK_REFERENCE.md | 15 min |
| Deployment guide | MIGRATION_GUIDE.md | 20 min |
| Full reference | HOOK_ARCHITECTURE.md | 30 min |
| Implementation details | IMPLEMENTATION_SUMMARY.md | 15 min |
| Individual hook logic | Hook source code | varies |

---

## Next Steps

1. **Choose your path:**
   - Developer? → Read HOOK_QUICK_REFERENCE.md
   - DevOps? → Read MIGRATION_GUIDE.md
   - Architect? → Read HOOK_ARCHITECTURE.md

2. **Run validation:**
   ```bash
   bash validate-implementation.sh
   ```

3. **Create PLAN.md** for your project (if doing planned work)

4. **Review policy.json** and adjust thresholds

5. **Deploy** following MIGRATION_GUIDE.md

6. **Monitor** first interactions

---

## Version & Status

- **Version:** 2.0 (7-phase architecture)
- **Status:** ✅ Complete and production-ready
- **Last Updated:** 2026-02-04
- **Tested:** All 13 hooks validated
- **Backwards Compatible:** Yes (drop-in replacement)

---

## Quick Links

- 🔗 [HOOK_ARCHITECTURE.md](HOOK_ARCHITECTURE.md) — Full reference
- 🔗 [HOOK_QUICK_REFERENCE.md](HOOK_QUICK_REFERENCE.md) — Developer guide
- 🔗 [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) — Deployment
- 🔗 [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — Overview
- 🔗 [windsurf/policy/policy.json](windsurf/policy/policy.json) — Configuration
- 🔗 [windsurf/hooks.json](windsurf/hooks.json) — Hook registry
- 🔗 [validate-implementation.sh](validate-implementation.sh) — Validation script

---

**Ready to get started? Pick your reading path above.** 🚀
