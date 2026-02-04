# Workflow: /pre-pr-review

**Purpose:** Self-review before opening PR to catch issues early and ensure all quality requirements met.

**Prerequisites:** Feature/fix/refactoring complete, local tests passing.

**Inputs:** None (self-review before PR submission).

---

## Comprehensive Pre-PR Review Checklist

### Code Quality

- [ ] **No placeholders:** `git diff HEAD | grep -E "TODO|FIXME|stub|mock|placeholder|pass|return null"` returns nothing
- [ ] **Lint passes:** `npm run lint` with 0 errors, 0 warnings
- [ ] **Typecheck passes:** `npm run typecheck` with 0 errors
- [ ] **Format consistent:** `npm run format` makes no changes (code already formatted)
- [ ] **No dead code:** Removed unused imports, unused variables, dead branches
- [ ] **No console.log:** Replaced with structured logger, except during debug

### Testing

- [ ] **Unit tests pass:** `npm test -- --testNamePattern="unit"` 100% passing
- [ ] **Integration tests pass:** `npm test -- --testNamePattern="integration"` 100% passing
- [ ] **All tests pass:** `npm test` 100% passing, no skipped tests
- [ ] **Coverage ≥80%:** `npm test -- --coverage` shows ≥80% across all metrics
- [ ] **Minimal repro test added:** For bugfixes, test reproduces original issue
- [ ] **Edge cases tested:** Empty input, null, boundary values, invalid input
- [ ] **Error paths tested:** Each error condition has explicit test
- [ ] **No flaky tests:** Tests are deterministic (not timing-dependent)

### Documentation

- [ ] **Module docstring:** Every module has docstring explaining purpose, key types, usage
- [ ] **Function docstrings:** Every non-trivial function documented (purpose, params, returns, errors, tradeoffs)
- [ ] **Inline comments:** Complex logic explained (why, not just what)
- [ ] **Error handling documented:** Every error type and how handled
- [ ] **Design decisions documented:** DECISION/WHY/ALTERNATIVES/REASON in comments
- [ ] **No misleading comments:** Comments match code (not stale)
- [ ] **Terminology consistent:** Same terms used throughout (e.g., userId vs user_id)
- [ ] **Security-relevant logic commented:** Why certain checks are in place

### Logging & Observability

- [ ] **Structured logging:** All significant operations log JSON with required fields
- [ ] **Correlation IDs:** Request/span IDs propagated through call chain
- [ ] **Secrets redacted:** Passwords, tokens, API keys not logged (`[REDACTED]`)
- [ ] **PII not logged:** Email, phone, SSN not logged (except on allowlist)
- [ ] **Error context:** Error logs include errorCode, message, stack, context
- [ ] **Debug hooks:** Feature flags or log-level overrides available
- [ ] **No over-logging:** Doesn't log too much (excessive noise)
- [ ] **No under-logging:** Logs enough to debug production issues

### Security

- [ ] **Secrets not in code:** No hard-coded API keys, passwords, tokens
- [ ] **Secrets from env vars:** All secrets loaded from environment/vault
- [ ] **Input validation:** All external input validated (type, format, length, format)
- [ ] **Output encoding:** User input encoded when displayed (HTML, URL, JSON)
- [ ] **SQL injection prevention:** All queries parameterized or use ORM
- [ ] **SSRF protection:** URLs validated (deny private IPs, cloud metadata)
- [ ] **CSRF protection:** State-changing requests have CSRF tokens
- [ ] **No custom crypto:** Uses standard libraries only (no rolling own encryption)
- [ ] **Passwords hashed:** Uses bcrypt, not plain text
- [ ] **JWT short-lived:** Access tokens <30 min, refresh tokens in httpOnly cookies
- [ ] **Dependency audit:** `npm audit` clean, `npx snyk test` clean
- [ ] **License compliance:** No GPL/AGPL dependencies (unless acceptable)
- [ ] **No sensitive data in URLs:** Query params don't include PII or secrets

### Error Handling

- [ ] **All error paths handled:** No silent failures (catch without handling)
- [ ] **Explicit error types:** Domain-specific error classes (not generic Error)
- [ ] **User-facing messages:** Error messages are non-technical, actionable
- [ ] **Error codes:** Machine-readable error codes for client handling
- [ ] **Error context:** Errors include relevant context (user ID, resource ID, attempt count)
- [ ] **Stack traces logged:** Full stack traces in logs (not displayed to user)
- [ ] **No error swallowing:** Doesn't catch and ignore errors silently

### Dependencies & Configuration

- [ ] **No new vulnerabilities:** `npm audit` shows 0 vulnerabilities
- [ ] **Dependencies pinned:** Versions pinned or range specified (not `*`)
- [ ] **License compliant:** All licenses checked (no unacceptable licenses)
- [ ] **Configuration documented:** Environment variables documented (required, defaults, valid values)
- [ ] **Config loaded:** All required config validated at startup (fails fast)
- [ ] **No hard-coded values:** Configuration externalized (env vars, config files)

### Breaking Changes

- [ ] **No breaking changes:** OR clearly documented with migration guide
- [ ] **API compatibility:** Existing clients continue to work
- [ ] **Database backward compatibility:** Schema changes are backward compatible
- [ ] **Deprecation period:** Old API versions supported for reasonable time
- [ ] **Migration guide:** If breaking, guide provided for upgrading

### Performance

