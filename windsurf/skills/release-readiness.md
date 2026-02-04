# Skill: @release-readiness

**Purpose:** Verify code is production-ready, changelog is accurate, versions are correct, and deployment will succeed without rollback.

**Invocation:** `/use-skill release-readiness` before creating releases or deploying to production.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Before any release (tag, publish, deploy).
- **Dependencies:** All other skills, @kaiza-mcp-ops.
- **Owner:** Release engineering team.

---

## Step-Based Instructions

### Step 1: Verify Code Quality

```bash
# All quality gates must pass
npm run lint
npm run typecheck
npm test -- --coverage

# Confirm all tests pass
npm test -- --testNamePattern=".*" --coverage

# Verify security scan is clean
npm audit --audit-level moderate
npx snyk test

# Placeholder scan (no TODOs in production code)
npm run check:placeholders
```

Document results:

```json
{
  "quality_gates": {
    "lint": { "status": "passed", "errors": 0, "warnings": 0 },
    "typecheck": { "status": "passed", "errors": 0 },
    "tests": { "status": "passed", "total": 127, "passed": 127, "coverage": 89 },
    "security_scan": { "status": "passed", "vulnerabilities": 0 },
    "placeholder_scan": { "status": "passed", "issues": 0 }
  }
}
```

### Step 2: Verify Version Numbers

```typescript
/**
 * Check that version numbers are correct and consistent.
 */

// Read current version
const packageVersion = require("./package.json").version;  // e.g., "1.2.3"
const cargoVersion = fs.readFileSync("Cargo.toml", "utf-8").match(/^version = "(.*)"$/m)?.[1];

// Verify version format is semantic
const isSemanticVersion = /^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$/.test(packageVersion);
if (!isSemanticVersion) {
  throw new Error(`Invalid semantic version: ${packageVersion}`);
}

// Verify version is greater than previous release
const previousVersion = "1.2.2";  // From git tag or npm registry
if (isVersionGreater(previousVersion, packageVersion)) {
  throw new Error(`Version ${packageVersion} must be > ${previousVersion}`);
}

// Document version change
const versionBump = {
  from: "1.2.2",
  to: "1.2.3",
  bump_type: "patch", // or "minor", "major"
  reason: "Bugfix: Fix JWT validation error handling",
};
```

### Step 3: Verify Changelog

```markdown
/**
 * Changelog must be complete and accurate.
 *
 * Format: Keep a CHANGELOG.md (follows https://keepachangelog.com/)
 */

# CHANGELOG.md

## [1.2.3] - 2026-01-15

### Added
- Structured logging for JWT validation (correlation IDs, error details)
- New error types for JWT validation (TOKEN_EXPIRED, INVALID_TOKEN, MALFORMED)

### Fixed
- Issue #456: JWT validation silently fails on malformed tokens (now throws clear error)
- Issue #789: Expired tokens missing context in error logs (now includes userId, attempt count)

### Changed
- JWT error handling refactored for consistency across all validation paths

### Security
- No known vulnerabilities in this release
- Dependency audit: All dependencies up-to-date

### Database
- No migrations required for this release

### Breaking Changes
- None

---

## [1.2.2] - 2026-01-10
...
```

Verification:
- [ ] CHANGELOG.md exists
- [ ] New version has a section in CHANGELOG
- [ ] All user-facing changes listed (features, bugfixes, breaking changes)
- [ ] All security-relevant changes noted
- [ ] All database migrations noted (if any)
- [ ] Date is current (or future for pre-release)
- [ ] Versions in CHANGELOG match package.json

```json
{
  "changelog_verification": {
    "file_exists": true,
    "format": "keepachangelog",
    "current_version_documented": true,
    "features_listed": 2,
    "bugfixes_listed": 2,
    "breaking_changes": 0,
    "security_notes": "dependency audit clean",
    "date_correct": true
  }
}
```

### Step 4: Verify No Breaking Changes (or document them)

