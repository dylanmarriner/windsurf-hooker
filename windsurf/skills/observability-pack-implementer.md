# Skill: @observability-pack-implementer

**Purpose:** Implement standardized observability across code: structured logging, distributed tracing, metrics, and diagnostics that enable fast debugging and production monitoring.

**Invocation:** `/use-skill observability-pack-implementer` in all services and critical paths.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** When implementing features with I/O, auth, payments, or critical paths.
- **Dependencies:** @debuggable-by-default, @audit-first-commentary.
- **Owner:** Observability team.

---

## Observability Pack Components

### 1. Structured Logging Schema

Every log entry must include:

```json
{
  "timestamp": "2026-01-15T10:30:45.123Z",
  "level": "info",
  "message": "user authenticated",
  "service": "auth-service",
  "env": "production",
  "version": "1.2.3",
  "requestId": "req-abc123",
  "traceId": "trace-def456",
  "spanId": "span-ghi789",
  "userId": "user-123",
  "operation": "validateJWT",
  "duration_ms": 5,
  "status": "success"
}
```

**Required fields (every log):**
- `timestamp`: ISO 8601, UTC
- `level`: "debug", "info", "warn", "error"
- `message`: Concise, max 200 chars, human-readable
- `service`: Service name (auth-service, payment-service, api-gateway)
- `env`: "development", "staging", "production"
- `version`: App version (from package.json or env var)
- `requestId`: Correlation ID for tracing requests

**Contextual fields (when applicable):**
- `userId`: User ID (when user is authenticated)
- `traceId`, `spanId`: Distributed trace IDs
- `operation`: Function/step name
- `duration_ms`: Time taken (for performance monitoring)
- `status`: "success", "error", "in_progress"
- Error fields (for errors only): `errorCode`, `errorMessage`, `stack`

**Implementation:**

```typescript
class StructuredLogger {
  constructor(
    private context: {
      service: string;
      version: string;
      env: string;
      requestId: string;
      traceId?: string;
      userId?: string;
    }
  ) {}

  info(message: string, data?: Record<string, unknown>) {
    console.log(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        level: "info",
        message,
        service: this.context.service,
        env: this.context.env,
        version: this.context.version,
        requestId: this.context.requestId,
        traceId: this.context.traceId,
        userId: this.context.userId,
        ...this.redactSecrets(data || {}),
      })
    );
  }

  error(message: string, err?: Error, data?: Record<string, unknown>) {
    console.error(
      JSON.stringify({
        timestamp: new Date().toISOString(),
        level: "error",
        message,
        errorCode: data?.errorCode || "UNKNOWN",
        errorMessage: err?.message,
        stack: err?.stack,
        service: this.context.service,
        env: this.context.env,
        version: this.context.version,
        requestId: this.context.requestId,
        userId: this.context.userId,
        ...this.redactSecrets(data || {}),
      })
    );
  }

  private redactSecrets(data: Record<string, unknown>): Record<string, unknown> {
    const secretFields = ["password", "token", "secret", "apiKey", "creditCard"];
    const redacted = { ...data };

    for (const key in redacted) {
      if (secretFields.some((s) => key.toLowerCase().includes(s.toLowerCase()))) {
        redacted[key] = "[REDACTED]";
      }
    }

    return redacted;
  }
}
```

### 2. Correlation ID Propagation

IDs must flow through all operations (HTTP, databases, message queues, etc.):

```typescript
/**
 * Generate correlation ID on request entry
 */
app.use((req, res, next) => {
  const requestId = req.headers["x-request-id"] || generateRequestId();
  const traceId = req.headers["x-trace-id"] || generateTraceId();

  // Store in async context so all nested calls can access
  asyncLocalStorage.run({ requestId, traceId }, () => next());
});

/**
 * Propagate through outbound HTTP calls
 */
async function callExternalAPI(endpoint: string) {
  const { requestId, traceId } = getAsyncLocalStorage();

  const response = await fetch(endpoint, {
    headers: {
      "X-Request-ID": requestId,
      "X-Trace-ID": traceId,
    },
  });

  return response;
}

/**
 * Propagate through database calls
 */
async function getUserById(userId: string) {
  const { requestId, traceId } = getAsyncLocalStorage();

  const logger = createLogger({ requestId, traceId });
  logger.info("querying user by id", { userId });

  const user = await prisma.user.findUnique({
    where: { id: userId },
  });

  logger.info("user found", { userId, name: user?.name });
  return user;
}

/**
 * Propagate through message queues
 */
async function publishEvent(eventName: string, data: unknown) {
  const { requestId, traceId } = getAsyncLocalStorage();

  await messageQueue.publish(eventName, {
    ...data,
    _metadata: {
      requestId,
      traceId,
      timestamp: new Date().toISOString(),
    },
  });
}

/**
 * Consume from queue and restore context
 */
messageQueue.on(eventName, async (event) => {
  const { requestId, traceId } = event._metadata;

  asyncLocalStorage.run({ requestId, traceId }, async () => {
    // Handle event with context restored
  });
});
```

