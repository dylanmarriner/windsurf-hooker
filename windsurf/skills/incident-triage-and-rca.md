# Skill: @incident-triage-and-rca

**Purpose:** Rapidly diagnose and resolve production incidents with structured triage, root cause analysis, corrective actions, and prevention.

**Invocation:** `/use-skill incident-triage-and-rca` when production issues occur.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** When production incident reported.
- **Dependencies:** @debuggable-by-default, @observability-pack-implementer.
- **Owner:** Incident response team.

---

## Phase 1: Immediate Triage (First 5 Minutes)

### Severity Assessment

```json
{
  "severity_levels": {
    "critical": {
      "description": "Complete outage or data loss affecting all users",
      "impact": "Revenue loss, reputational damage",
      "slo": "Incident commander engaged within 5 minutes",
      "examples": [
        "Authentication broken (all login requests fail)",
        "Payment processing down (no transactions going through)",
        "Data corruption (user data being overwritten)",
        "Cascading failures (multiple services down)"
      ]
    },
    "high": {
      "description": "Significant degradation or data corruption affecting subset of users",
      "impact": "User impact, potential data loss",
      "slo": "Investigation started within 15 minutes",
      "examples": [
        "JWT validation failures for 20% of users",
        "Database connection pool exhausted",
        "Memory leak causing service restart loop",
        "Unhandled exceptions in critical path"
      ]
    },
    "medium": {
      "description": "Degraded performance or non-critical features broken",
      "impact": "User annoyance, not critical",
      "slo": "Investigation started within 1 hour",
      "examples": [
        "API endpoint latency spike (p95: 5s, normally 50ms)",
        "Email notifications delayed",
        "Analytics dashboard slow",
        "Non-critical feature broken"
      ]
    },
    "low": {
      "description": "Minor issue, workaround exists",
      "impact": "Minimal",
      "slo": "Investigated within business day",
      "examples": [
        "Typo in error message",
        "Minor performance issue in rarely-used feature",
        "Cosmetic bug in UI"
      ]
    }
  }
}
```

### Immediate Actions by Severity

