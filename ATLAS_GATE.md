# ATLAS-GATE: Execution-Only Enforcement Layer

**Hard security boundary for windsurf-hooker**

---

## Core Invariant (Non-Negotiable)

```
If a capability is not routed through ATLAS-GATE, it must be impossible.
```

This means:

- ❌ No "soft allow + warning"
- ❌ No fallback paths
- ❌ No silent success
- ✅ Everything funnels through one MCP surface

---

## What Is ATLAS-GATE?

A **syscall boundary** for AI code modification.

Like how a kernel enforces syscalls, ATLAS-GATE enforces all file, command, and resource access through a single, validated interface.

### The Model

```
Windsurf (AI Agent)
    ↓
    └─→ Only ATLAS-GATE tools exist in allowlist
    └─→ Only ATLAS-GATE commands allowed
    └─→ No direct filesystem access
    └─→ No escape primitives (subprocess, os.system, etc.)
    ↓
ATLAS-GATE (Syscall Table)
    ├─→ atlas_gate.read
    ├─→ atlas_gate.write
    ├─→ atlas_gate.exec
    └─→ atlas_gate.stat
    ↓
System (Controlled Execution)
```

---

## Four Mandatory Hooks (Non-Negotiable)

These hooks form the boundary. If any is bypassed, the system is compromised.

### 1. `pre_mcp_tool_use_atlas_gate.py` — Primary Gate

**File:** `windsurf-hooks/pre_mcp_tool_use_atlas_gate.py`

**Purpose:** Hard choke point. Only ATLAS-GATE tools permitted.

**Behavior:**
1. Reject any tool not prefixed with `atlas_gate.`
2. Reject missing or malformed ATLAS-GATE payloads
3. Reject attempts to smuggle execution via arguments
4. Validate schema for each ATLAS-GATE operation

**Invariant:** If this hook is bypassed, system is compromised. No exceptions.

**Example Block:**

```
BLOCKED: Only ATLAS-GATE tools are permitted
  Tool requested: read_file
  ATLAS-GATE tools: atlas_gate.read, atlas_gate.write, atlas_gate.exec, atlas_gate.stat
  Solution: Route through atlas_gate.read
```

### 2. `pre_run_command_kill_switch.py` — Absolute Kill Switch

**File:** `windsurf-hooks/pre_run_command_kill_switch.py`

**Purpose:** Unconditional block on direct command execution.

**Behavior:**
1. Check execution profile (from policy.json)
2. If `execution_profile == "execution_only"`: BLOCK all commands
3. No regex, no heuristics, no exceptions

**Invariant:** If this hook ever allows execution → bug.

**Code:**
```python
if execution_profile == "execution_only":
    block("Direct command execution is disabled. Use atlas_gate.exec")
```

### 3. `pre_write_code_escape_detection.py` — Escape Blocker

**File:** `windsurf-hooks/pre_write_code_escape_detection.py`

**Purpose:** Prevent capability re-introduction via code.

**Blocks:**
- `subprocess` module
- `os.system`, `os.popen`
- `open()`, file operations
- `socket`, `urllib`, `requests`
- `exec()`, `eval()`, `compile()`
- `ctypes`, `cffi`
- Shell wrappers (`bash -c`, `sh -c`, etc.)

**Invariant:** Even if not executed yet, escape primitives are forbidden.

**Example Block:**

```
BLOCKED: Code contains escape attempts
  src/main.py:42 (subprocess) → subprocess.run([...])
  Reason: Escape primitives forbidden in execution-only mode
```

### 4. `pre_filesystem_write_atlas_enforcement.py` — Filesystem Boundary

**File:** `windsurf-hooks/pre_filesystem_write_atlas_enforcement.py`

**Purpose:** Enforce that agent never touches filesystem directly.

**Blocks:**
- Writes to sensitive paths (.ssh, /etc, /proc, /root, etc.)
- Binary blob creation (.exe, .dll, .so, etc.)
- Escape attempts (../, ~/, absolute paths)
- Direct writes in execution-only mode (must use atlas_gate.write)