### 3. Distributed Tracing

Spans represent individual operations; trace represents full request:

```typescript
/**
 * Wrapper for any operation that should be traced
 */
function withSpan<T>(
  spanName: string,
  attributes: Record<string, unknown>,
  fn: () => T | Promise<T>
): T | Promise<T> {
  const { requestId, traceId } = getAsyncLocalStorage() || {};
  const spanId = generateSpanId();
  const startTime = performance.now();
  const logger = createLogger({ requestId, traceId });

  try {
    logger.debug("span_start", {
      operation: spanName,
      spanId,
      attributes,
    });

    const result = fn();

    // Handle async result
    if (result instanceof Promise) {
      return result
        .then((value) => {
          const duration = performance.now() - startTime;
          logger.debug("span_end", {
            operation: spanName,
            spanId,
            duration_ms: duration,
            status: "success",
          });
          return value;
        })
        .catch((err) => {
          const duration = performance.now() - startTime;
          logger.error("span_error", err, {
            operation: spanName,
            spanId,
            duration_ms: duration,
            errorCode: err?.code || "UNKNOWN",
          });
          throw err;
        });
    }

    // Handle sync result
    const duration = performance.now() - startTime;
    logger.debug("span_end", {
      operation: spanName,
      spanId,
      duration_ms: duration,
      status: "success",
    });

    return result;
  } catch (err) {
    const duration = performance.now() - startTime;
    logger.error("span_error", err as Error, {
      operation: spanName,
      spanId,
      duration_ms: duration,
    });
    throw err;
  }
}

// Usage
export async function validateJWT(token: string): Promise<Claims> {
  return withSpan("validateJWT", { tokenLength: token.length }, async () => {
    // Validation logic
  });
}

export async function processPayment(
  userId: string,
  amount: number
): Promise<PaymentResult> {
  return withSpan("processPayment", { userId, amount }, async () => {
    // Payment logic
  });
}
```

### 4. Metrics & Key Indicators

Track RED metrics (Rate, Errors, Duration) and business metrics:

```typescript
/**
 * Metrics collection via logs (metrics backend parses these)
 */

class MetricsCollector {
  recordRequest(
    operation: string,
    status: "success" | "error",
    duration_ms: number,
    attributes?: Record<string, unknown>
  ) {
    const logger = getLogger();

    logger.info("request_metric", {
      operation,
      status,
      duration_ms,
      ...attributes,
    });
  }

  recordPayment(status: "success" | "failed", amount: number, duration_ms: number) {
    const logger = getLogger();

    logger.info("payment_metric", {
      operation: "processPayment",
      status,
      amount,
      duration_ms,
    });
  }
}

// Usage
const metrics = new MetricsCollector();

app.get("/api/users/:id", async (req, res) => {
  const startTime = performance.now();
  try {
    const user = await getUser(req.params.id);
    const duration = performance.now() - startTime;

    metrics.recordRequest("getUser", "success", duration, {
      userId: user.id,
    });

    res.json(user);
  } catch (err) {
    const duration = performance.now() - startTime;
    metrics.recordRequest("getUser", "error", duration, {
      errorCode: err?.code || "UNKNOWN",
    });

    res.status(500).json({ error: "Internal server error" });
  }
});

/**
 * Example metrics to track:
 *
 * RED Metrics (for every endpoint/operation):
 * - Rate: requests per second
 * - Errors: error rate (errors / total requests)
 * - Duration: latency (p50, p95, p99)
 *
 * Business Metrics:
 * - Payment success rate
 * - User registration rate
 * - API endpoint usage distribution
 * - Error rate by error code
 *
 * Infrastructure Metrics:
 * - Database connection pool usage
 * - Memory usage
 * - CPU usage
 * - Disk space remaining
 */
```

### 5. Redaction Policy

Never log PII or secrets:

```typescript
/**
 * Redaction rules:
 *
 * NEVER LOG:
 * - Passwords, tokens, API keys, credit cards
 * - SSN, driver's license, passport numbers
 * - Full email addresses (except on allowlist for support)
 * - Full phone numbers
 *
 * SAFE TO LOG:
 * - User ID (internal identifier, not PII)
 * - Request ID / trace ID (for correlation)
 * - Error codes and messages (non-technical)
 * - HTTP method, path, status code
 * - Duration of operations
 * - Feature flags / experiment assignments
 */

class RedactionPolicy {
  static ALLOW_LIST = [
    "userId",
    "requestId",
    "traceId",
    "spanId",
    "operation",
    "duration_ms",
    "status",
    "errorCode",
    "errorMessage",
    "message",
    "level",
    "timestamp",
    "service",
    "env",
    "version",
  ];

  static DENY_PATTERNS = [
    /password/i,
    /token/i,
    /secret/i,
    /apiKey/i,
    /creditCard/i,
    /ssn/i,
    /driverLicense/i,
    /passport/i,
    /email/i,
    /phone/i,
  ];

  static shouldLog(key: string, value: unknown): boolean {
    // Redact if matches deny pattern
    if (this.DENY_PATTERNS.some((pattern) => pattern.test(key))) {
      return false;
    }

    // Log if in allow list or doesn't match deny pattern
    return true;
  }

  static redact(data: Record<string, unknown>): Record<string, unknown> {
    const redacted = { ...data };

    for (const key in redacted) {
      if (!this.shouldLog(key, redacted[key])) {
        redacted[key] = "[REDACTED]";
      }
    }

    return redacted;
  }
}

// Usage
logger.info("user login attempt", RedactionPolicy.redact({
  userId: "user-123",          // Logged
  email: "user@example.com",   // Redacted (email)
  password: "secret123",        // Redacted (password)
  ipAddress: "192.168.1.1",    // Logged
  userAgent: "Mozilla/5.0...", // Logged
}));

// Output:
// {"userId": "user-123", "email": "[REDACTED]", "password": "[REDACTED]", "ipAddress": "192.168.1.1", ...}
```

