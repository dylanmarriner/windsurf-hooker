---
name: debuggable-by-default
description: Add structured logging, correlation IDs, and observability to every boundary layer so failures are diagnosable without redeployment. Invoke as @debuggable-by-default.
---

# Skill: Debuggable by Default

## Purpose
When code fails in production, the structured logs and correlation IDs should tell the story without needing to re-run the scenario. Every boundary layer (HTTP handler, job runner, DB client, external API call) must emit actionable, machine-parseable telemetry.

## When to Use This Skill
- Writing HTTP handlers or REST endpoints
- Writing job runners or scheduled tasks
- Adding external API integrations
- Adding database operations
- Any code that crosses a boundary (network, process, storage)

## Steps

### 1) Identify boundary layers
Boundaries are places where:
- Requests enter the system (HTTP handler, message queue, file upload)
- Requests leave the system (external API call, database query, file write)
- Failures are most likely to occur (network errors, validation errors, timeouts)

### 2) Generate a correlation ID at entry
At the first boundary (e.g., HTTP request handler):
- Check for existing `X-Request-Id` or `X-Correlation-Id` header
- If absent, generate a unique ID (UUID or random string with prefix)
- Pass this ID to all downstream operations

Example (JavaScript):
```javascript
import { ensureRequestId } from './observability/node/obs.js';

app.use((req, res, next) => {
  const requestId = ensureRequestId(req.headers);
  req.requestId = requestId;
  res.setHeader('X-Request-Id', requestId);
  next();
});
```

### 3) Emit structured logs at every step
At entry, exit, and error, emit JSON logs with:
- `timestamp`: ISO-8601 UTC
- `level`: 'debug', 'info', 'warn', 'error'
- `message`: Human-readable summary
- `service`: Service/app name
- `env`: Environment (dev/staging/prod)
- `version`: Build version
- `request_id`: Correlation ID from step 2
- `component`: Module or subsystem name
- `op`: Operation name (e.g., 'http.handler.auth', 'db.query.user', 'api.call.stripe')
- `duration_ms`: For completed operations
- `error`: Only for failures; include type, message, safe stack trace (redacted)

Example (JavaScript using obs.js):
```javascript
const log = createLogger({ service: 'api', env: process.env.NODE_ENV, version: pkg.version });

app.post('/users', (req, res) => {
  const requestId = req.requestId;
  const logger = log.child({ request_id: requestId, op: 'http.handler.user.create' });
  
  logger.info('user creation request received', { email: req.body.email });
  
  try {
    const user = await createUser(req.body);
    logger.info('user created successfully', { user_id: user.id, duration_ms: Date.now() - start });
    res.status(201).json(user);
  } catch (err) {
    logger.errorFrom('user creation failed', err, { email: req.body.email });
    res.status(500).json({ error: 'Internal error' });
  }
});
```

### 4) Log external API calls
For every external service call (HTTP, DB, cache, queue):
- Log before the call with parameters (sanitized)
- Log after success with result summary and duration
- Log failures with error type, message, and retry information

Example:
```javascript
async function fetchUserFromAuth(userId, requestId) {
  const logger = log.child({ request_id: requestId, op: 'api.call.auth' });
  const start = Date.now();
  
  logger.debug('calling auth service', { user_id: userId, auth_url: process.env.AUTH_URL });
  
  try {
    const res = await fetch(`${process.env.AUTH_URL}/users/${userId}`, {
      headers: { 'X-Request-Id': requestId },
      timeout: 5000,
    });
    const duration = Date.now() - start;
    
    if (!res.ok) {
      logger.warn('auth service returned error', { status: res.status, duration_ms: duration });
      throw new Error(`Auth error: ${res.status}`);
    }
    
    const user = await res.json();
    logger.debug('auth call succeeded', { duration_ms: duration });
    return user;
  } catch (err) {
    const duration = Date.now() - start;
    logger.errorFrom('auth call failed', err, { duration_ms: duration });
    throw err;
  }
}
```

### 5) Ensure request_id propagates
Pass the `request_id` to all downstream operations:
- As an HTTP header to external services
- As a parameter to logger.child() for all new log contexts
- In database query context if available

Example (passing to DB):
```javascript
async function queryUsers(requestId) {
  const logger = log.child({ request_id: requestId, op: 'db.query.users' });
  
  try {
    const start = Date.now();
    const rows = await db.query('SELECT * FROM users LIMIT 10', { requestId });
    const duration = Date.now() - start;
    logger.debug('query succeeded', { row_count: rows.length, duration_ms: duration });
    return rows;
  } catch (err) {
    logger.errorFrom('query failed', err);
    throw err;
  }
}
```

### 6) Validate schema compliance
Ensure logs match the schema in `observability/logging_schema.md`:
- Required fields: timestamp, level, message, service, env, version, request_id
- Recommended fields: component, op, duration_ms, error
- No sensitive data (secrets, tokens, PII) in any field

### 7) Add error recovery context
When logging errors, include actionable recovery information:
- What was the system trying to do?
- What failed?
- What should the operator do?

Example:
```javascript
logger.errorFrom('database connection failed', err, {
  message: 'Failed to connect to primary database; retrying to read-replica',
  recovery: 'Check database.example.com uptime, verify network connectivity from this host',
  retry_after_ms: 1000,
});
```

## Quality Checklist

- [ ] All boundary layers (HTTP, DB, external API) emit structured logs
- [ ] Correlation ID is generated at entry and passed downstream
- [ ] All logs include request_id, service, env, version, timestamp, level, message
- [ ] Operation names (op field) are consistent and documented
- [ ] Error logs include error.type, error.message, error.code
- [ ] No sensitive data (secrets, tokens, PII) in logs
- [ ] Durations are measured and recorded for slow operations (>100ms)
- [ ] Tests verify that logs are emitted with correct fields

## Verification Commands

```bash
# Run tests and capture log output
npm test 2>&1 | grep -o '"service":"[^"]*"' | sort | uniq -c

# Check for sensitive patterns in logs (should find none)
npm test 2>&1 | grep -iE 'password|token|secret|api_key' || echo "Clean"

# Validate log schema (if using JSON Schema)
npm test 2>&1 | jq 'select(.level == "error")' | npm run validate:log-schema
```

## How to Recover if You Violate This Skill

If you add code without observability:
1. Identify the boundary layer (what service does it call?)
2. Add logging at entry, exit, and error paths
3. Ensure request_id is propagated
4. Add tests that verify logs are emitted
5. Re-run tests and confirm log output

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: List of boundary layers modified
- **Verification**: Include sample log output showing required fields
- **Key Decisions**: Explain which operations warrant logging
- **Results**: Confirm no sensitive data leaks; correlation IDs propagate end-to-end
