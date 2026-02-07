# ATLAS-GATE Windsurf write_file Tool Guide

## Overview

With the enforcement system locked down, **all file writes must use `atlas_gate.write` tool** (Windsurf terminology: `write_file`).

This is the **ONLY authorized method** to modify files in protected directories:
- `/etc/windsurf/`
- `/usr/local/share/windsurf-hooks/`
- All code repositories under enforcement

---

## Tool Details

### Tool Name
```
atlas_gate.write
mcp_atlas-gate-mcp_write_file  (MCP equivalent)
write_file                      (Windsurf shorthand)
```

### Required Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path` | string | YES | Full path to file to write |
| `content` | string | YES | File content to write |
| `mode` | string | NO | File permissions (e.g., "0644", "0755") |
| `encoding` | string | NO | Encoding (default: "utf-8") |

### Example Usage

```json
{
  "tool_name": "atlas_gate.write",
  "path": "/etc/windsurf/policy/policy.json",
  "content": "{...json content...}",
  "mode": "0644",
  "encoding": "utf-8"
}
```

---

## Windsurf Implementation

### In Windsurf Code

```python
# Using atlas_gate.write
response = atlas_gate.write(
    path="/etc/windsurf/policy/policy.json",
    content=policy_json_string,
    mode="0644"
)
```

### In Windsurf Plans

```markdown
## Step: Update Enforcement Policy

Write updated policy using atlas_gate.write:

```json
{
  "tool_name": "atlas_gate.write",
  "path": "/etc/windsurf/policy/policy.json",
  "content": {...},
  "mode": "0644"
}
```
```

---

## Protected Paths

### System-Level Protection

Paths that **REQUIRE** atlas_gate.write:

```
/etc/windsurf/                          (All windsurf config)
/etc/windsurf/policy/policy.json        (Enforcement policy)
/usr/local/share/windsurf-hooks/        (All 24 enforcement hooks)
/usr/local/share/windsurf-hooks/*.py    (Individual hooks)
```

### Repository Protection

Protected in code repositories:

```
./.windsurf-hooks/                      (Repo-local enforcement)
./.windsurf-hooks/*.py                  (Individual repo hooks)
./windsurf/policy/                      (Repo-local policy)
./windsurf/policy/policy.json           (Repo policy)
```

### User-Level Protection

Protected in user directories:

```
~/.local/share/windsurf-hooks/          (User-local hooks)
~/.local/share/windsurf-hooks/*.py      (Individual user hooks)
```

---

## Access Control

### Who Can Use atlas_gate.write

✓ Authorized users with:
- Active Windsurf session
- Valid API credentials
- Proper authorization level

### Who Cannot Use Direct Writes

✗ Direct file writes (BLOCKED)
✗ Manual edits (BLOCKED)
✗ Scripts using system tools (BLOCKED)
✗ Any non-atlas_gate method (BLOCKED)

---

## Workflow

### 1. Update Policy

```python
import json

# Load current policy
current_policy = load_policy()

# Modify policy
current_policy["some_key"] = "new_value"

# Write back via atlas_gate.write
response = atlas_gate.write(
    path="/etc/windsurf/policy/policy.json",
    content=json.dumps(current_policy, indent=2),
    mode="0644"
)

# Verify write
if response.status == "success":
    print(f"Policy updated: {response.checksum}")
```

### 2. Update Enforcement Hook

```python
# Load new hook code
hook_code = read_file("new_hook.py")

# Write via atlas_gate.write
response = atlas_gate.write(
    path="/usr/local/share/windsurf-hooks/pre_write_new_hook.py",
    content=hook_code,
    mode="0755"  # Executable
)

# Verify
if response.status == "success":
    print("Hook deployed successfully")
```

### 3. Deploy Configuration

```python
config = {
    "enforcement_level": "strict",
    "languages": 15,
    "prohibitions": [...]
}

response = atlas_gate.write(
    path="/etc/windsurf/config.json",
    content=json.dumps(config),
    mode="0644"
)
```

---

## Error Handling

### Common Errors

#### Direct Write Attempt (BLOCKED)

```python
# This will FAIL
with open("/etc/windsurf/policy/policy.json", "w") as f:
    f.write(content)

# Error: BLOCKED: Enforcement system protection violation
#        HARD FAIL: Cannot write to protected enforcement system file
```

#### Missing atlas_gate.write

```python
# This will FAIL
import subprocess
subprocess.run(["cp", "policy.json", "/etc/windsurf/policy/policy.json"])

# Error: BLOCKED: Shell command execution disabled
```

#### Using Wrong Tool

```python
# This will FAIL
file_write(path="/etc/windsurf/policy/policy.json", content=...)

# Error: BLOCKED: Enforcement system protection violation
#        Must use atlas_gate.write tool
```

### Success Response

