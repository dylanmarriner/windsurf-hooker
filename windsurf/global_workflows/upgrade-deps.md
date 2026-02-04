# Workflow: /upgrade-deps

**Purpose:** Upgrade dependencies safely: check for breaking changes, test compatibility, and verify security.

**Prerequisites:** Dependency to upgrade identified.

**Inputs:**
- Package name: `<package-name>`
- Current version: `<current-version>`
- Target version: `<target-version>`

---

## Steps

### 1. Check Breaking Changes
```bash
# Read CHANGELOG for target version
npm view <package-name>@<target-version>
# or visit https://www.npmjs.com/package/<package-name>/v/<target-version>

# Check for breaking changes
cat node_modules/<package-name>/CHANGELOG.md | grep -A 20 "<target-version>"

# Document breaking changes found
```

### 2. Check for Security Vulnerabilities
```bash
# In current version
npm audit

# After upgrade (simulate)
npm install --save <package-name>@<target-version>
npm audit
```

If new vulnerabilities introduced, consider staying on current version or waiting for patch.

### 3. Create Feature Branch
```bash
git checkout -b deps/upgrade-<package-name>-to-<target-version>
```

### 4. Upgrade Dependency
```bash
npm install <package-name>@<target-version>
# or if using yarn/pnpm
yarn upgrade <package-name>@<target-version>
pnpm update <package-name>@<target-version>
```

### 5. Handle Breaking Changes
If breaking changes exist, update code:

```typescript
// Example: Library API changed
// Old:
const instance = new Package({ option: true });

// New (in v2.0.0):
const instance = new Package({ enabled: true }); // option → enabled

// Update all usages:
// 1. Grep for old API
grep -r "option:" src/ | grep Package

// 2. Replace with new API
// 3. Run tests to verify
```

### 6. Run Full Test Suite
```bash
npm run lint
npm run typecheck
npm test -- --coverage
npm audit

# All must pass
```

### 7. Integration Testing
If upgrading critical dependency, test in staging:

```bash
npm run build
npm start

# Manual testing:
# - Test core workflows (auth, payment, etc.)
# - Verify no errors in logs
# - Check performance is acceptable
```

### 8. Create Audit Summary
Document: `docs/deps/upgrade-<package-name>.md`

```markdown
## Dependency Upgrade: <Package>
**From:** <current-version>
**To:** <target-version>
**Author:** <your-name>
**Date:** <date>

### Reason for Upgrade
- Security patch: <details>
- Performance improvement: <details>
- New features needed: <details>
- Dependency of our dependency: <details>

### Breaking Changes
1. API change: `option` → `enabled`
   - Affected files: src/config.ts, src/__tests__/config.test.ts
   - Updated: Yes ✓

2. Default behavior change: <change>
   - Impact: <impact>
   - Mitigation: <mitigation>

### Security Impact
- Current version vulnerabilities: 0
- New version vulnerabilities: 0 ✓
- npm audit: Clean ✓

### Testing
- Unit tests: 127/127 passing ✓
- Integration tests: All passing ✓
- Staging deployment: Verified ✓
- Performance impact: No regression

### Rollback Plan
If issues occur in production:
```bash
npm install <package-name>@<current-version>
git push
# Deploy previous version
```

### Dependencies Affected
- <dependent-package-1>: No changes needed
- <dependent-package-2>: Requires version constraint update in package.json
```

### 9. Push & Open PR
```bash
git add package.json package-lock.json
git commit -m "deps: upgrade <package-name> from <current-version> to <target-version>

Reason: <reason for upgrade>

Breaking changes:
- API change: option → enabled (updated in src/config.ts)

Testing:
- All 127 tests passing
- Security scan: clean
- Staging tested: verified
- No regression in performance

See docs/deps/upgrade-<package-name>.md for full details."

git push origin deps/upgrade-<package-name>-to-<target-version>
```

### 10. Code Review
Reviewer verifies:
- [ ] Breaking changes identified and handled
- [ ] All tests passing
- [ ] No security vulnerabilities introduced
- [ ] Performance acceptable
- [ ] Rollback plan clear

### 11. Merge & Deploy
```bash
git checkout main
git pull
git merge deps/upgrade-<package-name>-to-<target-version>
git push origin main
```

---

## Success Criteria

- [ ] Breaking changes identified and handled
- [ ] All tests passing (no regression)
- [ ] Security scan clean (no new vulnerabilities)
- [ ] Performance acceptable (no regression)
- [ ] Audit summary documented
- [ ] Code review approved
- [ ] CI all green
- [ ] Rollback plan documented
- [ ] Merged and deployed

---

## Dependency Update Best Practices

### Frequency
- **Weekly:** Check for security updates (npm audit, npm outdated)
- **Monthly:** Update minor/patch versions (lower risk)
- **Quarterly:** Update major versions (requires breaking change handling)

### Caution with Major Versions
Major version upgrades often have breaking changes:
- Carefully read CHANGELOG
- Upgrade one at a time (not all at once)
- Test thoroughly before deploying
- Have rollback plan ready

### Lock Files
Always commit package-lock.json (or yarn.lock, pnpm-lock.yaml):
```bash
git add package.json package-lock.json
# Ensures reproducible installs
```

### npm audit
Regularly check for vulnerabilities:
```bash
npm audit                          # List vulnerabilities
npm audit --audit-level moderate  # Fail if moderate or worse
npm audit fix                       # Auto-fix (careful: may update versions)
npm audit fix --force             # Force fix (can introduce breaking changes)
```

---

## Related Skills & Workflows

- @secure-by-default (verify no security issues introduced)
- @test-engineering-suite (comprehensive tests before/after)
- @kaiza-mcp-ops (pre-flight checks before merge)
- /pre-pr-review (comprehensive code review)