```typescript
/**
 * Identify any changes that will break existing users.
 *
 * Breaking changes must be:
 * 1. Documented clearly in CHANGELOG
 * 2. Accompanied by migration guide (if complex)
 * 3. Announced in release notes
 * 4. Justified (why is this necessary?)
 */

// Example: API endpoint signature changed
const BREAKING_CHANGES = [
  {
    item: "API endpoint POST /api/users",
    old: "Returns { userId: string, email: string, created_at: string }",
    new: "Returns { id: string, email: string, createdAt: string }",
    migration: "Update client to use 'id' instead of 'userId', 'createdAt' instead of 'created_at'",
    justification: "Standardize naming conventions across all endpoints",
  },
];

// Document in CHANGELOG:
// ### Breaking Changes
// - API response field names changed: `userId` → `id`, `created_at` → `createdAt`
//   Migration: Update client code using these fields. See migration guide.

if (BREAKING_CHANGES.length > 0) {
  // If breaking changes exist:
  // 1. Bump major version (1.2.3 → 2.0.0)
  // 2. Include migration guide in release notes
  // 3. Consider deprecation period in previous version
  console.warn(`Found ${BREAKING_CHANGES.length} breaking changes. Bump major version.`);
}
```

### Step 5: Verify Deployment Impact Assessment

```json
{
  "deployment_impact": {
    "database_migrations": {
      "required": false,
      "details": "No schema changes in this release"
    },
    "feature_flags_needed": false,
    "rollout_strategy": "Blue-green deployment, no special handling needed",
    "rollback_plan": "git revert <commit>, redeploy previous version",
    "downtime_required": false,
    "configuration_changes": {
      "required": false,
      "env_vars": []
    },
    "monitoring_additions": [
      "Watch JWT validation error rate (should be <0.1%)",
      "Watch auth endpoint latency (should be <50ms p95)"
    ],
    "deployment_checklist": [
      "Run all tests in staging",
      "Deploy to staging first, verify endpoints",
      "Deploy to 10% of production (canary)",
      "Monitor error rates for 10 minutes",
      "Deploy to remaining 90% of production",
      "Verify health checks pass"
    ]
  }
}
```

### Step 6: Verify Documentation

```bash
# Ensure README is up-to-date
grep -i "installation\|usage\|getting started" README.md

# Ensure API docs are current (if applicable)
ls docs/API.md
grep -c "POST /api" docs/API.md  # Should match actual endpoints

# Ensure migration guide exists (if breaking changes)
ls docs/MIGRATION_v1_to_v2.md
```

Documentation checklist:
- [ ] README.md updated with latest version info
- [ ] Installation instructions accurate
- [ ] API documentation current (endpoints, parameters, responses)
- [ ] Migration guide exists (if breaking changes)
- [ ] Architecture documentation updated (if significant refactor)
- [ ] Contributing guidelines current

### Step 7: Verify Signatures & Checksums (for distributed releases)

```bash
# If releasing npm package:
npm pack  # Create tarball
shasum -a 256 my-app-1.2.3.tgz > my-app-1.2.3.tgz.sha256
cat my-app-1.2.3.tgz.sha256  # Publish with release

# If releasing Docker image:
docker build -t my-app:1.2.3 .
docker inspect my-app:1.2.3  # Get image digest (SHA256)
# Publish digest in release notes

# If releasing binary:
cargo build --release
shasum -a 256 target/release/my-app > my-app-1.2.3.sha256
```

Document in release notes:

```markdown
## Signatures

### SHA-256 Checksums

```
abc123def456...  my-app-1.2.3.tgz
```

To verify:
```bash
shasum -a 256 -c my-app-1.2.3.tgz.sha256
```

### Docker Image

Image digest: sha256:abc123def456...
```

### Step 8: Create Release Notes

```markdown
# Release Notes: v1.2.3

**Release Date:** 2026-01-15

## Summary
Fixed JWT validation error handling with improved logging and error types.

## Features
- Structured logging for JWT validation with correlation IDs
- New domain-specific error types (TOKEN_EXPIRED, INVALID_TOKEN, MALFORMED)

## Bugfixes
- **#456:** JWT validation silently fails on malformed tokens → now throws clear error
- **#789:** Expired tokens missing context in error logs → now includes userId, attempt count

## Security
- Dependency audit clean (npm audit passed)
- No new vulnerabilities introduced
- No secrets or PII in logs

## Deployment
- **Database migrations:** None required
- **Downtime:** None required
- **Rollback:** git revert, redeploy previous version
- **Rollout:** Standard blue-green deployment

## Testing
- Unit tests: 127/127 passing
- Integration tests: All passing
- Coverage: 89%
- Security scan: Clean
- All quality gates: Passed

## Changelog
See CHANGELOG.md for full details.

## Contributors
- @alice (implementation, testing)
- @bob (code review)

## Notes
This release improves error handling and observability for authentication. No action required from users.
```

