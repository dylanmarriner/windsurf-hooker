# Panic Button Quick Reference

## One-Line Commands

### 🔴 LOCK (Revoke All Capabilities)
```bash
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### 🟢 UNLOCK (Restore to Standard)
```bash
jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### 🔵 EXECUTION-ONLY MODE
```bash
jq '.execution_profile="execution_only"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### ⚪ DEV MODE
```bash
jq '.execution_profile="dev"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### 🟡 ATLAS-ONLY MODE
```bash
jq '.execution_profile="atlas_only"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

## Check Current Status
```bash
jq '.execution_profile' /etc/windsurf/policy/policy.json
```

## What Gets Blocked When Locked

| Component | Blocked | Reason |
|-----------|---------|--------|
| Shell commands | ✅ | pre_run_command_kill_switch checks at line 51 |
| MCP tools | ✅ | pre_mcp_tool_use_atlas_gate checks at line 117 |
| Code writes | ✅ | pre_write_code_escape_detection checks at line 138 |
| File writes | ✅ | pre_filesystem_write_atlas_enforcement checks at line 203 |

## Immediate Actions

**If system needs immediate lock:**
```bash
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
echo "System locked. Next hook invocation will fail safely."
```

**If system needs immediate unlock:**
```bash
jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
echo "System unlocked. Standard policies now active."
```

## Test That Lock Works

```bash
# Set locked mode
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# Test command block (should fail)
echo '{"tool_info": {"command": "ls"}}' | \
  python3 /usr/local/share/windsurf-hooks/pre_run_command_kill_switch.py 2>&1

# Expected: exit code 2, "LOCKED mode" message
```

## Profiles Explained

- **dev** — Full capabilities, no restrictions
- **standard** — Default, policy-based restrictions
- **execution_only** — ATLAS-GATE only, no direct execution
- **atlas_only** — ATLAS-GATE restricted execution
- **locked** — All capabilities revoked (emergency mode)

## Why This Works

1. Hooks re-read policy.json **on every invocation**
2. Lock is **atomic** (single write)
3. Takes effect **immediately** (no restart)
4. **Survives retries** (state-independent)
5. **No fallback paths** (all blocked)

## Emergency Contact

If locked incorrectly:
```bash
# Verify current state
jq '.execution_profile' /etc/windsurf/policy/policy.json

# If stuck, restore standard
jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# Verify restoration
jq '.execution_profile' /etc/windsurf/policy/policy.json
```

## Documentation

- Full details: [PANIC_BUTTON.md](PANIC_BUTTON.md)
- Implementation: [IMPLEMENTATION_SUMMARY_PANIC_BUTTON.md](IMPLEMENTATION_SUMMARY_PANIC_BUTTON.md)
- Automated tests: [test-panic-button.sh](test-panic-button.sh)
- Architecture: [ATLAS_GATE.md](ATLAS_GATE.md)
