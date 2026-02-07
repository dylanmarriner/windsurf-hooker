# Migration Guide: v1 → v2 Hook Architecture

**Upgrading to the comprehensive 7-phase hook system**

---

## What Changed

### New Hooks (8 total)

| Hook | Purpose | Phase | Blocking |
|------|---------|-------|----------|
| `pre_intent_classification` | Classify user intent | 1 | No |
| `pre_plan_resolution` | Discover plans & scope | 2 | No |
| `pre_write_diff_quality` | Check diff coherence | 3 | SHIP only |
| `pre_filesystem_write` | Prevent pathological writes | 3 | Yes |
| `post_write_semantic_diff` | Verify intent match | 5 | STRICT only |
| `post_write_observability` | Check logging/metrics | 5 | SHIP only |
| `post_refusal_audit` | Audit refusal structure | 6 | No |
| `post_session_entropy_check` | Detect circular patterns | 7 | No |

### Refactored Hooks

| Hook | Changes |
|------|---------|
| `pre_user_prompt_gate` | Now uses intent classification; smarter gating |
| `pre_write_code_policy` | Better error messages; mode detection |
| `post_write_verify` | Inverted logic (WARN on missing, BLOCK on failure) |

### Policy File Expanded

`policy.json` now includes configuration sections for:
- Intent classification thresholds
- Plan resolution paths
- Diff quality limits
- Filesystem write restrictions
- Observability requirements
- Session entropy detection

---

## Step-by-Step Upgrade

### 1. Backup Current Installation

```bash
sudo cp -r /usr/local/share/windsurf-hooks /usr/local/share/windsurf-hooks.backup.v1
sudo cp /etc/windsurf/policy/policy.json /etc/windsurf/policy/policy.json.backup.v1
```

### 2. Update Hook Files

Copy all new hooks to the deployment location:

```bash
# From repo root
sudo cp windsurf-hooks/*.py /usr/local/share/windsurf-hooks/
chmod +x /usr/local/share/windsurf-hooks/*.py
```

**New files to add:**
- `pre_intent_classification.py`
- `pre_plan_resolution.py`
- `pre_write_diff_quality.py`
- `pre_filesystem_write.py`
- `post_write_semantic_diff.py`
- `post_write_observability.py`
- `post_refusal_audit.py`
- `post_session_entropy_check.py`

### 3. Update hooks.json

Replace `/etc/windsurf/hooks.json` with the new version:

```bash
sudo cp windsurf/hooks.json /etc/windsurf/hooks.json
```

This adds entries for all new hooks in the correct execution order.

### 4. Update policy.json

Replace `/etc/windsurf/policy/policy.json`:

```bash
sudo cp windsurf/policy/policy.json /etc/windsurf/policy/policy.json
```

**Important:** Review any custom policies and merge them:

```bash
# View differences
diff /etc/windsurf/policy/policy.json.backup.v1 /etc/windsurf/policy/policy.json

# If you had custom prohibited_patterns, merge them:
jq '.prohibited_patterns += {"custom": [...]}' /etc/windsurf/policy/policy.json > policy.json.tmp
sudo mv policy.json.tmp /etc/windsurf/policy/policy.json
```

### 5. Test Hook Execution

Run hooks locally to verify they load correctly:

```bash
# Test each hook
for hook in windsurf-hooks/*.py; do
  echo "Testing $(basename $hook)..."
  echo '{}' | python3 "$hook" > /dev/null 2>&1 && echo "✓ OK" || echo "✗ FAILED"
done
```

### 6. Monitor First Interactions

After upgrade, monitor the first few user interactions:

```bash
# Check Windsurf logs for hook execution
tail -f ~/.codeium/logs/*

# Look for new hook output
grep -i "intent_classification\|plan_resolution\|entropy" logs/*
```

---

## Behavioral Changes You'll Notice

### 1. Intent Classification Output

You may see new JSON output from intent classification:

```
{
  "primary_intent": "code_write",
  "confidence": 0.92,
  "is_high_confidence": true
}
```

This is normal. It's used internally to guide downstream hooks.

### 2. Plan Discovery

If you have a `PLAN.md` file, it will be automatically discovered:

```
[INFO] Plan found at PLAN.md
[INFO] Declared scope: src/main.ts, src/utils/
```

### 3. More Granular Error Messages

Errors now include more context:

**Before:**
```
BLOCKED: Prohibited pattern detected
```

**After:**
```
BLOCKED: Prohibited pattern in src/main.ts: TODO
```

### 4. Diff Quality Warnings

You may see warnings about large changes:

```
[WARN] Large single edit: 150 lines in src/config.ts
       (consider breaking into smaller edits)
```

These are warnings in normal mode, but will block in SHIP mode.

### 5. Verification Script Behavior Changed

**Before:** Missing `./scripts/verify` → BLOCK

**After:** Missing `./scripts/verify` → WARN only

This is intentional. Absence of tests shouldn't grant false confidence, but also shouldn't prevent development.

---

## Migration Checklist

- [ ] Backup existing installation
- [ ] Copy new hook files
- [ ] Copy updated `hooks.json`
- [ ] Copy updated `policy.json`
- [ ] Review merged policies
- [ ] Test all hooks locally
- [ ] Monitor first interactions
- [ ] Document custom policy rules
- [ ] Train team on new modes (PLAN, REPAIR, AUDIT, SHIP)
- [ ] Review HOOK_ARCHITECTURE.md with team

---

## Rollback Procedure

If you need to revert to v1:

```bash
# Restore backed-up files
sudo cp /usr/local/share/windsurf-hooks.backup.v1/* /usr/local/share/windsurf-hooks/
sudo cp /etc/windsurf/policy/policy.json.backup.v1 /etc/windsurf/policy/policy.json

# Test that hooks load
echo '{}' | python3 /usr/local/share/windsurf-hooks/pre_user_prompt_gate.py
```

---

## Performance Impact

The new hooks add minimal overhead:

| Hook | Typical Runtime |
|------|-----------------|
| `pre_intent_classification` | <10ms |
| `pre_plan_resolution` | 5-20ms (depends on repo size) |
| `pre_write_diff_quality` | <10ms |
| `pre_filesystem_write` | <5ms |
| `post_write_semantic_diff` | 20-50ms |
| `post_write_observability` | <10ms |
| `post_refusal_audit` | <5ms |
| `post_session_entropy_check` | 30-100ms |

Total: ~100-200ms added latency (usually imperceptible)

---

## FAQ

**Q: Will my existing workflows break?**

A: No. The new hooks are designed to be non-breaking. Warnings are emitted but don't block in normal mode.

**Q: Do I need to update my PLAN.md format?**

A: No. The hook looks for common patterns (## Scope:, ## Files to modify:, etc.). Any standard markdown plan works.

**Q: Can I disable the new hooks?**

A: Yes. Remove entries from `hooks.json` to disable specific hooks. But we don't recommend disabling security hooks.

**Q: What's the "PLAN_OK" mode?**

A: When a PLAN.md exists and is valid, `PLAN_OK=true` is set in context. This enables scope enforcement. See HOOK_ARCHITECTURE.md.

**Q: How do I know if a hook is blocking my code?**

A: Hooks output structured error messages. Look for `BLOCKED:` prefix. The hook's docstring (top of file) explains what can cause blocking.

**Q: Can I customize policy thresholds?**

A: Yes. Edit `policy.json` and adjust values like `max_lines_per_edit`, `max_new_files`, etc.

---

## Support

For issues during migration:

1. Check that all Python files are executable: `chmod +x /usr/local/share/windsurf-hooks/*.py`
2. Test hooks in isolation: `echo '{}' | python3 hook_name.py`
3. Review hook docstrings for invariants and rules
4. Check `HOOK_ARCHITECTURE.md` for design decisions
5. Open an issue with hook name and error output

---

## Next Steps

1. **Read HOOK_ARCHITECTURE.md** to understand the 7-phase model
2. **Create or update PLAN.md** in your repo to leverage plan resolution
3. **Review policy.json** and adjust thresholds for your team
4. **Train your team** on operational modes (PLAN, REPAIR, AUDIT, SHIP)
5. **Monitor first week** of usage for any friction