**Critical:**
1. **Declare incident** → Notify incident commander, on-call team
2. **Communication** → Update status page, notify users
3. **Mitigate immediately** (don't debug first):
   - Revert recent deploy
   - Scale up resources
   - Disable problematic feature
   - Route traffic away from affected service
4. **Assign investigator** → Start root cause analysis in parallel

**High/Medium/Low:**
1. **Create incident** → Issue/ticket with severity level
2. **Assign investigator** → Someone begins diagnosis
3. **Set SLO** → Investigation deadline based on severity
4. **Monitor** → Watch error rates, performance metrics

---

## Phase 2: Diagnosis (5-30 Minutes)

### Step 1: Gather Data

```bash
# Collect logs (search for errors)
grep -i "error\|exception\|failed" /var/log/app.log | tail -100

# Parse structured logs
tail -f /var/log/app.log | grep "^{" | jq "." | grep "error\|exception" | head -20

# Check metrics
# - Error rate spike
# - Latency increase
# - Memory/CPU surge
# - Connection pool exhaustion
# - Specific error codes

# Check for recent changes
git log --oneline -20
# Did we deploy something recently?

# Check system resources
ps aux | grep "app\|node\|python"  # CPU, memory usage
df -h                               # Disk space
netstat -an | grep ESTABLISHED | wc -l  # Connection count
```

### Step 2: Form Hypothesis

Based on data gathered, form hypotheses (in order of likelihood):

```json
{
  "hypotheses": [
    {
      "rank": 1,
      "hypothesis": "JWT validation failing for some users",
      "likelihood": "high",
      "evidence": [
        "Error log contains 50 'JWTValidationError' in last 10 minutes",
        "Only users from specific region affected (IP pattern)",
        "Error started 5 minutes ago (coincides with recent deploy)"
      ],
      "next_check": "Examine JWT validation code changes in recent deploy"
    },
    {
      "rank": 2,
      "hypothesis": "Database connection pool exhausted",
      "likelihood": "medium",
      "evidence": [
        "Error logs show 'too many connections' errors",
        "Latency spike visible in metrics"
      ],
      "next_check": "Check active connection count, query logs for slow queries"
    },
    {
      "rank": 3,
      "hypothesis": "Memory leak causing out-of-memory error",
      "likelihood": "low",
      "evidence": [
        "Service restarted 3 times in last hour",
        "Memory graph shows steady increase"
      ],
      "next_check": "Heap dump analysis"
    }
  ]
}
```

### Step 3: Eliminate Hypotheses (Cheapest First)

Test hypotheses starting with cheapest (quickest to verify):

1. **Check recent deploy:**
   ```bash
   git log -1 --stat
   # What was deployed? Did JWT validation code change?
   ```

2. **Check database:**
   ```sql
   SELECT count(*) FROM information_schema.processlist;
   -- Normal: <20 connections, Concerning: >100 connections
   ```

3. **Check error patterns:**
   ```bash
   grep "JWTValidationError" /var/log/app.log | wc -l
   # How many? What error codes?
   ```

4. **Check specific error code:**
   ```bash
   grep -o '"errorCode":"[^"]*"' /var/log/app.log | sort | uniq -c | sort -rn
   # Which error codes are most common?
   ```

---

## Phase 3: Root Cause Identification (15-45 Minutes)

Once hypothesis narrowed, dig deep:

### Example: JWT Validation Failing

```bash
# 1. Get error logs
grep "JWTValidationError" /var/log/app.log | tail -5

# Output:
# {"timestamp":"2026-01-15T10:30:00Z","errorCode":"TOKEN_EXPIRED","userId":"user-123"}
# {"timestamp":"2026-01-15T10:30:05Z","errorCode":"TOKEN_EXPIRED","userId":"user-456"}
# {"timestamp":"2026-01-15T10:30:10Z","errorCode":"INVALID_TOKEN","userId":"user-789"}

# 2. Identify pattern
# Most errors are TOKEN_EXPIRED or INVALID_TOKEN

# 3. Check recent code change
git diff HEAD~1 src/auth/jwt.ts

# If change looks suspicious:
# Before:
#   const decoded = jwt.verify(token, secret);
# After:
#   const decoded = jwt.verify(token, secret, { expiresIn: "5m" }); // WRONG!

# This is the bug: expiresIn should only be on jwt.sign(), not jwt.verify()

# 4. Root cause: Code change introduced regression
# Mitigation: Revert the change immediately
```

### Example: Database Connection Pool Exhausted

```bash
# 1. Check active connections
mysql> SELECT count(*) FROM information_schema.processlist;
# Returns: 500 (normal is <20)

# 2. Check for slow queries
mysql> SHOW processlist;
# Find queries that are RUNNING for >10 seconds

# 3. Check query performance
mysql> SELECT * FROM slow_query_log WHERE query_time > 5;
# Identify which queries are slow

# 4. Root cause identified
# A recent code change added N+1 query: for each user, query all their orders
# With 10,000 users, this causes 10,000+ queries per request

# 5. Mitigation
# - Revert code change (quick fix)
# - OR increase connection pool size (temporary)
# - OR add query cache (temporary)
```

---

## Phase 4: Mitigation (Immediate)

### Quick Fixes (Choose Fastest)

```json
{
  "mitigation_options": {
    "revert_deploy": {
      "time_to_fix": "2 minutes",
      "risk": "low (revert to known-good code)",
      "when": "When root cause is in recent deploy",
      "steps": ["git revert HEAD", "git push", "deploy previous version"]
    },
    "feature_flag_disable": {
      "time_to_fix": "1 minute",
      "risk": "low (disables broken feature only)",
      "when": "When issue is in optional feature",
      "steps": ["Set FEATURE_FLAG_BROKEN_FEATURE=false", "No deploy needed (feature flag check)"]
    },
    "scale_resources": {
      "time_to_fix": "5 minutes",
      "risk": "low (scales up, doesn't change code)",
      "when": "When issue is resource exhaustion",
      "steps": ["kubectl scale deployment app --replicas=5", "Wait for new pods to be ready"]
    },
    "scale_database": {
      "time_to_fix": "10-30 minutes",
      "risk": "medium (depends on database type)",
      "when": "When database is bottleneck",
      "steps": [
        "Increase connection pool size",
        "OR scale database vertically (add CPUs/RAM)",
        "OR add read replicas"
      ]
    },
    "fix_bug": {
      "time_to_fix": "30-120 minutes",
      "risk": "medium (need to verify fix)",
      "when": "When quick mitigation not possible",
      "steps": [
        "Fix code",
        "Run tests locally",
        "Deploy to staging",
        "Test in staging",
        "Deploy to production"
      ]
    }
  }
}
```

**Choose immediate mitigation over perfect fix:**
- Revert broken deploy (2 min) instead of debugging + fixing (30 min)
- Disable feature flag (1 min) instead of fixing code
- Scale up database (10 min) instead of optimizing queries

---

## Phase 5: Verification (5-10 Minutes)

After mitigation, verify issue is resolved:

```bash
# 1. Check error rate dropped
tail -f /var/log/app.log | grep "error" | wc -l
# Should be back to normal (<1 per second)

# 2. Check user-facing metrics
# - API endpoint latency: p95 < 100ms
# - Error rate: < 0.1%
# - Payment success rate: > 99.9%

# 3. Check for secondary issues
grep -i "cascading\|downstream" /var/log/app.log
# Did the fix cause other issues?

# 4. Announce resolution
# Update status page: "Incident resolved"
# Notify users via email/SMS if notification sent during incident
```

---

## Phase 6: Root Cause Analysis (Post-Incident, Next 24 Hours)

Complete within 24 hours while details are fresh:

```markdown
## Root Cause Analysis Report

### Incident Summary
- **ID:** INC-2026-0115-001
- **Title:** JWT validation failures for 20% of users
- **Severity:** High
- **Duration:** 15 minutes (10:30-10:45)
- **Users Affected:** ~50,000
- **Data Loss:** None
- **Incident Commander:** alice

### Timeline
- **10:25:** Deploy v1.2.3 merged and deployed
- **10:30:** First error received from users (monitoring alert)
- **10:32:** Incident commander engaged
- **10:35:** Root cause identified (JWT validation code regression)
- **10:37:** Mitigation: Deploy reverted to v1.2.2
- **10:40:** All tests passing, incident resolved
- **10:45:** Status page updated, users notified

### Root Cause
Deploy v1.2.3 introduced regression in JWT validation code:

**Before (v1.2.2):**
```typescript
const decoded = jwt.verify(token, secret);
return decoded as Claims;
```

**After (v1.2.3 - BROKEN):**
```typescript
const decoded = jwt.verify(token, secret, { expiresIn: "5m" });
return decoded as Claims;
```

**Why This Broke:**
- `expiresIn` parameter should only be used in `jwt.sign()` (when creating tokens)
- Using `expiresIn` in `jwt.verify()` (when validating tokens) causes verification to fail
- Root cause: Code reviewer didn't catch the misuse of JWT library

### Why It Wasn't Caught
- Unit tests for JWT validation existed but were insufficient:
  - Tests only checked happy path (valid tokens)
  - Tests didn't cover "verify with unexpected parameters" scenario
  - Tests didn't use realistic tokens with exp field
- Code review comments about expiresIn parameter were ignored
- No property-based tests to catch parameter misuse

### Contributing Factors
1. **Lack of property-based testing:** For critical auth code
2. **Insufficient code review:** Parameter not questioned
3. **Limited test coverage:** Only happy path tested
4. **No integration tests:** Production-like behavior not tested pre-deploy

### Corrective Actions (To Prevent Recurrence)

#### Code Changes
1. **Add property-based tests for JWT validation:**
   ```typescript
   import fc from "fast-check";
   test("verify never accepts expiresIn parameter", () => {
     const validToken = jwt.sign({ userId: "user-123" }, secret, { expiresIn: "1h" });
     
     // Should succeed
     expect(() => validateJWT(validToken, secret)).not.toThrow();
     
     // Should fail if expiresIn passed to verify (parameter validation test)
     const invalidCall = () => {
       (jwt.verify as any)(validToken, secret, { expiresIn: "5m" });
     };
     expect(invalidCall).toThrow(); // Documents correct usage
   });
   ```

2. **Improve unit test coverage:**
   - Add test for tokens with exp field
   - Add test for expired tokens
   - Add test for invalid signatures
   - Add test with real JWT format

3. **Add integration test:**
   ```typescript
   test("end-to-end: full login + JWT validation flow", async () => {
     const loginResponse = await request(app).post("/login").send({
       email: "user@example.com",
       password: "password123"
     });
     
     const token = loginResponse.body.token;
     
     // Verify token works in subsequent request
     const response = await request(app)
       .get("/user/profile")
       .set("Authorization", `Bearer ${token}`);
     
     expect(response.status).toBe(200);
   });
   ```

#### Process Changes
1. **Code review checklist addition:**
   - [ ] JWT/auth code must have parameter validation tests
   - [ ] Critical paths must have integration tests
   - [ ] Library usage matches official documentation

2. **Pre-deploy verification:**
   - [ ] Run integration tests in staging before production deploy
   - [ ] Check error rate in staging (should be 0)
   - [ ] Verify JWT validation specifically works end-to-end

3. **Monitoring enhancement:**
   - Alert on JWT validation error rate > 1% (trigger auto-rollback)
   - Track error codes specifically (TOKEN_EXPIRED vs INVALID_TOKEN)
   - Add canary deployment (10% of traffic first, 30 min before 100%)

#### Documentation
1. **JWT usage guide created:**
   - Document correct usage of jwt.verify() (no expiresIn parameter)
   - Link to official jsonwebtoken documentation
   - Provide code examples

2. **Incident review:**
   - Shared findings with team
   - Discussed why tests were insufficient
   - Discussed code review process

### Prevention Checklist
- [ ] Property-based tests added for JWT library usage
- [ ] Unit test coverage for all error paths
- [ ] Integration tests for critical auth flow
- [ ] Code review checklist updated
- [ ] Pre-deploy staging verification documented
- [ ] Canary deployment process implemented
- [ ] Auto-rollback on error rate spike configured
- [ ] JWT usage guide documented
- [ ] Team trained on findings

### Lessons Learned
1. **Critical paths need comprehensive testing:** Unit tests alone aren't enough for auth
2. **Parameter misuse can break core functionality:** Validate parameters match library contract
3. **Integration tests catch real-world scenarios:** Unit tests in isolation missed this bug
4. **Canary deployment helps:** Full rollout would have hit more users (10% canary would have caught in 1 min)

### Appendix A: Error Logs

```json
{"timestamp":"2026-01-15T10:30:00Z","errorCode":"INVALID_TOKEN","message":"JsonWebTokenError: malformed at ..."}
{"timestamp":"2026-01-15T10:30:05Z","errorCode":"INVALID_TOKEN","message":"JsonWebTokenError: malformed at ..."}
```

### Appendix B: Performance Impact

- **During incident:** Error rate 5% (normal: 0.01%), JWT validation latency 0ms (failed fast)
- **After mitigation:** Error rate back to 0.01%, latency 5ms (normal)
- **No data loss:** All errors were validation failures, no data corruption

### Approval
- **Incident Commander:** alice (verified root cause, approved mitigation)
- **Post-Incident Review:** bob (reviewed RCA, approved corrective actions)
- **Date Completed:** 2026-01-16
```

---

## Quality Checklist

- [ ] Triage completed within SLO.
- [ ] Severity assessed correctly.
- [ ] Root cause identified.
- [ ] Immediate mitigation applied.
- [ ] Issue verified as resolved.
- [ ] RCA completed within 24 hours.
- [ ] Corrective actions documented.
- [ ] Prevention measures implemented.
- [ ] Team notified of findings.
- [ ] Prevention measures added to CI/tests.

---

## Deliverable Summary

```json
{
  "skill": "incident-triage-and-rca",
  "completed": true,
  "incident": {
    "id": "INC-2026-0115-001",
    "title": "JWT validation failures",
    "severity": "high",
    "duration_minutes": 15
  },
  "triage": {
    "assessment_completed": true,
    "time_to_assess_minutes": 5,
    "severity_correct": true
  },
  "diagnosis": {
    "root_cause_identified": true,
    "time_to_diagnose_minutes": 10,
    "hypothesis_confirmed": true
  },
  "mitigation": {
    "applied": true,
    "time_to_mitigate_minutes": 7,
    "verified": true
  },
  "rca": {
    "completed": true,
    "corrective_actions": 5,
    "prevention_measures": 4,
    "team_notified": true
  }
}
```

---

## Related Skills

- @debuggable-by-default (provides logs for diagnosis)
- @observability-pack-implementer (provides metrics for diagnosis)
- @test-engineering-suite (property tests + integration tests prevent regressions)
- /triage-prod-issue (workflow wrapper around this skill)
