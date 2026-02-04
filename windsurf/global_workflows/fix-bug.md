# Workflow: /fix-bug

**Purpose:** Fix a bug with confidence: reproduce, isolate, fix, verify, and prevent recurrence.

**Prerequisites:** Bug reported with description, ideally steps to reproduce.

**Inputs:**
- Bug ID: `<bug-id>`
- Title: `<bug-title>`
- Steps to reproduce: `<steps>`

---

## Steps

### 1. Understand the Bug
```
[ ] Read bug report thoroughly
[ ] Identify affected module(s)
[ ] Understand expected behavior vs actual behavior
[ ] Classify severity (critical, high, medium, low)
[ ] Confirm bug still reproduces in latest code
```

### 2. Create Minimal Repro Test
**Before fixing, write a test that reproduces the bug.**

```typescript
test("repro: issue #<bug-id> - <bug-title>", () => {
  // This test should FAIL with current code
  // It will PASS once the bug is fixed
  const result = buggyFunction(input);
  expect(result).toEqual(expectedValue);
  // Currently fails with: actual value is different
});
```

Verify test fails:
```bash
npm test -- --testNamePattern="issue #<bug-id>"
# Should see: FAIL (this is expected)
```

### 3. Investigate Root Cause
Use skill: **@debuggable-by-default**
- Review error logs for context
- Check correlation IDs for full request trace
- Review observability pack data (metrics, traces)
- Inspect related code
- Debug locally if needed

### 4. Fix the Bug
Use skills:
- **@no-placeholders-production-code** (complete fix, not workaround)
- **@audit-first-commentary** (document why bug occurred)
- **@secure-by-default** (ensure fix doesn't introduce security issues)

### 5. Verify Minimal Repro Test Passes
```bash
npm test -- --testNamePattern="issue #<bug-id>"
# Should see: PASS
```

### 6. Run Full Test Suite
```bash
npm test -- --coverage
# All tests must pass
# Coverage must not decrease
```

### 7. Add Regression Tests
Add additional tests to prevent bug from reoccurring:

```typescript
describe("<module> regression tests for bug #<bug-id>", () => {
  test("original issue: <title>", () => {
    // Original minimal repro test
  });

  test("related edge case 1", () => {
    // Related scenario that could hit same bug
  });

  test("related edge case 2", () => {
    // Another related scenario
  });
});
```

### 8. Create Audit Summary
Document: `docs/bugfixes/<bug-id>.md`

```markdown
## Bugfix: <Bug Title>
**Issue:** #<bug-id>
**Severity:** High
**Author:** <your-name>
**Date:** <date>

### What Was Broken
User reported: <description of issue>
Impact: <users affected, data loss, etc.>
Duration: <how long bug existed>

### Root Cause
<Explanation of why bug occurred>

Code location: src/auth/jwt.ts line 42
Old code:
```typescript
const decoded = jwt.verify(token, secret, { expiresIn: "5m" });
```

Why it was wrong: expiresIn should only be used in jwt.sign(), not jwt.verify()

### Fix Applied
New code:
```typescript
const decoded = jwt.verify(token, secret);
```

### Testing
- Minimal repro test: validates bug is fixed
- Regression tests: 3 additional tests prevent recurrence
- All tests passing: 127/127
- Coverage: 89% (same as before fix)

### Prevention
Added property-based tests to catch parameter misuse in JWT library.

### Verification
- Local: All tests pass
- CI: All gates pass
- Staging: Deployed and verified
```

### 9. Push & Open PR
```bash
git add .
git commit -m "fix: <bug-title> (#<bug-id>)

Root cause: <brief explanation>

Changes:
- src/auth/jwt.ts: Fixed JWT verification parameter misuse
- src/auth/jwt.test.ts: Added minimal repro test + 3 regression tests

Testing:
- Minimal repro test now passes
- All 127 tests passing
- No regression in coverage (still 89%)

Fixes #<bug-id>

See docs/bugfixes/<bug-id>.md for full analysis."

git push origin fix/<bug-id>
```

### 10. Code Review
Reviewer verifies:
- [ ] Root cause correctly identified
- [ ] Minimal repro test included
- [ ] Regression tests comprehensive
- [ ] Fix doesn't introduce new bugs
- [ ] All tests passing
- [ ] Fix is minimal (not over-engineered)

### 11. Merge & Deploy
```bash
git checkout main
git pull
git merge fix/<bug-id>
git push origin main
```

---

## Success Criteria

- [ ] Bug reproduced and isolated
- [ ] Root cause identified and documented
- [ ] Minimal repro test created and passes after fix
- [ ] Regression tests added to prevent recurrence
- [ ] All tests passing (no regression)
- [ ] Audit summary documented
- [ ] Code review approved
- [ ] CI all green
- [ ] Merged to main and deployed

---

## Related Skills & Workflows

- @repo-understanding (locate affected code)
- @debuggable-by-default (use logs/traces to diagnose)
- @no-placeholders-production-code (complete fix)
- @audit-first-commentary (document root cause)
- @test-engineering-suite (regression tests)
- @secure-by-default (ensure fix is secure)
- @kaiza-mcp-ops (pre-flight checks before merge)
- /pre-pr-review (comprehensive review)