- [ ] **No performance regression:** Benchmarks show no slowdown (or improvement)
- [ ] **Appropriate complexity:** Algorithm complexity reasonable for input size
- [ ] **No N+1 queries:** Database queries don't scale badly with data size
- [ ] **Appropriate caching:** Expensive operations cached (if applicable)
- [ ] **Resource cleanup:** Connections closed, files handled, memory released
- [ ] **No memory leaks:** Tools like `clinic.js` show no leaks

### Files & Version Control

- [ ] **Only necessary files modified:** No unrelated changes
- [ ] **Commit messages clear:** Describe what changed and why (not just "fix bug")
- [ ] **Commit history clean:** Logical commits (not 50 WIP commits)
- [ ] **No merge conflicts:** All conflicts resolved correctly
- [ ] **No sensitive files committed:** No .env, secrets, credentials in git
- [ ] **Unnecessary files not added:** No node_modules, dist, build/ in git

### Accessibility & Usability

- [ ] **Accessible:** UI changes include proper ARIA labels, semantic HTML
- [ ] **No hardcoded strings:** User-facing text externalized (i18n)
- [ ] **Responsive:** Works on mobile, tablet, desktop
- [ ] **Keyboard navigable:** All functionality accessible via keyboard
- [ ] **Error messages clear:** Help users understand what went wrong

---

## Pre-PR Review Checklist (Automated)

Run this script before opening PR:

```bash
#!/bin/bash
set -e

echo "=== Pre-PR Review Checklist ==="

echo "1. Lint..."
npm run lint || exit 1

echo "2. Format check..."
npm run format --check || exit 1

echo "3. Typecheck..."
npm run typecheck || exit 1

echo "4. Tests..."
npm test -- --coverage || exit 1

echo "5. Placeholder scan..."
npm run check:placeholders || exit 1

echo "6. Security scan..."
npm audit --audit-level moderate || exit 1

echo "7. Check for console.log..."
git diff HEAD | grep -E "^\+.*console\.(log|warn|error)" && echo "ERROR: console.log found" && exit 1

echo "8. Check for hard-coded secrets..."
git diff HEAD | grep -E "password|secret|token|api.?key" | grep -v test | grep -v mock && echo "ERROR: Potential secret found" && exit 1

echo ""
echo "✓ All pre-PR checks passed!"
echo ""
echo "Next: Review checklist above manually, then open PR"
```

Save as `scripts/pre-pr-check.sh`, run before PR:

```bash
chmod +x scripts/pre-pr-check.sh
./scripts/pre-pr-check.sh
# If all pass: git push, open PR
```

---

## Manual Review Questions

Before opening PR, ask yourself:

1. **Would I be comfortable deploying this to production right now?** (No "wait, let me fix this first")
2. **If this breaks in production, can I debug it quickly?** (Is logging comprehensive?)
3. **If a colleague needs to understand this code in 6 months, can they?** (Is documentation sufficient?)
4. **Did I test the happy path, error paths, and edge cases?** (Not just "seems to work")
5. **Is there any code I'm embarrassed to show a senior engineer?** (Fix it before PR)
6. **Are there any "temporary" hacks or workarounds?** (Remove them before PR)
7. **Did I introduce any security issues?** (Validated input, escaped output, no secrets?)
8. **Will this PR break existing clients?** (Do they still work? Any migration needed?)

---

## Final Checks Before Pushing

```bash
# Final lint
npm run lint --fix

# Final test
npm test -- --coverage

# Check git status
git status

# Review diff
git diff HEAD

# Stage changes
git add .

# Verify changes are correct
git diff --cached

# Commit with clear message
git commit -m "feat/fix/refactor: <title>

<Detailed explanation of what changed and why>

Fixes #<issue-id> (if applicable)"

# Push
git push origin <branch>

# Now open PR on GitHub with link to docs/changes/<id>.md or docs/bugfixes/<id>.md
```

---

## PR Description Template

When opening PR on GitHub, include:

```markdown
## Description
<Brief description of changes>

## Type of Change
- [ ] Feature (new functionality)
- [ ] Bugfix (fixes issue #<issue-id>)
- [ ] Refactor (improves code, no behavior change)
- [ ] Dependency upgrade
- [ ] Security hardening
- [ ] Documentation

## Changes
- File1.ts: <what changed>
- File2.ts: <what changed>
- File3.test.ts: <what changed>

## Testing
- [ ] Unit tests: All passing (count: <X>/< X>)
- [ ] Integration tests: All passing (count: <X>/<X>)
- [ ] Coverage: <X>% (threshold: 80%)
- [ ] Manual testing: <describe>

## Security
- [ ] No secrets in code
- [ ] Input validation present
- [ ] No SQL injection vectors
- [ ] npm audit: Clean

## Deployment Impact
- Database migrations: <Yes/No>
- Breaking changes: <Yes/No>
- Backward compatibility: <Full/Partial/None>

## Audit Summary
See `docs/changes/<issue-id>.md` or `docs/bugfixes/<issue-id>.md`

## Related Issues
Fixes #<issue-id>
```

---

## Success Criteria

- [ ] All automated checks passing (lint, typecheck, tests, security)
- [ ] All manual checklist items complete
- [ ] No placeholders, TODOs, or temporary hacks
- [ ] Documentation complete
- [ ] Security verified
- [ ] Tests comprehensive
- [ ] Commit messages clear
- [ ] PR description complete
- [ ] Ready for code review

---

## Related Workflows

- /implement-feature (includes pre-PR review)
- /fix-bug (includes pre-PR review)
- /refactor-module (includes pre-PR review)
