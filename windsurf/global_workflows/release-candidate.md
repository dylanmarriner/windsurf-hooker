# Workflow: /release-candidate

**Purpose:** Test release candidate in staging before deploying to production.

**Prerequisites:** Code merged to main, CI passing, ready for staging deployment.

**Inputs:**
- Version: `<version>` (e.g., "1.2.3")
- Release notes: `<release-notes-file>`

---

## Steps

### 1. Verify CI Status
```bash
# Check that main branch CI is passing
gh run list --branch main --status success --limit 1

# Verify latest commit
git log -1 --oneline

# Confirm this is the commit to release
```

### 2. Build Release Candidate Artifact
```bash
# Build artifact (npm package, Docker image, binary, etc.)
npm run build

# Create artifact
npm pack
# or
docker build -t my-app:rc-1.2.3 .

# Generate checksums
sha256sum my-app-1.2.3.tgz > my-app-1.2.3.tgz.sha256
```

### 3. Deploy to Staging
```bash
# Deploy RC to staging environment
# (Using your deployment system: Kubernetes, Heroku, Lambda, etc.)

kubectl set image deployment/my-app-staging \
  my-app=my-app:rc-1.2.3 \
  --record

# Wait for rollout
kubectl rollout status deployment/my-app-staging

# Verify deployment
curl https://staging.example.com/health
# Expected: {"status":"healthy"}
```

### 4. Smoke Tests (Staging)
```bash
# Run basic smoke tests in staging
npm run test:smoke -- --env=staging

# Test critical workflows
curl -X POST https://staging.example.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
# Expected: 200 with token

curl -X POST https://staging.example.com/api/payment \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"amount":1000}'
# Expected: 200 with payment result
```

### 5. Verify Logs
```bash
# Check for errors in staging logs
tail -f /var/log/my-app-staging.log | grep "error\|exception" | head -20

# Verify structured logging works
tail -f /var/log/my-app-staging.log | grep "^{" | jq "." | head -5

# Check for security warnings
grep -i "security\|vulnerability\|exploit" /var/log/my-app-staging.log
```

### 6. Performance Testing
```bash
# Load test staging (if applicable)
# Test with realistic load to catch performance regressions

# Example: Apache Bench
ab -n 1000 -c 10 https://staging.example.com/api/users

# Example: wrk
wrk -t4 -c100 -d30s https://staging.example.com/api/users

# Expected: No significant latency increase, no errors
```

### 7. Integration Testing
```bash
# Run full integration test suite against staging
npm run test:integration -- --env=staging

# Test with realistic data
# Test with production-like load
# Test all critical workflows
```

### 8. Verify Release Notes
```bash
# Check that CHANGELOG.md is accurate
cat CHANGELOG.md | grep -A 20 "^## \[1.2.3\]"

# Check release notes are clear
# Verify version number is correct
# Verify date is current
```

### 9. Security Verification
```bash
# Verify no secrets in release artifacts
strings my-app-1.2.3.tgz | grep -i "password\|secret\|token" | grep -v test

# Verify signatures (if applicable)
gpg --verify my-app-1.2.3.tgz.sig

# Verify checksums
sha256sum -c my-app-1.2.3.tgz.sha256
```

### 10. Performance Comparison
```bash
# Compare staging RC to production baseline
# If latency increased >5%, investigate before production deploy

# Check metrics
# - API endpoint latency (p95, p99)
# - Error rate
# - Memory usage
# - CPU usage
# - Database connection pool usage

# Expected: No significant increase from production baseline
```

### 11. Approval Sign-Off
```
[ ] Staging deployment successful
[ ] Smoke tests passing
[ ] No errors in logs
[ ] Performance acceptable
[ ] Security verified
[ ] Release notes accurate
[ ] Ready for production?

If all checks pass: Move to production deployment

If issues found:
1. Note issue
2. Go back to main branch
3. Fix issue
4. Create new commit
5. Re-run CI
6. Rebuild RC
7. Test again in staging
8. Do not proceed to production with known issues
```

### 12. Production Deployment Plan
Before deploying, document plan:

```markdown
## Production Deployment Plan: v1.2.3

### Deployment Strategy
- Blue-green deployment (minimize downtime)
- Canary rollout (10% → 25% → 50% → 100% over 30 minutes)
- Rollback ready (revert to v1.2.2 if critical issues)

### Monitoring During Deployment
- [ ] Error rate normal (<0.1%)
- [ ] API latency normal (p95 <100ms)
- [ ] Payment success rate normal (>99.9%)
- [ ] Database performance normal
- [ ] No unusual logs or alerts

### Rollback Triggers
If any of these occur, rollback to v1.2.2:
- Error rate spikes >1%
- Payment success rate drops <99%
- API latency p95 >500ms
- Database connectivity issues
- Unhandled exceptions in critical path

### Communication Plan
- [ ] Notify team 15 min before deployment
- [ ] Update status page during deployment
- [ ] Notify users if issues occur
- [ ] Post-deployment verification email
```

### 13. Final Checklist Before Production

```
Staging Testing:
[ ] Smoke tests passed
[ ] Integration tests passed
[ ] Performance acceptable
[ ] Logs clean (no errors)
[ ] Security verified
[ ] Release notes accurate

Release Artifacts:
[ ] Docker image built and tested
[ ] npm package built and verified
[ ] Checksums generated
[ ] Signatures validated
[ ] Release notes included

Rollback Plan:
[ ] Previous version available
[ ] Rollback procedure documented
[ ] Rollback tested (in staging)

Team Coordination:
[ ] Team notified
[ ] On-call engineer available
[ ] Deployment window confirmed
[ ] Status page ready to update
```

---

## Common Issues & Fixes

| Issue | Check | Fix |
|-------|-------|-----|
| Staging deployment fails | Check deployment logs | Verify image is built, credentials are correct |
| Health check fails | Check service logs | Verify service started, config loaded |
| Database connection fails | Check DB credentials, network | Verify DB is accessible from staging |
| Performance degraded | Compare to production baseline | Check for N+1 queries, memory leaks, missing indexes |
| High error rate | Check error logs | Find root cause, fix before production |

---

## Success Criteria

- [ ] RC successfully deployed to staging
- [ ] Smoke tests passing
- [ ] Integration tests passing
- [ ] Logs clean (no errors)
- [ ] Performance acceptable
- [ ] Security verified
- [ ] Release notes accurate
- [ ] Rollback plan documented and tested
- [ ] Team approval obtained
- [ ] Ready for production deployment

---

## Related Skills & Workflows

- @release-readiness (verify code is production-ready)
- @debuggable-by-default (interpret logs and metrics)
- @kaiza-mcp-ops (deploy via CI/CD)
- /pre-pr-review (ensure code quality before RC)
