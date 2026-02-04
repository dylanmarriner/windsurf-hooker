# Workflow: /triage-prod-issue

**Purpose:** Rapidly diagnose and resolve production incidents with structured triage and root cause analysis.

**Prerequisites:** Production issue reported.

**Inputs:**
- Issue type: `<feature|payment|auth|database|etc>`
- Severity: `<critical|high|medium|low>`
- Description: `<what's happening>`

---

## Phase 1: Immediate Triage (0-5 minutes)

### Assess Severity

```json
{
  "critical": {
    "indicators": [
      "Complete outage (all users affected)",
      "Data loss or corruption",
      "Payment processing down",
      "Authentication broken"
    ],
    "action": "Page on-call team immediately, begin incident response"
  },
  "high": {
    "indicators": [
      "Significant degradation (20%+ users affected)",
      "Critical feature broken",
      "Error rate spike >1%"
    ],
    "action": "Notify team, start investigation within 5 minutes"
  },
  "medium": {
    "indicators": [
      "Partial degradation (some users affected)",
      "Non-critical feature broken",
      "Performance spike but recovering"
    ],
    "action": "Start investigation within 15 minutes"
  },
  "low": {
    "indicators": [
      "Minor issue",
      "Workaround available",
      "No user impact"
    ],
    "action": "Investigate within business day"
  ]
}
```

### Immediate Actions by Severity

**Critical:**
1. **Declare incident** → Incident channel, page on-call
2. **Status page** → Update "Investigating" or "Degraded Performance"
3. **User notification** → Email, SMS, in-app alert
4. **Mitigation (fast):**
   - Revert recent deploy
   - Scale up resources
   - Disable problematic feature
   - Route traffic away from affected service

**High/Medium/Low:**
1. **Create incident ticket** → Document issue, severity, impact
2. **Assign investigator** → Who's investigating?
3. **Set SLO** → When must be resolved?
4. **Monitor** → Watch metrics, error rate, user reports

---

## Phase 2: Diagnosis (5-30 minutes)

Use skill: **@incident-triage-and-rca**

### Step 1: Gather Data

```bash
# Error logs (last 30 minutes)
tail -500 /var/log/app.log | grep -i "error\|exception\|failed"

# Structured logs (JSON format)
tail -f /var/log/app.log | grep "^{" | jq "select(.level==\"error\")" | head -20

# Metrics (spike detection)
# - Error rate: normally <0.1%, now >1%?
# - Latency: p95 normally 50ms, now 500ms?
# - Memory: normal 500MB, now 1500MB?
# - CPU: normal <30%, now >80%?

# System resources
ps aux | head -20  # Memory, CPU
df -h              # Disk space
netstat -an | wc -l  # Connection count

# Recent changes
git log --oneline -10  # Did we deploy recently?
docker ps           # Container restarts?
```

### Step 2: Form Hypotheses

Based on data, list 3-5 hypotheses in order of likelihood:

```markdown
## Hypotheses (in order of likelihood)

1. **JWT validation failures** (Likelihood: High)
   - Evidence: Error log shows "JWTValidationError" 50 times in last 10 min
   - Evidence: Error started 5 min ago (coincides with deploy)
   - Next check: Examine JWT validation code in recent deploy

2. **Database connection pool exhausted** (Likelihood: Medium)
   - Evidence: Error logs show "too many connections"
   - Evidence: Latency spike 5 min ago
   - Next check: Check active DB connections

3. **Memory leak** (Likelihood: Low)
   - Evidence: Service restarted 3 times in last hour
   - Evidence: Memory graph shows steady increase
   - Next check: Heap dump analysis
```

### Step 3: Test Hypotheses (Cheapest First)

Verify each hypothesis, starting with cheapest:

```bash
# Hypothesis 1: Recent deploy caused regression
git diff HEAD~1 HEAD -- src/auth/jwt.ts
# If change looks suspicious → hypothesis confirmed

# Hypothesis 2: Database connections exhausted
mysql> SELECT count(*) FROM information_schema.processlist;
# Normal: <20, Concerning: >100

# Hypothesis 3: Memory leak
grep "out of memory" /var/log/app.log | tail -5
```

---

## Phase 3: Identify Root Cause (10-45 minutes)

### Example: JWT Validation Failing

```bash
# Get error patterns
grep "JWTValidationError" /var/log/app.log | tail -10

# Identify which error code is most common
grep -o '"errorCode":"[^"]*"' /var/log/app.log | sort | uniq -c | sort -rn
# Output:
#   45 "errorCode":"INVALID_TOKEN"
#   12 "errorCode":"TOKEN_EXPIRED"

# Check recent code change
git diff HEAD~1 HEAD -- src/auth/jwt.ts

# If you see:
# - const decoded = jwt.verify(token, secret, { expiresIn: "5m" }); // WRONG!
# Root cause: expiresIn should only be in jwt.sign(), not jwt.verify()
```

### Example: Database Connections Exhausted

```bash
# Check active connections
mysql> SHOW processlist;
# Find queries RUNNING for >10 seconds

# Check logs for slow queries
grep "Query_time: [1-9]" /var/log/mysql-slow.log | tail -20

# Identify the slow query, root cause
# If new slow query appears → caused by recent code change

# Check code for N+1 query pattern
git diff HEAD~1 HEAD -- src/db/queries.ts
```

---

## Phase 4: Mitigate (Immediate)

Choose fastest mitigation option:

```markdown
## Mitigation Options (ranked by speed)

### Option 1: Revert Deploy (2 minutes)
- git revert HEAD
- Push and deploy v1.2.2 (previous version)
- Wait 2 min for new version to roll out
- Risk: Low (going back to known-good code)
- When: If root cause is in recent deploy

### Option 2: Feature Flag (1 minute)
- Set BROKEN_FEATURE_FLAG=false
- No deploy needed (feature flag checked at runtime)
- Risk: Low (disables only broken feature)
- When: If issue is in optional feature

### Option 3: Scale Resources (5 minutes)
- kubectl scale deployment app --replicas=5
- Adds more instances to handle load
- Risk: Low (scales up, doesn't change code)
- When: Issue is resource exhaustion

### Option 4: Fix & Deploy (30-60 minutes)
- Identify bug, fix code
- Run tests, verify fix works
- Deploy new version
- Risk: Medium (need to verify fix works)
- When: Quick mitigation not possible

### Recommendation
Always choose fastest mitigation first. Debug later. Revert first, fix later.
```

---

## Phase 5: Verify Resolution (5-10 minutes)

After mitigation:

```bash
# Check error rate dropped
tail -100 /var/log/app.log | grep "error" | wc -l
# Should be back to normal (<1 per second)

# Check metrics recovered
# - Error rate: < 0.1% (was >1%)
# - Latency: p95 < 100ms (was >500ms)
# - User reports: stopped (no new complaints)

# Check for secondary issues
grep -i "cascading\|downstream\|failing" /var/log/app.log
# Did the fix cause other issues?

# Update status page
# "Issue resolved. Thank you for your patience."

# Notify users (if notification sent during incident)
# "The issue has been resolved. Services are returning to normal."
```

---

## Phase 6: Root Cause Analysis (Next 24 Hours)

Use skill: **@incident-triage-and-rca**

Complete detailed RCA post-incident:

```markdown
# Root Cause Analysis: <Incident Title>

## Incident Summary
- ID: INC-2026-0115-001
- Title: JWT validation failures
- Severity: High
- Duration: 15 minutes (10:30-10:45)
- Users Affected: ~50,000
- Data Loss: None

## Timeline
- 10:25: Deploy v1.2.3 (merged and deployed)
- 10:30: First user report (login failing)
- 10:32: Incident commander engaged
- 10:35: Root cause identified (JWT code regression)
- 10:37: Mitigation: Reverted to v1.2.2
- 10:40: Verification: Incident resolved
- 10:45: Status page updated, users notified

## Root Cause
Deploy v1.2.3 introduced regression:
- Used `expiresIn` in jwt.verify() (incorrect)
- `expiresIn` should only be in jwt.sign() (create token)
- Using `expiresIn` in jwt.verify() breaks validation

## Why Not Caught?
1. Insufficient unit tests (only happy path)
2. No property-based tests for parameter misuse
3. No integration tests (production-like scenarios)
4. Code review didn't catch parameter misuse

## Contributing Factors
1. Complex JWT library usage not fully understood
2. No examples in code of correct usage
3. Tests didn't cover realistic tokens with exp field
4. Integration tests would have caught this immediately

## Corrective Actions
1. Add property-based tests for JWT validation
2. Add integration tests (full login flow)
3. Add code review checklist for auth code
4. Document JWT library usage patterns

## Prevention Measures
1. CI gate: Add integration tests (fail without them)
2. CI gate: Add property-based tests for critical paths
3. Pre-deploy: Run in staging, verify no errors
4. Canary: Deploy to 10% first, monitor for 1 min

## Lessons Learned
1. Integration tests catch real-world scenarios unit tests miss
2. Property-based tests catch parameter misuse
3. Critical code needs multiple test types
4. Staging verification before production is critical

## Approval
- Incident Commander: alice
- RCA Reviewed: bob
- Corrective actions: Assigned to @charlie
```

---

## Handoff & Follow-Up

```
[ ] Incident resolved (mitigation applied, verification complete)
[ ] Root cause analysis completed
[ ] Corrective actions identified
[ ] Corrective actions assigned to team members
[ ] Post-incident meeting scheduled (if severity high/critical)
[ ] Team debriefing: What we learned
[ ] Prevention measures added to CI/tests
[ ] Documentation updated
[ ] Incident closed
```

---

## Tools & Commands Reference

### Log Searching
```bash
# Last 100 lines
tail -100 /var/log/app.log

# Search for errors
grep "error\|exception\|failed" /var/log/app.log | tail -50

# Parse JSON logs
tail -f /var/log/app.log | grep "^{" | jq "select(.level==\"error\")"

# Count errors by type
grep -o '"errorCode":"[^"]*"' /var/log/app.log | sort | uniq -c | sort -rn
```

### Metrics & Health Checks
```bash
# Health check
curl https://api.example.com/health

# Diagnostics
curl https://api.example.com/admin/diagnostics

# Database status
mysql> SHOW status;

# Connection count
netstat -an | grep ESTABLISHED | wc -l
```

### Fast Mitigations
```bash
# Revert recent deploy
git revert HEAD && git push

# Scale up
kubectl scale deployment app --replicas=5

# Disable feature
# Set environment variable or feature flag
```

---

## Success Criteria

- [ ] Severity assessed correctly
- [ ] Root cause identified (within SLO)
- [ ] Mitigation applied (fastest option chosen)
- [ ] Issue verified as resolved
- [ ] RCA completed (within 24 hours)
- [ ] Corrective actions documented
- [ ] Prevention measures implemented
- [ ] Team notified and learned
- [ ] Incident closed

---

## Related Skills & Workflows

- @debuggable-by-default (use logs/traces to diagnose)
- @observability-pack-implementer (structured logging enables diagnosis)
- @incident-triage-and-rca (detailed RCA process)
- @test-engineering-suite (integration tests prevent regressions)