**Invariant:** Agent only requests file ops via ATLAS-GATE.

**Example Block:**

```
BLOCKED: Filesystem write policy violation
  /root/.ssh/config: SSH keys and config (forbidden_path)
  .env: Environment files (forbidden_path)
  Reason: Direct filesystem write not allowed in execution-only mode
```

---

## Execution Flow (End-to-End)

Correct execution-only lifecycle:

```
1. AI intent arrives
   ↓
2. pre_user_prompt (intent only) → OK
   ↓
3. pre_mcp_tool_use (PRIMARY GATE)
   ├─ atlas_gate.read  → OK
   ├─ atlas_gate.write → OK
   ├─ atlas_gate.exec  → OK
   ├─ atlas_gate.stat  → OK
   └─ anything else    → BLOCK
   ↓
4. pre_run_command (KILL SWITCH)
   └─ execution_profile == "execution_only" → BLOCK all
   ↓
5. pre_write_code (ESCAPE DETECTION)
   └─ No subprocess, os.system, open(), socket, exec, eval
   ↓
6. pre_filesystem_write (BOUNDARY ENFORCEMENT)
   └─ Only atlas_gate.write permitted
   ↓
7. Code written & executed
   ↓
8. Verification & post-write checks
```

**There is no other path.**

---

## Policy Configuration

### 🔴 The Panic Button: Instant Global Lock

If the system must be locked immediately:

```bash
jq '.execution_profile="locked"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

**Immediate Effect (next hook invocation):**
- ❌ All shell execution blocked
- ❌ All MCP tools blocked (except what hooks explicitly allow)
- ❌ All filesystem writes blocked (unless routed via ATLAS-GATE and hooks permit)
- ❌ No bypass via prompts, retries, or partial state

**Why it works:**
- Hooks re-read `policy.json` on every invocation
- Collapsing `execution_profile` to `"locked"` invalidates all capability grants simultaneously
- Not a soft mode—hard capability revocation
- Survives stuck agents, retry loops, hallucinated compliance

**Guaranteed Properties:**
- ✅ Atomic (single write)
- ✅ Reversible
- ✅ Takes effect on next hook invocation (no restart)
- ✅ Does not rely on environment variables, process state, or agent cooperation

**Critical Invariant:**
Every execution-capable hook must branch on `execution_profile`. If any hook ignores it, the panic button is broken.

**Restore to Dev Mode:**
```bash
jq '.execution_profile="dev"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

**Restore to ATLAS-Gate-Only Mode:**
```bash
jq '.execution_profile="atlas_only"' /etc/windsurf/policy/policy.json | sponge /etc/windsurf/policy/policy.json
```

---

### Enable Execution-Only Mode

In `windsurf/policy/policy.json`:

```json
{
  "execution_profile": "execution_only",
  "atlas_gate_enabled": true,

  "mcp_tool_allowlist": [
    "atlas_gate.read",
    "atlas_gate.write",
    "atlas_gate.exec",
    "atlas_gate.stat"
  ],

  "block_commands_regex": [".*"],

  "filesystem": {
    "direct_read": false,
    "direct_write": false,
    "direct_exec": false
  },

  "atlas_gate": {
    "enabled": true,
    "enforce_mode": "strict",
    "operations": {
      "atlas_gate.read": {
        "required_fields": ["path"],
        "optional_fields": ["encoding", "max_bytes"]
      },
      "atlas_gate.write": {
        "required_fields": ["path", "content"],
        "optional_fields": ["mode", "encoding"]
      },
      "atlas_gate.exec": {
        "required_fields": ["command"],
        "optional_fields": ["timeout", "env"]
      },
      "atlas_gate.stat": {
        "required_fields": ["path"],
        "optional_fields": []
      }
    },
    "escape_patterns": [
      "subprocess\\.",
      "os\\.system",
      "open\\(",
      "exec\\(",
      "eval\\(",
      "socket\\."
    ]
  }
}
```

---

## ATLAS-GATE Tool Interface

All ATLAS-GATE tools follow a schema:

### atlas_gate.read

```json
{
  "tool_name": "atlas_gate.read",
  "path": "/path/to/file",
  "encoding": "utf-8",
  "max_bytes": 1000000
}
```

**Returns:** File content

### atlas_gate.write

```json
{
  "tool_name": "atlas_gate.write",
  "path": "/path/to/file",
  "content": "...",
  "mode": "0644",
  "encoding": "utf-8"
}
```

**Returns:** Write status, checksum

### atlas_gate.exec

```json
{
  "tool_name": "atlas_gate.exec",
  "command": "python3 script.py",
  "timeout": 30,
  "env": { "VAR": "value" }
}
```

**Returns:** Exit code, stdout, stderr

### atlas_gate.stat

```json
{
  "tool_name": "atlas_gate.stat",
  "path": "/path/to/file"
}
```

**Returns:** File metadata (size, mtime, permissions, etc.)

---

## Failure Modes (What NOT To Do)

### ❌ Mistake 1: Allowing read_file "Temporarily"

```python
"mcp_tool_allowlist": [
    "atlas_gate.read",
    "read_file"  # ← BACKDOOR
]
```

**Why bad:** `read_file` is a native tool that bypasses enforcement.

**Fix:** Remove `read_file`. Use only `atlas_gate.read`.

### ❌ Mistake 2: Letting Code Generation Include subprocess "for Later"

```python
def process_data(data):
    subprocess.run([...])  # ← Delayed execution
```

**Why bad:** Code execution may happen later outside your enforcement.

**Fix:** Block at `pre_write_code_escape_detection`.

### ❌ Mistake 3: Allowing Shell Execution If Command Is "Safe"

```python
if command in ["ls", "pwd", "echo"]:
    allow_execution()  # ← Safety is contextual, not lexical
```

**Why bad:** Context changes. "Safe" commands can be chained into unsafe ones.

**Fix:** Block unconditionally. Use `atlas_gate.exec` with explicit validation.

### ❌ Mistake 4: Relying on Prompts ("Please Only Use ATLAS-GATE")

```
"Important: The AI should only use ATLAS-GATE tools. Please respect this."
```

**Why bad:** Prompts are not enforcement. AI will eventually try native tools.

**Fix:** Make ATLAS-GATE the only option in `mcp_tool_allowlist`.

---

## Deployment

### Step 1: Update Policy

Edit `windsurf/policy/policy.json`:

```bash
# Set execution profile
jq '.execution_profile = "execution_only"' policy.json > policy.json.tmp
mv policy.json.tmp policy.json

# Verify ATLAS-GATE tools in allowlist
grep -A 4 "mcp_tool_allowlist" policy.json
```

### Step 2: Deploy ATLAS-GATE Hooks

```bash
# Copy new hooks
cp windsurf-hooks/pre_*_atlas_*.py /usr/local/share/windsurf-hooks/
cp windsurf-hooks/pre_run_command_kill_switch.py /usr/local/share/windsurf-hooks/

# Update hooks.json (already done)
cp windsurf/hooks.json /etc/windsurf/
```

### Step 3: Validate

```bash
# Test ATLAS-GATE primary gate
echo '{"tool_info": {"tool_name": "atlas_gate.read", "path": "/etc/hosts"}}' | \
  python3 /usr/local/share/windsurf-hooks/pre_mcp_tool_use_atlas_gate.py

# Expected: exit code 0 (success)

# Test rejection of non-ATLAS-GATE tools
echo '{"tool_info": {"tool_name": "read_file", "path": "/etc/hosts"}}' | \
  python3 /usr/local/share/windsurf-hooks/pre_mcp_tool_use_atlas_gate.py 2>&1

# Expected: BLOCKED message
```

### Step 4: Monitor

Check logs after first interactions:

```bash
# Should see ATLAS-GATE in use
grep -i "atlas_gate" logs/*

# Should NOT see direct commands
grep -i "subprocess\|os\.system\|open(" logs/*
```

---

## Testing Checklist