```json
{
  "status": "success",
  "path": "/etc/windsurf/policy/policy.json",
  "bytes_written": 2048,
  "checksum": "sha256:abc123...",
  "timestamp": "2026-02-08T12:00:00Z"
}
```

---

## Validation

### Pre-Write Validation

atlas_gate.write validates:

1. **Path authorization**
   - Is path in allowed write locations?
   - Is user authorized?

2. **Content validation**
   - JSON syntax (for .json files)
   - Python syntax (for .py files)
   - File format correctness

3. **Permissions**
   - Valid mode (0644, 0755, etc.)
   - User has write capability

### Post-Write Validation

After write succeeds:

1. File checksum verified
2. Content readable and valid
3. Permissions set correctly
4. Change logged to audit trail

---

## Audit Trail

All atlas_gate.write operations are logged:

```
2026-02-08T12:00:00Z - User: admin
  Tool: atlas_gate.write
  Path: /etc/windsurf/policy/policy.json
  Status: SUCCESS
  Checksum: sha256:abc123...
  Diff: [...changes...]
```

---

## Best Practices

### ✓ DO

- ✓ Use atlas_gate.write for all protected files
- ✓ Validate content before writing
- ✓ Check write response status
- ✓ Log all modifications
- ✓ Use appropriate file modes (0644 for data, 0755 for executables)
- ✓ Include descriptive messages
- ✓ Document changes in audit trail

### ✗ DON'T

- ✗ Use direct file operations
- ✗ Use shell commands (cp, mv, etc.)
- ✗ Use alternative tools
- ✗ Bypass validation
- ✗ Write without checking response
- ✗ Use overly permissive modes
- ✗ Modify files without audit trail

---

## Examples

### Example 1: Update Policy

```python
def update_enforcement_policy(new_rule):
    """Add new enforcement rule via atlas_gate.write"""
    
    # Load current policy
    policy = atlas_gate.read(path="/etc/windsurf/policy/policy.json")
    policy_dict = json.loads(policy)
    
    # Add rule
    policy_dict["prohibited_patterns"]["new_category"] = new_rule
    
    # Write back
    response = atlas_gate.write(
        path="/etc/windsurf/policy/policy.json",
        content=json.dumps(policy_dict, indent=2),
        mode="0644"
    )
    
    if response.status != "success":
        raise Exception(f"Write failed: {response.error}")
    
    return response

# Usage
update_enforcement_policy(["new_pattern_1", "new_pattern_2"])
```

### Example 2: Deploy New Hook

```python
def deploy_hook(hook_name, hook_code):
    """Deploy new enforcement hook"""
    
    path = f"/usr/local/share/windsurf-hooks/{hook_name}.py"
    
    response = atlas_gate.write(
        path=path,
        content=hook_code,
        mode="0755"  # Executable
    )
    
    if response.status == "success":
        print(f"✓ Hook deployed: {hook_name}")
        print(f"  Checksum: {response.checksum}")
    else:
        print(f"✗ Deployment failed: {response.error}")
    
    return response

# Usage
hook_code = """
#!/usr/bin/env python3
...hook implementation...
"""
deploy_hook("pre_write_custom_check", hook_code)
```

### Example 3: Batch Updates

```python
def batch_update_hooks(hooks_dict):
    """Update multiple hooks via atlas_gate.write"""
    
    results = []
    
    for hook_name, hook_code in hooks_dict.items():
        path = f"/usr/local/share/windsurf-hooks/{hook_name}.py"
        
        response = atlas_gate.write(
            path=path,
            content=hook_code,
            mode="0755"
        )
        
        results.append({
            "hook": hook_name,
            "status": response.status,
            "checksum": response.checksum
        })
    
    return results

# Usage
hooks = {
    "pre_write_hook1": "...code...",
    "pre_write_hook2": "...code...",
    "post_write_hook": "...code..."
}
batch_update_hooks(hooks)
```

---

## Troubleshooting

### Issue: "Cannot write to protected file"

**Cause:** Not using atlas_gate.write
**Solution:** Use `atlas_gate.write()` tool

### Issue: "Unauthorized path"

**Cause:** Path not in allowed locations
**Solution:** Check if path is protected system path

### Issue: "Invalid syntax"

**Cause:** Content has syntax errors
**Solution:** Validate content before writing

### Issue: "Permission denied"

**Cause:** File mode or user permissions
**Solution:** Check user authorization level

---

## Summary

| Aspect | Details |
|--------|---------|
| **Tool** | atlas_gate.write (write_file) |
| **Use For** | ALL file modifications to protected paths |
| **Protected Paths** | /etc/windsurf/*, /usr/local/share/windsurf-hooks/* |
| **Parameters** | path (required), content (required), mode (optional), encoding (optional) |
| **Returns** | status, checksum, timestamp |
| **Audit** | All operations logged |
| **Authorization** | Requires valid Windsurf session |

**Only atlas_gate.write is authorized. All direct writes are blocked.**
