# The Panic Button: Instant Global Lock

**One-line command to instantly revoke ALL capabilities.**

## Activate (Lock System)

```bash
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

## Effect (Immediate on Next Hook Invocation)

- ❌ All shell execution blocked
- ❌ All MCP tools blocked
- ❌ All filesystem writes blocked
- ❌ All code writes blocked
- ❌ No bypass via prompts, retries, or partial state

## Why It Works

1. **Every critical hook re-reads policy.json on every invocation**
   - `pre_mcp_tool_use_atlas_gate.py` → blocks all tools
   - `pre_run_command_kill_switch.py` → blocks all commands
   - `pre_write_code_escape_detection.py` → blocks all code writes
   - `pre_filesystem_write_atlas_enforcement.py` → blocks all filesystem writes

2. **Atomic state change**
   - Single `jq` write, single policy.json change
   - No race conditions, no partial states
   - Not dependent on agent cooperation

3. **Takes effect immediately**
   - Next hook invocation hits the `execution_profile == "locked"` check
   - No restart required
   - No environment variables or process state

4. **Survives any failure mode**
   - Stuck agents trying to retry → blocked
   - Hallucinated compliance → blocked
   - Partial state → doesn't matter, policy is absolute

## Guaranteed Properties

| Property | Value |
|----------|-------|
| Atomic | ✅ Single write operation |
| Reversible | ✅ Restore with one command |
| Restart-free | ✅ Takes effect immediately |
| No bypass | ✅ No fallback paths |
| Survives failures | ✅ Independent of agent state |

## Deactivate

### Restore to Dev Mode
```bash
jq '.execution_profile="dev"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### Restore to Standard Mode
```bash
jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### Restore to Execution-Only Mode
```bash
jq '.execution_profile="execution_only"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

### Restore to ATLAS-Gate-Only Mode
```bash
jq '.execution_profile="atlas_only"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

## Verify Lock Status

```bash
jq '.execution_profile' /etc/windsurf/policy/policy.json
```

Expected output (when locked): `"locked"`

## Implementation Details

### Hook Enforcement

All 4 critical hooks check for `execution_profile == "locked"` at entry:

1. **pre_mcp_tool_use_atlas_gate.py** (line 117-122)
   ```python
   if execution_profile == "locked":
       block("System is in LOCKED mode (panic button activated).",
             ["All MCP tool access is revoked.", "Contact administrator to unlock."])
   ```

2. **pre_run_command_kill_switch.py** (line 51-57)
   ```python
   if execution_profile == "locked":
       block("BLOCKED: System is in LOCKED mode (panic button activated).\n"
             "  All shell execution and capabilities are revoked.\n"
             "  Contact administrator to unlock.")
   ```

3. **pre_write_code_escape_detection.py** (line 138-144)
   ```python
   if execution_profile == "locked":
       block("System is in LOCKED mode (panic button activated).",
             ["All code writes are revoked.", "Contact administrator to unlock."])
   ```

4. **pre_filesystem_write_atlas_enforcement.py** (line 203-209)
   ```python
   if execution_profile == "locked":
       block("System is in LOCKED mode (panic button activated).",
             ["All filesystem writes are revoked.", "Contact administrator to unlock."])
   ```

### Critical Invariant

**If any execution-capable hook does NOT check `execution_profile == "locked"`, the panic button is broken.**

Current status:
- ✅ All 4 critical hooks implemented
- ✅ All check policy.json on every invocation
- ✅ All block on locked mode before any logic

## Usage Scenarios

### Scenario 1: Agent Stuck in Retry Loop
```bash
# Agent is stuck, retry attempts detected
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# Next hook invocation will fail immediately
# No more retries possible
```

### Scenario 2: Suspected Compromise
```bash
# Unknown agent behavior detected
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# All capabilities revoked instantly
# Investigation can proceed safely
```

### Scenario 3: Policy Emergency
```bash
# New policy violation discovered in production
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# All work stopped immediately
# Policy can be updated safely
```

## Testing the Panic Button

### Test 1: Verify Lock Blocks Commands
```bash
# Set locked mode
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# Try to execute a command (should be blocked)
echo '{"tool_info": {"command": "ls"}}' | \
  python3 /usr/local/share/windsurf-hooks/pre_run_command_kill_switch.py 2>&1

# Expected output: "BLOCKED: System is in LOCKED mode"
# Expected exit code: 2
```

### Test 2: Verify Lock Blocks Tools
```bash
# With locked mode still active:

# Try to use a tool (should be blocked)
echo '{"tool_info": {"tool_name": "atlas_gate.read", "path": "/etc/hosts"}}' | \
  python3 /usr/local/share/windsurf-hooks/pre_mcp_tool_use_atlas_gate.py 2>&1

# Expected output: "BLOCKED: System is in LOCKED mode"
# Expected exit code: 2
```

### Test 3: Verify Unlock Works
```bash
# Restore standard mode
jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json

# Now commands should no longer be blocked by the lock
# (Other policy checks may still apply)
```

## Emergency Contact

If system is in locked mode and needs immediate unlock:

1. **Verify lock status:**
   ```bash
   jq '.execution_profile' /etc/windsurf/policy/policy.json
   ```

2. **If legitimately locked, restore appropriate profile:**
   ```bash
   jq '.execution_profile="standard"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
   ```

3. **Verify restoration:**
   ```bash
   jq '.execution_profile' /etc/windsurf/policy/policy.json
   ```

## See Also

- [ATLAS_GATE.md](ATLAS_GATE.md) — Complete execution-only enforcement
- [HOOK_ARCHITECTURE.md](HOOK_ARCHITECTURE.md) — 7-phase hook system
- [policy.json](windsurf/policy/policy.json) — Runtime configuration
