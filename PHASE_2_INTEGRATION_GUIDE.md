# Phase 2 Integration Guide

**For**: DevOps Engineers, System Administrators, and Platform Engineers  
**Purpose**: Deploy and verify Phase 2 language support in production

---

## Quick Overview

Phase 2 adds enforcement for 4 enterprise languages:
- **Java** (via public/private method detection + JavaDoc)
- **C/C++** (via function definition detection + Doxygen)
- **Go** (via exported function detection + Go-style comments)
- **Rust** (via fn definition detection + doc comments)

Both completeness and documentation enforcement are active.

---

## Pre-Deployment Checklist

- [ ] Python 3.6+ installed on Windsurf servers
- [ ] Hooks deployed to `/etc/windsurf/hooks/` (or configured path)
- [ ] Policy file at `/etc/windsurf/policy/policy.json`
- [ ] Backup of existing hook files
- [ ] Test environment available for validation
- [ ] Rollback plan in place

---

## Files to Deploy

### Core Hooks (Required)
1. **pre_write_completeness.py**
   - Size: ~12 KB
   - MD5: Check against source
   - Permissions: 755
   - Deploy to: `/etc/windsurf/hooks/pre_write_completeness.py`

2. **pre_write_comprehensive_comments.py**
   - Size: ~18 KB
   - MD5: Check against source
   - Permissions: 755
   - Deploy to: `/etc/windsurf/hooks/pre_write_comprehensive_comments.py`

### Test Files (Optional but Recommended)
- `tests/test-phase2-languages.sh` (200 lines, 755 permissions)
- Deploy to: `/opt/testing/test-phase2-languages.sh`

### Documentation (Reference)
- `PHASE_2_IMPLEMENTATION.md`
- `PHASE_2_QUICK_START.md`
- Deploy to: `/opt/docs/` or internal wiki

---

## Deployment Procedure

### Step 1: Backup Existing Hooks
```bash
mkdir -p /backups/windsurf-hooks-pre-phase2/
cp /etc/windsurf/hooks/pre_write_*.py /backups/windsurf-hooks-pre-phase2/
ls -la /backups/windsurf-hooks-pre-phase2/
```

### Step 2: Deploy New Hooks
```bash
# Copy Phase 2 hooks
cp windsurf-hooker/windsurf-hooks/pre_write_completeness.py /etc/windsurf/hooks/
cp windsurf-hooker/windsurf-hooks/pre_write_comprehensive_comments.py /etc/windsurf/hooks/

# Verify permissions
chmod 755 /etc/windsurf/hooks/pre_write_completeness.py
chmod 755 /etc/windsurf/hooks/pre_write_comprehensive_comments.py

# Verify deployment
ls -la /etc/windsurf/hooks/pre_write_*.py
```

### Step 3: Deploy Test Suite (Optional)
```bash
mkdir -p /opt/testing/
cp windsurf-hooker/tests/test-phase2-languages.sh /opt/testing/
chmod 755 /opt/testing/test-phase2-languages.sh
```

### Step 4: Verify Python Syntax
```bash
# Each hook must compile without errors
python3 -m py_compile /etc/windsurf/hooks/pre_write_completeness.py
python3 -m py_compile /etc/windsurf/hooks/pre_write_comprehensive_comments.py

# Both should print nothing (exit 0)
echo "✓ Syntax validation complete"
```

### Step 5: Configure Policy
Update `/etc/windsurf/policy/policy.json`:

```json
{
  "version": "2.0",
  "execution_profile": "standard",
  "phase": 2,
  "supported_languages": [
    "python",
    "javascript",
    "java",
    "cpp",
    "c",
    "go",
    "rust"
  ],
  "hooks": {
    "pre_write": [
      "pre_write_completeness.py",
      "pre_write_comprehensive_comments.py"
    ]
  },
  "enforcement_level": "strict"
}
```

