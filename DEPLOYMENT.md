# Deployment Guide

## Installation

### Repo-Local Installation (Recommended)

Hooks are already present in `windsurf-hooks/` directory:

```bash
cd /path/to/windsurf-hooker
chmod +x windsurf-hooks/*.py
```

All hooks are executable and ready to use.

### User Installation

```bash
mkdir -p ~/.local/share/windsurf-hooks
cp windsurf-hooks/*.py ~/.local/share/windsurf-hooks/
chmod +x ~/.local/share/windsurf-hooks/*.py
```

### System Installation (requires sudo)

```bash
sudo mkdir -p /usr/local/share/windsurf-hooks
sudo cp windsurf-hooks/*.py /usr/local/share/windsurf-hooks/
sudo chmod +x /usr/local/share/windsurf-hooks/*.py
```

---

## Configuration

### Policy File

Location: `windsurf/policy/policy.json`

Contains:
- All prohibited patterns (15 languages)
- Language-specific test frameworks
- Language-specific linting tools
- Implementation requirements
- Performance constraints
- Quality standards

No additional configuration needed.

---

## Hook Integration

### Windsurf Integration

Hooks are automatically discovered from:
1. Repo-local: `./windsurf-hooks/`
2. User: `~/.local/share/windsurf-hooks/`
3. System: `/usr/local/share/windsurf-hooks/`

### Hook Execution Order

**Pre-Write Phase:**
1. `pre_write_code_policy.py` - Prohibitions & completeness
2. `pre_write_language_compliance.py` - Config presence
3. `pre_write_comprehensive_comments.py` - Documentation

**Post-Write Phase:**
1. `post_write_self_contained_enforcement.py` - Syntax & tests
2. `post_write_coverage_enforcement.py` - Test validation
3. `post_write_verify.py` - Final verification

---

## Verification

### List Installed Hooks

```bash
ls -la ~/.local/share/windsurf-hooks/
```

### Test Hook Syntax

```bash
python3 -m py_compile windsurf-hooks/*.py
```

### Verify Policy

```bash
python3 -c "import json; json.load(open('windsurf/policy/policy.json'))" && echo "✓ Policy valid"
```

---

## Active Enforcement

All 6 enforcement hooks are active:

### Pre-Write (Before Code Acceptance)

| Hook | File | Checks |
|------|------|--------|
| Code Policy | `pre_write_code_policy.py` | Prohibitions, empty code, logic preservation, error handling |
| Language Compliance | `pre_write_language_compliance.py` | Test & lint configs |
| Comments | `pre_write_comprehensive_comments.py` | Docstrings, comments, names |

### Post-Write (After Code Written)

| Hook | File | Checks |
|------|------|--------|
| Self-Contained | `post_write_self_contained_enforcement.py` | Syntax, test files, mocks, configs |
| Coverage | `post_write_coverage_enforcement.py` | Test functions, no mocks |
| Verify | `post_write_verify.py` | Final syntax & placeholder check |

---

## Requirements

- Python 3.8+
- No external dependencies (hooks are pure Python)
- Access to `windsurf/policy/policy.json`

---

## Enforcement Specifications

### 15 Languages Supported

Python, JavaScript, TypeScript, Java, C, C++, C#, Go, Rust, PHP, Ruby, Swift, Kotlin, R, MATLAB

### Zero-Tolerance Prohibitions

- TODO, FIXME, XXX, HACK, TEMP, dummy, null, placeholder, etc.
- Empty implementations, stubs, skeletons
- Mock/fake/stub code
- Commented-out logic
- Incomplete code

### Mandatory Requirements

- 100% real, working implementations
- Complete documentation (docstrings + WHY comments)
- All logic paths handled explicitly
- All dependencies real, explicit, pinned
- Error handling comprehensive and explicit
- All tests real (no mocks) with 100% coverage
- Strict linting and type checking

---

## Failure Handling

If any hook fails:

1. Code write is **rejected**
2. Error message displays violations
3. No code is committed
4. Developer must fix violations and resubmit

**Examples:**

```
BLOCKED: pre_write_code policy violation
  • HARD FAIL: Absolute prohibition 'TODO' found in src/api.py:42
  • HARD FAIL: Logic removal in src/handler.py (5 → 2 lines)
  • Missing error handling in src/utils.py function load_file
```

---

## Status Check

All hooks deployed and active:

```bash
✓ pre_write_code_policy.py (8.5 KB, executable)
✓ pre_write_language_compliance.py (5.1 KB, executable)
✓ pre_write_comprehensive_comments.py (21 KB, executable)
✓ post_write_self_contained_enforcement.py (11 KB, executable)
✓ post_write_coverage_enforcement.py (6.9 KB, executable)
✓ post_write_verify.py (5.1 KB, executable)
```

---

## Documentation

- **SPECIFICATION.md** - Core requirements
- **ENFORCEMENT_SPECIFICATION.md** - Complete 15-language spec
- **ENFORCEMENT_QUICK_REFERENCE.md** - Quick lookup
- **HARD_FAIL_CRITERIA.md** - Failure conditions
- **SELF_CONTAINED_ENFORCEMENT.md** - Hook-based enforcement
- **DEPLOYMENT.md** (this file)

---

## Support

All hooks are self-contained and require no external tools to function.

For issues with hook execution:

1. Check Python version (3.8+)
2. Verify hook files are executable: `chmod +x windsurf-hooks/*.py`
3. Check policy file exists: `cat windsurf/policy/policy.json`
4. Test hook syntax: `python3 -m py_compile windsurf-hooks/pre_write_code_policy.py`

