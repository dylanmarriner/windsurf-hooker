# Enforcement System Protection

## Overview

The enforcement system itself is protected against tampering. All writes to system enforcement files are blocked unless they go through the authorized `atlas_gate.write` tool.

## Protected Paths (READ-ONLY)

The following system paths are protected:

```
/usr/local/share/windsurf-hooks/     (All 22 enforcement hooks)
/etc/windsurf/policy/                (Policy configuration)
/etc/windsurf/                        (All windsurf system config)
~/.local/share/windsurf-hooks/        (User-local hooks)
```

## Protection Mechanism

**Hook:** `pre_filesystem_write_enforcement_protection.py`

Executes **before any filesystem write** and checks:

1. Is the write going through `atlas_gate.write` tool?
2. Is the write targeting a protected path?

If both are true → write is allowed
If write targets protected path but NOT through atlas_gate.write → **HARD FAIL**, write blocked

## Enforcement

```
User tries to write to /etc/windsurf/policy/policy.json directly
        ↓
pre_filesystem_write_enforcement_protection.py runs
        ↓
Checks: Is tool_name == "atlas_gate.write"?
        ↓ NO
Checks: Is path in protected_paths?
        ↓ YES
HARD FAIL: Cannot write to protected enforcement system file
          All modifications must use atlas_gate.write tool
```

## How to Modify Enforcement System

Any modification to protected enforcement files MUST use the authorized method:

```
atlas_gate.write(
    path="/etc/windsurf/policy/policy.json",
    content=<new content>
)
```

The `atlas_gate.write` tool is the only authorized method for modifying:
- Enforcement hooks
- Policy configuration
- System-level windsurf settings

## Why Protection?

1. **Integrity** - Prevents accidental or malicious modification of enforcement rules
2. **Audit Trail** - All modifications tracked through atlas_gate.write
3. **Authorization** - Only authorized personnel can modify enforcement system
4. **Security** - Enforcement system cannot be weakened by unauthorized changes
5. **Consistency** - Ensures all systems use identical enforcement rules

## Direct Writes (BLOCKED)

These attempts will be blocked:

```bash
# Direct file write (BLOCKED)
echo "modified" > /etc/windsurf/policy/policy.json

# Direct file copy (BLOCKED)
cp policy.json /etc/windsurf/policy/policy.json

# Editor modification (BLOCKED)
vim /etc/windsurf/policy/policy.json

# Any other direct write method (BLOCKED)
```

## Authorized Modification (ALLOWED)

Only this method works:

```
atlas_gate.write(
    path="/etc/windsurf/policy/policy.json",
    content=<validated content>
)
```

Requirements for atlas_gate.write:
- Must be authorized user/process
- Must go through ATLAS-GATE authorization
- All changes audited
- Content validated before write
- Audit trail maintained

## Protected Files List

| Path | Protection | Type |
|------|-----------|------|
| `/usr/local/share/windsurf-hooks/*.py` | READ-ONLY | Enforcement hooks (22 files) |
| `/etc/windsurf/policy/policy.json` | READ-ONLY | Policy configuration |
| `/etc/windsurf/` | READ-ONLY | All windsurf config |
| `~/.local/share/windsurf-hooks/*.py` | READ-ONLY | User-local hooks |

## Failure Messages

If someone tries direct write:

```
BLOCKED: Enforcement system protection violation
  • HARD FAIL: Cannot write to protected enforcement system file: /etc/windsurf/policy/policy.json
              All modifications to enforcement system must use atlas_gate.write tool
```

## Hook Execution Order

```
pre_filesystem_write_enforcement_protection.py
        ↓ (Protection check)
[Other filesystem write hooks...]
        ↓
[Write proceeds only if all checks pass]
```

This hook runs **first** before any other filesystem write operations.

## Security Model

```
Untrusted/Unverified Write
        ↓
pre_filesystem_write_enforcement_protection.py
        ↓
Is it to protected path? YES
        ↓
Is it through atlas_gate.write? NO
        ↓
BLOCKED ✗

Trusted Write through atlas_gate.write
        ↓
pre_filesystem_write_enforcement_protection.py
        ↓
Is it to protected path? YES
        ↓
Is it through atlas_gate.write? YES
        ↓
ALLOWED ✓
```

## Impact on Users

1. **Cannot directly modify** `/etc/windsurf/policy/policy.json`
2. **Cannot directly modify** `/usr/local/share/windsurf-hooks/`
3. **Cannot modify enforcement rules** without authorization
4. **Must use atlas_gate.write** for any enforcement system changes

## Policy Updates

To update policy:

```
# Request change through atlas_gate.write
# All changes audited and logged
# Cannot bypass protection
```

To update hooks:

```
# Request through atlas_gate.write
# All versions tracked
# Cannot bypass protection
```

## System Integrity

The enforcement system cannot be weakened because:

- ✓ All enforcement files protected
- ✓ Direct writes blocked
- ✓ Only authorized method: atlas_gate.write
- ✓ All changes audited
- ✓ No bypass possible

This ensures the enforcement system itself remains secure and unchanged unless explicitly authorized.