### Step 9: Run Staging Verification

```bash
# If applicable, deploy to staging and test
npm install  # Ensure clean install works
npm run build  # Verify build succeeds
npm test -- --testNamePattern="smoke"  # Smoke tests in staging

# Verify endpoints work
curl https://staging.example.com/health  # Health check
curl https://staging.example.com/api/users  # Sample endpoint

# Verify logs look good
tail -f /var/log/app.log | grep "^{" | jq "."  # JSON logs should parse

# Verify monitoring/alerts work
# Trigger test alert, verify it's received
```

### Step 10: Execute Release via Kaiza MCP

```json
{
  "operation": "create_release",
  "version": "1.2.3",
  "tag": "v1.2.3",
  "changelog": "See CHANGELOG.md section [1.2.3]",
  "artifacts": [
    {
      "type": "npm_package",
      "package": "my-app",
      "version": "1.2.3",
      "registry": "https://registry.npmjs.org"
    }
  ],
  "breaking_changes": false,
  "rollback_plan": "git revert, redeploy previous version",
  "deployment_checklist": [
    "Unit tests pass: 127/127",
    "Coverage: 89%",
    "Quality gates: All passed",
    "Changelog: Updated",
    "Version: Bumped (1.2.2 → 1.2.3)",
    "Staging tested: Passed"
  ],
  "audit_metadata": {
    "release_lead": "alice",
    "reviewed_by": ["bob"],
    "timestamp": "2026-01-15T15:30:00Z"
  }
}
```

---

## Pre-Release Checklist

- [ ] All quality gates pass (lint, typecheck, tests, security, placeholder scan).
- [ ] Test coverage ≥80% (or documented exceptions).
- [ ] Version number bumped correctly (semantic versioning).
- [ ] CHANGELOG.md updated and accurate.
- [ ] No breaking changes (or clearly documented with migration guide).
- [ ] Documentation current (README, API docs, migration guides).
- [ ] Deployment impact assessed (migrations, rollout strategy, rollback plan).
- [ ] Monitoring/alerts configured for this release.
- [ ] Staging deployment tested and verified.
- [ ] Release notes written and accurate.
- [ ] Signatures/checksums generated (if distributed).
- [ ] All team reviews completed.

---

## Quality Checklist

- [ ] Code quality verified (all quality gates passing).
- [ ] Version numbers correct and consistent.
- [ ] Changelog complete and accurate.
- [ ] No breaking changes (or clearly documented).
- [ ] Deployment impact assessed and documented.
- [ ] Documentation up-to-date (README, API docs, guides).
- [ ] Staging tested successfully.
- [ ] Release notes written.
- [ ] Signatures/checksums generated.
- [ ] Rollback plan documented and tested.

---

## Deliverable Summary

```json
{
  "skill": "release-readiness",
  "completed": true,
  "release_version": "1.2.3",
  "verifications": {
    "code_quality": "passed",
    "version_numbers": "correct",
    "changelog": "complete_and_accurate",
    "breaking_changes": "none",
    "documentation": "current",
    "staging_tested": "passed",
    "deployment_impact": "assessed",
    "rollback_plan": "documented"
  },
  "quality_gates": {
    "lint": "passed",
    "typecheck": "passed",
    "tests": { "total": 127, "passed": 127, "coverage": 89 },
    "security_scan": "clean",
    "placeholder_scan": "clean"
  },
  "ready_to_release": true,
  "release_notes": "created",
  "approval": {
    "reviewed_by": ["bob"],
    "approved_at": "2026-01-15T15:00:00Z"
  }
}
```

---

## Related Skills

- All previous skills (code quality foundational to release)
- @kaiza-mcp-ops (release creation and deployment)
- /release-candidate (workflow for testing release)
