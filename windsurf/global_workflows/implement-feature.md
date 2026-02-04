# Workflow: /implement-feature

**Purpose:** Structured workflow for implementing a complete feature from requirement to production.

**Prerequisites:** Feature requirement documented, architecture reviewed if complex, effort estimated.

**Inputs:**
- Feature name: `<feature-name>`
- Issue ID: `<issue-id>`
- Description: `<brief description>`

---

## Steps

### 1. Understand Requirement & Design
```
[ ] Read issue/requirement fully
[ ] Identify affected modules
[ ] List data models/APIs that need changes
[ ] Document design (sketch, pseudocode, data flow)
[ ] Identify test scenarios
[ ] Confirm no blockers (API schemas, env setup, dependencies)
```

### 2. Set Up Local Environment
```bash
git checkout -b feat/<feature-name>
npm run lint
npm run typecheck
npm test
npm run security-scan
```

### 3. Implement Core Logic
Use skills:
- **@repo-understanding** (understand affected code)
- **@no-placeholders-production-code** (complete, functional code)
- **@audit-first-commentary** (detailed documentation)
- **@debuggable-by-default** (structured logging)
- **@secure-by-default** (input validation, secrets management)

### 4. Add Tests
Use skill: **@test-engineering-suite**
```
[ ] Unit tests for core logic (>60% of tests)
[ ] Integration tests for workflows (20-30% of tests)
[ ] Edge cases and error paths tested
[ ] Target ≥80% coverage
```

### 5. Verify Quality Gates (Local)
```bash
npm run lint --fix
npm run format
npm run typecheck
npm test -- --coverage
npm audit --audit-level moderate
npx snyk test
npm run check:placeholders
```

### 6. Create Audit Summary
Document: `docs/changes/<issue-id>.md`

```markdown
## Feature: <Feature Name>
**Issue:** #<issue-id>
**Author:** <your-name>
**Date:** <date>

### What Changed
- File1.ts: Added function X
- File2.ts: Refactored Y to use new API
- File3.test.ts: Added 12 tests

### Why
Requirement: User needs to be able to X because Y.

### Testing
- 12 unit tests (core logic)
- 2 integration tests (end-to-end workflows)
- Coverage: 87%
- All tests passing

### Security
- Input validated
- Secrets not committed
- No SQL injection vectors
- Dependency audit clean

### Deployment Impact
- Database migration: None
- API changes: New endpoint POST /api/feature-name
- Backward compatibility: Full
```

### 7. Push & Open PR
```bash
git add .
git commit -m "feat: <feature-name>

Implements feature X per #<issue-id>.

Changes:
- File1.ts: Added validateInput() function
- File2.test.ts: Added 12 tests

Testing:
- 12 unit tests passing
- 2 integration tests passing
- Coverage: 87%

See docs/changes/<issue-id>.md for detailed audit summary."

git push origin feat/<feature-name>
```

### 8. CI Verification
```
[ ] CI pipeline runs (ci.yml)
[ ] All checks pass: lint, typecheck, tests, security, coverage
[ ] Code review requested from team
```

### 9. Code Review
Reviewer verifies:
- [ ] Code is complete, no placeholders (@no-placeholders-production-code)
- [ ] Tests comprehensive (@test-engineering-suite)
- [ ] Comments explain intent and tradeoffs (@audit-first-commentary)
- [ ] Security best practices followed (@secure-by-default)
- [ ] Logging/observability in place (@debuggable-by-default)
- [ ] No breaking changes (unless documented)

### 10. Merge & Deploy
```bash
git checkout main
git pull
git merge feat/<feature-name>
git push origin main

# Verify deployment
curl https://api.example.com/health
```

---

## Success Criteria

- [ ] Feature requirement fully implemented
- [ ] All tests passing (unit, integration, smoke)
- [ ] Code review approved
- [ ] CI all green (lint, typecheck, tests, security, coverage)
- [ ] Audit summary documented
- [ ] No placeholders, TODOs, or stubs
- [ ] Detailed comments and docstrings present
- [ ] Logging and error handling comprehensive
- [ ] Security best practices verified
- [ ] Merged to main and deployed

---

## Related Skills & Workflows

- @repo-understanding (understand affected code)
- @no-placeholders-production-code (complete implementation)
- @audit-first-commentary (documentation)
- @test-engineering-suite (testing)
- @secure-by-default (security)
- @debuggable-by-default (logging)
- @kaiza-mcp-ops (file modifications, pre-flight checks)
- /pre-pr-review (comprehensive review before merge)