### 6. Debug Toggles & Diagnostic Endpoints

```typescript
/**
 * Feature flags for enabling debug logging (safe in production)
 */

const DEBUG_FLAGS = {
  jwt: false,
  database: false,
  http: false,
  payment: false,
};

/**
 * Endpoint to toggle debug flags (protected by admin auth)
 */
app.post("/admin/debug", requireAdminAuth, (req, res) => {
  const { flag, value } = req.body;

  if (flag in DEBUG_FLAGS && typeof value === "boolean") {
    DEBUG_FLAGS[flag] = value;
    res.json({ ok: true, flag, value });
  } else {
    res.status(400).json({ error: "Invalid flag or value" });
  }
});

/**
 * Diagnostic endpoint (protected by admin auth)
 */
app.get("/admin/diagnostics", requireAdminAuth, (req, res) => {
  const logger = getLogger();

  logger.info("diagnostics_requested");

  res.json({
    timestamp: new Date().toISOString(),
    uptime_seconds: process.uptime(),
    memory: process.memoryUsage(),
    debug_flags: DEBUG_FLAGS,
    active_requests: getActiveRequestCount(),
    db_pool: getConnectionPoolStats(),
    recent_errors: getRecentErrorsList(10),
  });
});

/**
 * Usage in code:
 */
export function validateJWT(token: string): Claims {
  if (DEBUG_FLAGS.jwt) {
    const [header, payload, signature] = token.split(".");
    const logger = getLogger();

    logger.debug("jwt_debug", {
      header_decoded: Buffer.from(header, "base64url").toString("utf-8"),
      payload_decoded: Buffer.from(payload, "base64url").toString("utf-8"),
    });
  }

  // Validation logic
}
```

---

## Implementation Checklist

- [ ] Structured logging schema implemented.
- [ ] Correlation IDs generated and propagated.
- [ ] All secrets redacted from logs.
- [ ] PII logged only on allowlist.
- [ ] Span tagging in place for tracing.
- [ ] Distributed tracing integration (trace IDs passed between services).
- [ ] RED metrics collected (Rate, Errors, Duration).
- [ ] Debug toggles available (safe in production).
- [ ] Diagnostics endpoint implemented (protected).
- [ ] Health/readiness checks implemented.
- [ ] Logs aggregation configured (send logs to centralized system).

---

## Quality Checklist

- [ ] All significant operations have structured JSON logging.
- [ ] Correlation IDs flow through entire request lifecycle.
- [ ] No secrets or PII in logs (redaction policy enforced).
- [ ] Error logs include stack traces, error codes, and context.
- [ ] Metrics cover RED (Rate, Errors, Duration) indicators.
- [ ] Debug flags available for deep troubleshooting.
- [ ] Diagnostics endpoints available (protected).
- [ ] Traces can be correlated across services (via trace IDs).
- [ ] Logs are structured (JSON, parseable).

---

## Deliverable Summary

```json
{
  "skill": "observability-pack-implementer",
  "completed": true,
  "components_implemented": {
    "structured_logging": true,
    "correlation_id_propagation": true,
    "distributed_tracing": true,
    "metrics_collection": true,
    "redaction_policy": true,
    "debug_toggles": true,
    "diagnostics_endpoints": true
  },
  "logging": {
    "format": "JSON",
    "required_fields": [
      "timestamp",
      "level",
      "message",
      "service",
      "env",
      "version",
      "requestId"
    ],
    "secrets_redacted": true,
    "pii_allowlist_enforced": true
  },
  "tracing": {
    "correlation_ids": "generated_and_propagated",
    "trace_ids": "flow_across_services",
    "span_tagging": "implemented"
  },
  "metrics": {
    "red_metrics": "collected",
    "business_metrics": "tracked",
    "infrastructure_metrics": "monitored"
  },
  "debug_features": {
    "toggles": "available",
    "diagnostics_endpoint": "protected_by_auth",
    "health_checks": "implemented"
  }
}
```

---

## Related Skills

- @debuggable-by-default (foundation: logging and error capture)
- @audit-first-commentary (documenting observability)
- /triage-prod-issue (uses observability data to diagnose issues)
