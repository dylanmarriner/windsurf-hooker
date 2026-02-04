---
name: incident-triage-and-rca
description: Triage production incidents and conduct root cause analysis with evidence-driven diagnosis and prevention gates. Invoke as @incident-triage-and-rca.
---

# Skill: Incident Triage and RCA

## Purpose
When production is broken, rapidly triage severity, apply reversible mitigations, gather evidence, and then conduct a blameless RCA to prevent recurrence.

## When to Use This Skill
- Production incidents are reported
- Error rates spike unexpectedly
- Services are degraded or down
- Data inconsistency is detected

## Steps

### 1) Immediate triage (0-5 minutes)
Confirm the incident:
- What is broken? (service, endpoint, data flow)
- When did it start? (timestamp from metrics or logs)
- Who is impacted? (customers, internal users, percentage)
- Is it still ongoing?
- What is the severity?

**Severity levels:**
- **Sev 0**: Safety/legal or catastrophic data loss in progress. Stop the line immediately.
- **Sev 1**: Major outage or widespread user-impacting failure. Mitigate immediately.
- **Sev 2**: Partial outage or significant degradation with limited blast radius.
- **Sev 3**: Minor degradation or non-urgent operational issue.

Reference: `runbooks/triage.md`

### 2) Stabilize (5-15 minutes)
Choose reversible mitigations:
- Traffic shaping (reduce traffic to failing service)
- Feature disable (toggle off the broken feature)
- Rollback (revert to last known good version)
- Rate limiting (protect against cascade failures)
- Circuit breaker (stop calling a failing dependency)

Example:
```bash
# Disable broken feature flag
export ENABLE_NEW_CHECKOUT=false

# Reduce traffic to failing service
kubectl autoscale deployment api --min=1 --max=1

# Rollback if necessary
git deploy v1.2.2
```

Measure success:
- Error rate returns to baseline
- Latency returns to baseline
- Users can complete key flows

### 3) Evidence collection (time-bounded)
Gather data from:
- **Logs**: Filter by service, env, version, and correlation ID
  ```bash
  # Find errors around the incident time
  grep '"level":"error"' logs.json | grep '2026-01-15T14:30' | head -100
  ```
- **Metrics**: Check error rate, latency, throughput
  ```bash
  # Did error rate spike at 14:30 UTC?
  curl http://prometheus/api/v1/query_range?query=request_errors_total
  ```
- **Traces**: Capture failing request traces
  ```bash
  # Find slow or failed spans
  curl http://jaeger/api/traces?service=api&tags=error:true
  ```

Document findings in hypothesis log (step 4).

### 4) Hypothesis log
Maintain a list as you investigate:

| Hypothesis | Supporting Evidence | Refuting Evidence | Status |
|-----------|-------------------|-------------------|--------|
| Database query timeout | Error logs show "timeout", p99 latency spiked | Some queries complete normally | Testing |
| Memory leak in new feature | RSS grew 500MB in 1 hour | Restart cleared memory | Likely cause |
| Traffic spike from bot | Request rate 5x normal | Request distribution normal | Ruled out |

### 5) Root cause analysis (after stabilization)
Once the service is stable, conduct a blameless RCA:

**Use the RCA template:** `runbooks/rca_template.md`

Key sections:
- **Detection**: How was it detected? How long before detection?
- **Timeline**: Exact sequence of events with timestamps
- **Root cause**: What broke and why wasn't it caught?
- **Contributing factors**: What made it worse?
- **What went well**: What helped us recover quickly?
- **What went poorly**: Where were we slow?

Example RCA summary:
```markdown
## Root Cause
Database migration (migration-20260115-001.sql) removed an index on users.email,
causing a full table scan on every login attempt. This was not caught during
code review because the migration was not tested against production-scale data.

## Contributing Factors
1. No regression test for login latency
2. Prod database is 100x larger than staging
3. Migration was applied at peak traffic time

## What Went Well
1. Error logs were detailed enough to identify the slow query
2. Rollback was clean (index creation is idempotent)
3. Team responded quickly

## What Went Poorly
1. Migration was not performance-tested before deployment
2. No alert for query latency increase
3. Rollback took 10 minutes (manual process)
```

### 6) Corrective actions
For each root cause, define preventive actions:

| Category | Action | Owner | Due Date | Verification |
|----------|--------|-------|----------|--------------|
| Code | Add index back; test migration against prod data | alice | 2026-01-16 | Staging migration runs in <2s |
| Tests | Add regression test for login latency | bob | 2026-01-16 | Test fails without index |
| Alerts | Add alert for query p99 latency >500ms | charlie | 2026-01-17 | Alert fires in test |
| Process | Require migration review + perf testing | team | 2026-01-17 | Process doc updated |

### 7) Communication
Use template: `runbooks/comms_template.md`

Send updates to stakeholders:
- Initial notice: severity, impact, status, ETA for next update
- Status updates: what changed, current metrics, mitigation status
- Resolution notice: what was done, impact ended, follow-up RCA ETA

### 8) Post-incident
- [ ] RCA document is written and shared
- [ ] Corrective actions are scheduled and tracked
- [ ] Team debriefing is scheduled
- [ ] Retrospective is conducted blameless (focus on systems, not people)

Reference: `runbooks/rollback_checklist.md`

## Quality Checklist

- [ ] Incident severity is correctly assessed
- [ ] Mitigation is reversible and tested in staging first
- [ ] Evidence is collected from logs, metrics, traces
- [ ] Hypothesis log is maintained during investigation
- [ ] Root cause is identified with supporting evidence
- [ ] RCA document is blameless and thorough
- [ ] Corrective actions are specific and measurable
- [ ] Team is debriefed and feedback incorporated

## Verification Commands

```bash
# Query logs around incident time
grep '"timestamp":"2026-01-15T14:30' logs.json | jq '.level' | sort | uniq -c

# Check metrics for the time window
curl 'http://prometheus/api/v1/query_range?query=request_errors_total&start=1642264800&end=1642265400&step=60s'

# Verify corrective action (regression test)
npm test -- --testNamePattern="login latency"

# Check if alert would have caught it
npm run test:alerts
```

## How to Recover if RCA Is Incomplete

If you realize you missed something during RCA:
1. Create a follow-up issue with the missing analysis
2. Schedule a follow-up RCA session
3. Document findings and prevent

## KAIZA-AUDIT Compliance

When resolving an incident, your KAIZA-AUDIT block must include:
- **Plan**: incident-fix-<id>
- **Scope**: Root cause, corrective actions, prevention gates
- **Verification**: RCA conducted, tests added, alerts configured
- **Results**: Incident fully resolved, preventive measures in place
- **Risk Notes**: Any residual risks, follow-up actions
