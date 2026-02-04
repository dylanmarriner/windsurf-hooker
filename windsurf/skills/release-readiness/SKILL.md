---
name: release-readiness
description: Prepare releases with migration safety, artifact integrity checks, and verified rollback capability. Invoke as @release-readiness.
---

# Skill: Release Readiness

## Purpose
Before releasing to production, ensure the release is reproducible, verifiable, safe to rollback, and won't break user data or integrations.

## When to Use This Skill
- Preparing for a release (before pushing to prod)
- Tagging a version
- Packaging artifacts for distribution
- Verifying rollback capability

## Steps

### 1) Version and changelog
- Update version numbers (semantic versioning)
- Write release notes with:
  - New features
  - Bug fixes
  - Breaking changes (if any)
  - Migration instructions (if needed)
  - Known issues or workarounds

### 2) Migration safety
- Identify any database schema changes
- Ensure forward and backward compatibility
- Document rollback instructions
- For irreversible migrations, add a feature flag or deprecation period

Example:
```sql
-- Forward migration: add new column with default
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Backward compatible: old code still works
-- New code uses last_login_at
-- Rollback: DROP COLUMN last_login_at (clean)
```

### 3) Artifact integrity
- Build release artifacts deterministically
- Generate SHA256 checksums for all artifacts
- Record build environment and commit SHA

```bash
bash scripts/ci/package_artifacts.sh
bash scripts/ci/generate_checksums.sh dist

# Verify checksums
sha256sum -c dist/SHA256SUMS.txt
```

### 4) Smoke verification
Run minimal end-to-end tests:
- Health checks pass
- Key user flows work
- Observability signals are present (logs, metrics)
- No startup errors

Example:
```bash
# Start the service
./dist/app &
APP_PID=$!

# Verify health endpoint
curl -f http://localhost:8000/health || exit 1

# Verify a key endpoint
curl -f http://localhost:8000/api/version || exit 1

# Stop the service
kill $APP_PID
```

### 5) Release notes and communication
- Draft release notes with features, fixes, migration info
- Include verification evidence
- Include rollback steps
- Identify any teams that need to be notified

### 6) Artifact upload and tagging
- Upload artifacts to artifact repository
- Tag the git commit with version
- Ensure tag signature is verified (GPG sign if possible)

```bash
git tag -s v1.2.3 -m "Release v1.2.3: new features"
git push origin v1.2.3
```

### 7) Deployment verification
After deploying to production:
- Verify all health checks pass
- Verify structured logs are present
- Verify metrics are recording
- Run a quick smoke test in prod
- Monitor error rates and latency for 5-10 minutes

### 8) Rollback preparation
Ensure rollback is safe and documented:
- Previous version is available and tagged
- Rollback instructions are clear
- Rollback has been tested (in staging if possible)
- Rollback plan is documented in runbooks

Example:
```markdown
## Rollback Steps
1. Identify current version: `git describe --tags`
2. Identify previous version: `git tag | sort -V | tail -2`
3. Deploy previous version: `deploy v1.2.2`
4. Verify health checks pass in production
5. Monitor error rates for 5 minutes
```

## Quality Checklist

- [ ] Version is updated (semantic versioning)
- [ ] Release notes are written with breaking changes noted
- [ ] Migration safety is verified (forward/backward compatible)
- [ ] Artifacts are built deterministically
- [ ] Checksums are generated and verified
- [ ] Smoke tests pass
- [ ] All quality gates pass (tests, lint, security audit)
- [ ] Rollback procedure is documented and tested
- [ ] Deployment verification steps are identified

## Verification Commands

```bash
# Build artifacts deterministically
npm run build
bash scripts/ci/package_artifacts.sh

# Verify checksums
bash scripts/ci/generate_checksums.sh dist
sha256sum -c dist/SHA256SUMS.txt

# Generate changelog
bash scripts/ci/generate_changelog.sh > CHANGELOG.tmp

# Run smoke tests
bash scripts/ci/run_if_present.sh smoke:test

# Verify no untracked changes
git status --porcelain
```

## How to Recover if Release Fails

If a release has issues:
1. Do not push to production
2. Fix the issue in a commit
3. Update the version number (v1.2.3 → v1.2.4)
4. Re-run verification steps
5. Try again

If a release is deployed and breaks:
1. Follow the rollback procedure
2. Deploy the previous version
3. Verify health checks and metrics
4. Create a post-mortem
5. Add a regression test to prevent recurrence

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: Release version, changed modules
- **Verification**: Include artifact hashes, smoke test results, migration safety confirmation
- **Results**: Rollback procedure verified, all gates pass
- **Risk Notes**: Any breaking changes, deprecations, or migration concerns
