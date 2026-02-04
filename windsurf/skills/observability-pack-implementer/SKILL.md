---
name: observability-pack-implementer
description: Implement structured logging, tracing, metrics, and redaction policies across services. Invoke as @observability-pack-implementer.
---

# Skill: Observability Pack Implementer

## Purpose
Establish structured logging, tracing, and metrics conventions that enable operators to diagnose production issues without source code access.

## When to Use This Skill
- Setting up new services or applications
- Adding observability to existing services
- Implementing correlation ID propagation
- Adding metrics or traces to critical paths
- Enforcing redaction policies

## Steps

### 1) Adopt structured logging schema
Ensure all logs are JSON with required fields:
- timestamp, level, message, service, env, version, request_id
- Recommended: component, op, duration_ms, error

Reference: `observability/logging_schema.md`

### 2) Implement correlation ID propagation
- Generate request_id at entry (HTTP handler, job runner)
- Pass request_id to all downstream operations
- Ensure every log includes request_id

Example (JavaScript):
```javascript
import { createLogger, ensureRequestId } from './obs.js';

app.use((req, res, next) => {
  const requestId = ensureRequestId(req.headers);
  const logger = log.child({ request_id: requestId });
  req.logger = logger;
  res.setHeader('X-Request-Id', requestId);
  next();
});
```

### 3) Add RED/USE metrics
- Rate: requests_total (counter)
- Errors: request_errors_total (counter)
- Duration: request_duration_ms (histogram)

Example:
```javascript
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    const duration = Date.now() - start;
    metrics.recordRequest(req.method, req.route, res.statusCode, duration);
  });
  next();
});
```

### 4) Implement redaction policy
Apply redaction to denylisted keys in logs:
- Never emit: passwords, tokens, API keys, raw PII
- Use allowlist patterns: internal IDs, hashes, truncated values

Reference: `observability/redaction_policy.md`

### 5) Add tracing (optional, for complex flows)
Use OpenTelemetry or similar:
- Create spans for each operation (HTTP, DB, external API)
- Include correlation IDs in spans
- Never attach sensitive payloads

Reference: `observability/tracing_conventions.md`

## Quality Checklist

- [ ] All logs are JSON with required fields
- [ ] request_id is generated and propagated end-to-end
- [ ] RED metrics are recorded
- [ ] Redaction is enforced for sensitive keys
- [ ] Spans exist for external calls (if using traces)
- [ ] Tests verify logs and metrics are emitted

## Verification Commands

```bash
npm test 2>&1 | head -20 | grep -o '"service":"[^"]*"'
npm test 2>&1 | jq '.request_id' | sort | uniq
npm test 2>&1 | grep -i "password\|token" || echo "Clean"
```

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: Services or modules with new observability
- **Verification**: Sample log output, correlation ID propagation confirmed
- **Results**: Redaction verified, no sensitive data leaked