- [ ] Policy updated: `execution_profile = "execution_only"`
- [ ] ATLAS-GATE hooks deployed to `/usr/local/share/windsurf-hooks/`
- [ ] hooks.json updated (primary gates first)
- [ ] Non-ATLAS-GATE tools blocked (test with read_file)
- [ ] Direct commands blocked (test with bash -c)
- [ ] Escape patterns blocked (test with subprocess code)
- [ ] Filesystem boundary enforced (test with /etc write)
- [ ] ATLAS-GATE.read works (test legitimate read)
- [ ] ATLAS-GATE.write works (test legitimate write)
- [ ] ATLAS-GATE.exec works (test legitimate command)
- [ ] Logs show enforcement (no bypass attempts)

---

## Mental Model (The Key Insight)

Think of ATLAS-GATE as:

**A syscall boundary, not a tool.**

Just like a kernel enforces syscalls:
- User code cannot directly access memory
- User code cannot directly access hardware
- All access goes through the kernel's syscall table

Similarly, windsurf with ATLAS-GATE:
- AI cannot directly read files (use `atlas_gate.read`)
- AI cannot directly execute commands (use `atlas_gate.exec`)
- AI cannot directly write files (use `atlas_gate.write`)
- All access goes through ATLAS-GATE

windsurf's job is to ensure:

✓ The AI cannot cross that boundary
✓ Even accidentally
✓ Even indirectly
✓ Even in future code it writes

**Hooks are the kernel.**
**ATLAS-GATE is the syscall table.**

---

## Verification: Is My System Truly Execution-Only?

Ask these questions:

1. **Can the AI use non-ATLAS-GATE tools?**
   - No → ✓
   - Yes → ✗ (mcp_tool_allowlist misconfigured)

2. **Can the AI execute shell commands directly?**
   - No → ✓
   - Yes → ✗ (pre_run_command_kill_switch missing)

3. **Can the AI write code with subprocess/os.system?**
   - No → ✓
   - Yes → ✗ (pre_write_code_escape_detection missing)

4. **Can the AI write arbitrary files?**
   - No (only via atlas_gate.write) → ✓
   - Yes → ✗ (pre_filesystem_write_atlas_enforcement missing)

5. **Is there a fallback path if ATLAS-GATE fails?**
   - No → ✓
   - Yes → ✗ (system is compromised)

If all answers are ✓, your system is truly execution-only.

---

## Failure Recovery

If ATLAS-GATE fails or is compromised:

1. **Identify the bypass**
   ```bash
   grep -i "blocked\|denied" logs/* | head -20
   ```

2. **Check which hook failed**
   - pre_mcp_tool_use_atlas_gate? → MCP allowlist issue
   - pre_run_command_kill_switch? → Command blocked
   - pre_write_code_escape_detection? → Code pattern issue
   - pre_filesystem_write_atlas_enforcement? → Filesystem issue

3. **Verify hook is running**
   ```bash
   grep "atlas_gate\|kill_switch\|escape_detection" /etc/windsurf/hooks.json
   ```

4. **Check policy**
   ```bash
   jq '.execution_profile' /etc/windsurf/policy/policy.json
   ```

5. **Redeploy if needed**
   ```bash
   bash validate-implementation.sh
   sudo cp windsurf-hooks/*.py /usr/local/share/windsurf-hooks/
   ```

---

## References

- [Hook Architecture](HOOK_ARCHITECTURE.md) — Full 7-phase system
- [Policy Configuration](windsurf/policy/policy.json) — All settings
- [Migration Guide](MIGRATION_GUIDE.md) — Deployment steps
- [Quick Reference](HOOK_QUICK_REFERENCE.md) — Usage guide

---

## Summary

ATLAS-GATE is:

✓ A hard security boundary (like syscalls)
✓ Enforced by 4 critical hooks
✓ Configured via policy.json
✓ Non-negotiable (no fallbacks)
✓ Verified by validation script
✓ Tested before deployment

**Once enabled, the AI cannot escape execution-only mode.**

No compromises. No fallbacks. No exceptions.

This is what true execution-only enforcement looks like.