**Key Fields**:
- `phase`: Set to 2 for Phase 2 enforcement
- `execution_profile`: "standard" for normal mode, "locked" for emergency lock
- `hooks.pre_write`: Order matters (completeness first, then comments)
- `enforcement_level`: "strict" blocks all violations, "warning" logs only

---

## Post-Deployment Validation

### Test 1: Run Test Suite
```bash
/opt/testing/test-phase2-languages.sh

# Expected output:
# === Phase 2 Language Support Tests ===
# Total: 13 | Passed: 13 | Failed: 0
```

**Success Criteria**: All 13 tests must pass (exit 0)

### Test 2: Manual Hook Test (Java)
```bash
cat > /tmp/java_test.java <<'EOF'
public class Test {
    public void doWork() {
        System.out.println("working");
    }
}
EOF

python3 << 'PYEOF'
import json
code = open('/tmp/java_test.java').read()
payload = {
    'tool_info': {
        'edits': [{
            'path': 'Test.java',
            'new_string': code
        }]
    }
}
with open('/tmp/payload.json', 'w') as f:
    json.dump(payload, f)
PYEOF

# Should be blocked (missing docstring)
cat /tmp/payload.json | python3 /etc/windsurf/hooks/pre_write_comprehensive_comments.py
# Expected: exit 2, error message about missing docstring
```

### Test 3: Manual Hook Test (Go)
```bash
cat > /tmp/go_test.go <<'EOF'
package main

// MyFunc does something important
func MyFunc() {
    println("working")
}
EOF

python3 << 'PYEOF'
import json
code = open('/tmp/go_test.go').read()
payload = {
    'tool_info': {
        'edits': [{
            'path': 'test.go',
            'new_string': code
        }]
    }
}
print(json.dumps(payload))
PYEOF | python3 /etc/windsurf/hooks/pre_write_completeness.py

# Should succeed (no TODOs, exit 0)
```

### Test 4: Check Hook Integration
```bash
# Verify hooks are loaded in Windsurf configuration
grep -r "pre_write_completeness" /etc/windsurf/ || echo "Not found"
grep -r "pre_write_comprehensive_comments" /etc/windsurf/ || echo "Not found"

# Check system logs for hook execution
journalctl -n 20 | grep -i "windsurf\|hook" || echo "No recent logs"
```

---

## Monitoring and Troubleshooting

### Enable Debug Logging
In `/etc/windsurf/policy/policy.json`, add:
```json
{
  "debug": true,
  "log_level": "DEBUG",
  "log_file": "/var/log/windsurf/hooks.log"
}
```

### Check Hook Execution
```bash
tail -f /var/log/windsurf/hooks.log | grep -E "pre_write_|BLOCKED|Language"
```

### Common Issues

#### Issue 1: "Hook not found"
**Cause**: File not in correct path  
**Fix**: Verify deployment:
```bash
ls -la /etc/windsurf/hooks/pre_write_*.py
```

#### Issue 2: "python3: No module named 'json'"
**Cause**: Python 3 not installed or wrong path  
**Fix**: Verify Python installation:
```bash
python3 --version  # Should be 3.6+
which python3      # Should be /usr/bin/python3
```

#### Issue 3: "Permission denied"
**Cause**: Hook file not executable  
**Fix**: Fix permissions:
```bash
chmod 755 /etc/windsurf/hooks/pre_write_*.py
```

#### Issue 4: Too many false positives
**Cause**: Inline comment threshold too low, or code blocks misidentified  
**Fix**: Adjust threshold in pre_write_comprehensive_comments.py:
```python
# Line ~345: Change from > 8 to > 10 or > 12
if code_lines > 10 and comment_lines == 0:
```

---

## Rollback Procedure

If issues occur, quickly rollback to pre-Phase2:

```bash
# Option 1: Restore from backup
cp /backups/windsurf-hooks-pre-phase2/* /etc/windsurf/hooks/

# Option 2: Revert policy
sed -i 's/"phase": 2/"phase": 1/' /etc/windsurf/policy/policy.json

# Option 3: Enable panic button (immediate lock)
# In policy.json, set: "execution_profile": "locked"

# Verify rollback
ls -la /etc/windsurf/hooks/pre_write_*.py
cat /etc/windsurf/policy/policy.json | grep phase
```

---

## Performance Considerations

### Hook Execution Time
- **pre_write_completeness.py**: ~50-100ms per file
- **pre_write_comprehensive_comments.py**: ~100-200ms per file
- **Total**: ~150-300ms for both hooks

### Typical Windsurf Workflow
```
User types code: 0-500ms
Hooks run: 150-300ms (parallel if possible)
File write: 50ms
Total perceived latency: 200-350ms (acceptable)
```

### Optimization Tips
1. Cache language detection (store in payload)
2. Skip validation for small files (<100 bytes)
3. Batch process multiple edits if possible
4. Consider async execution for large files

---

## Language Detection Reference

| Extension | Language | Phase |
|-----------|----------|-------|
| .java | Java | 2 ✅ |
| .cpp, .cc, .cxx, .c++ | C++ | 2 ✅ |
| .c | C | 2 ✅ |
| .go | Go | 2 ✅ |
| .rs | Rust | 2 ✅ |
| .cs | C# | 3 🔄 |
| .php | PHP | 3 🔄 |
| .swift | Swift | 3 🔄 |
| .kt, .kts | Kotlin | 3 🔄 |
| .rb | Ruby | 3 🔄 |
| .r, .R | R | 4 🔄 |
| .m | MATLAB | 4 🔄 |

---

## Documentation Resources

- **Quick Start**: `windsurf-hooker/PHASE_2_QUICK_START.md`
- **Full Implementation**: `PHASE_2_IMPLEMENTATION.md`
- **Architecture**: `ENFORCEMENT_ARCHITECTURE.md`
- **API Reference**: `ENFORCEMENT_REFERENCE.md`

---

## Support and Escalation

### For Issues
1. Check troubleshooting section above
2. Review `/var/log/windsurf/hooks.log`
3. Run test suite: `/opt/testing/test-phase2-languages.sh`
4. Review relevant documentation

### For Feedback
- Report false positives with code samples
- Request new language support
- Suggest pattern improvements
- Document edge cases

### Emergency Procedures
1. Activate panic button: Set `execution_profile: locked` in policy.json
2. All code writes blocked immediately
3. Contact administrator for unlock
4. Investigate issues before re-enabling

---

## Success Criteria Checklist

After deployment:
- [ ] Test suite runs (13/13 passing)
- [ ] Manual hooks test succeeds
- [ ] No Python syntax errors
- [ ] Policy file correctly configured
- [ ] Permissions set to 755
- [ ] Language detection works for Java, C++, Go, Rust
- [ ] Completeness enforcement active
- [ ] Documentation enforcement active
- [ ] Hook execution logs present
- [ ] No file write delays (< 500ms added)

---

## Deployment Complete ✅

When all checks pass, document:
- Date deployed
- Deployer name
- Verified test results
- Any configuration changes
- Rollback timestamp (if needed)

```bash
echo "Phase 2 deployment completed: $(date)" >> /var/log/windsurf/deployment.log
```

---

## Next Steps

### Immediate
- Monitor hook execution and logs
- Collect feedback from developers
- Address false positives

### Short-term (1-2 weeks)
- Analyze usage patterns
- Optimize performance if needed
- Document edge cases

### Medium-term (1-2 months)
- Begin Phase 3 implementation (C#, PHP, Swift, Kotlin, Ruby)
- Expand documentation coverage
- Add code quality checks

### Long-term (3+ months)
- Implement Phase 4 (R, MATLAB)
- Add advanced checks (complexity, type safety)
- Integrate with ATLAS-GATE fully
