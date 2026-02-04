# Skill: @debuggable-by-default

**Purpose:** Ensure all code includes comprehensive debugging features: structured logging, assertions, diagnostics endpoints, and error capture that make failures reproducible and root causes findable.

**Invocation:** `/use-skill debuggable-by-default` or automatic in all code.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Part of development; verified in code review.
- **Dependencies:** @audit-first-commentary, @observability-pack-implementer.
- **Owner:** Observability team.

---

## Core Logging Pattern

### Structured JSON Logging

Every significant operation logs structured JSON with required fields:

```typescript
interface LogEntry {
  timestamp: string; // ISO 8601
  level: "debug" | "info" | "warn" | "error";
  message: string; // Human-readable, max 200 chars
  service: string; // e.g., "auth-service"
  env: string; // "development" | "staging" | "production"
  version: string; // App version
  requestId: string; // Correlation ID
  userId?: string; // When applicable
  operation?: string; // Function/step name
  duration_ms?: number; // For timed operations
  errorCode?: string; // Machine-readable error identifier
  errorMessage?: string; // Error message
  stack?: string; // Stack trace
  [key: string]: unknown; // Event-specific fields
}
```

### Logger Implementation

```typescript
class StructuredLogger {
  constructor(
    private context: {
      service: string;
      version: string;
      env: string;
      requestId: string;
      userId?: string;
    }
  ) {}

  private redactSecrets(obj: Record<string, unknown>): Record<string, unknown> {
    const redacted = { ...obj };
    const secretFields = ["password", "token", "secret", "apiKey", "Authorization", "creditCard"];

    for (const key in redacted) {
      if (secretFields.some((s) => key.toLowerCase().includes(s.toLowerCase()))) {
        redacted[key] = "[REDACTED]";
      }
    }

    return redacted;
  }

  private formatLog(level: string, message: string, data?: Record<string, unknown>): LogEntry {
    return {
      timestamp: new Date().toISOString(),
      level: level as any,
      message,
      service: this.context.service,
      env: this.context.env,
      version: this.context.version,
      requestId: this.context.requestId,
      userId: this.context.userId,
      ...this.redactSecrets(data || {}),
    };
  }

  debug(message: string, data?: Record<string, unknown>) {
    console.log(JSON.stringify(this.formatLog("debug", message, data)));
  }

  info(message: string, data?: Record<string, unknown>) {
    console.log(JSON.stringify(this.formatLog("info", message, data)));
  }

  warn(message: string, data?: Record<string, unknown>) {
    console.error(JSON.stringify(this.formatLog("warn", message, data)));
  }

  error(message: string, data?: Record<string, unknown>) {
    console.error(JSON.stringify(this.formatLog("error", message, data)));
  }
}
```

### Correlation ID Propagation

Every request gets a unique correlation ID, passed through all function calls:

```typescript
// Incoming request (Express middleware)
app.use((req, res, next) => {
  const requestId = req.headers["x-request-id"] || generateRequestId();
  asyncLocalStorage.run({ requestId }, () => next());
});

// Function signature: include correlationId parameter
export function validateJWT(token: string, secret?: string, correlationId?: string): Claims {
  const actualCorrelationId = correlationId || getFromAsyncLocalStorage()?.requestId;
  const logger = createLogger({ requestId: actualCorrelationId });
  // ... implementation logs everything with actualCorrelationId
}

// Propagate through outbound calls
async function callExternalAPI(endpoint: string, correlationId: string) {
  const response = await fetch(endpoint, {
    headers: { "X-Request-ID": correlationId },
  });
}
```

---

## Assertion & Invariant Checking

### Production-Safe Assertions

```typescript
function assert(
  condition: boolean,
  message: string,
  context?: Record<string, unknown>
): asserts condition {
  if (!condition) {
    const logger = getLogger();
    logger.error("assertion_failed", { message, ...context });

    if (process.env.NODE_ENV === "development") {
      throw new AssertionError(message);
    }
  }
}

// Usage
export function processUser(user: User) {
  assert(user.userId && user.userId.length > 0, "user.userId must be non-empty", {
    user: { id: user.id, email: user.email },
  });

  assert(user.email === user.email.toLowerCase(), "user.email must be lowercase", {
    email: user.email,
  });
}
```

### Diagnostic Functions

```typescript
export function createDiagnosticSnapshot(): DiagnosticSnapshot {
  return {
    timestamp: new Date().toISOString(),
    memory: process.memoryUsage(),
    uptime_ms: process.uptime() * 1000,
    active_requests: getActiveRequestCount(),
    recent_errors: getRecentErrorsList(10),
    pending_operations: getPendingOperationsCount(),
    db_connection_pool: getConnectionPoolStats(),
  };
}

// Diagnostics endpoint
app.get("/diagnostics", (req, res) => {
  if (!isAuthorizedForDiagnostics(req)) {
    return res.status(403).send("Forbidden");
  }
  res.json(createDiagnosticSnapshot());
});
```

---

## Error Capture & Reproduction

### Rich Error Objects

```typescript
export class DomainError extends Error {
  constructor(
    public userMessage: string,
    public errorCode: string,
    public context: Record<string, unknown> = {},
    public originalError?: Error
  ) {
    super(userMessage);
    this.name = "DomainError";
  }

  toJSON() {
    return {
      name: this.name,
      userMessage: this.userMessage,
      errorCode: this.errorCode,
      context: this.context,
      message: this.message,
      stack: this.stack,
      originalError: this.originalError
        ? { message: this.originalError.message, stack: this.originalError.stack }
        : undefined,
    };
  }
}

// Usage
async function processPayment(
  userId: string,
  amount: number,
  cardToken: string,
  attemptNumber: number = 1
): Promise<PaymentResult> {
  try {
    return await stripeClient.charge({ userId, amount, cardToken });
  } catch (err) {
    if (err instanceof Stripe.CardError) {
      throw new DomainError(
        "Card declined. Please try another card.",
        "CARD_DECLINED",
        { userId, amount, attemptNumber, cardErrorCode: err.code },
        err
      );
    }
    throw new DomainError(
      "Payment processing failed. Please try again.",
      "PAYMENT_FAILED",
      { userId, amount, attemptNumber },
      err instanceof Error ? err : undefined
    );
  }
}
```

### Minimal Repro Tests

```typescript
test("repro: issue #1234 - malformed token throws with MALFORMED code", async () => {
  const malformedToken = "not.a.valid.jwt";

  expect(() => validateJWT(malformedToken, "secret")).toThrow(
    expect.objectContaining({
      code: "MALFORMED",
    })
  );
});
```

---

## Feature Flags & Debug Toggles

### Safe Debug Toggles

```typescript
const debugFlags = {
  jwt: false,
  database: false,
  http: false,
  memory: false,
};

// Endpoint to toggle (protected by auth)
app.post("/admin/debug", requireAdminAuth, (req, res) => {
  const { flag, value } = req.body;
  if (flag in debugFlags && typeof value === "boolean") {
    debugFlags[flag] = value;
    res.json({ ok: true, flag, value });
  } else {
    res.status(400).json({ error: "Invalid flag or value" });
  }
});

// Usage
export function validateJWT(token: string, secret?: string): Claims {
  if (debugFlags.jwt) {
    const [header, payload, signature] = token.split(".");
    console.log("JWT parts", {
      headerDecoded: Buffer.from(header, "base64url").toString("utf-8"),
      payloadDecoded: Buffer.from(payload, "base64url").toString("utf-8"),
    });
  }
  // ... rest
}
```

### Log Level Overrides

```typescript
const logLevelOverrides = new Map<string, string>();

function parseDebugModules() {
  const modules = process.env.DEBUG_MODULES?.split(",") || [];
  for (const module of modules) {
    const [name, level] = module.split(":");
    if (name && level && ["debug", "info", "warn", "error"].includes(level)) {
      logLevelOverrides.set(name, level);
    }
  }
}

function shouldLog(module: string, level: string): boolean {
  const levels = ["debug", "info", "warn", "error"];
  const overrideLevel = logLevelOverrides.get(module);
  const configuredLevel = overrideLevel || (process.env.LOG_LEVEL || "info");
  return levels.indexOf(level) >= levels.indexOf(configuredLevel);
}
```

---

## Tracing Hooks

### Span Tagging

```typescript
function withSpan<T>(
  spanName: string,
  attributes: Record<string, unknown>,
  fn: () => T
): T {
  const startTime = performance.now();
  const logger = getLogger();

  try {
    logger.debug("span_start", { spanName, attributes });
    const result = fn();
    const duration = performance.now() - startTime;
    logger.debug("span_end", { spanName, duration_ms: duration, status: "ok" });
    return result;
  } catch (err) {
    const duration = performance.now() - startTime;
    logger.error("span_error", {
      spanName,
      duration_ms: duration,
      status: "error",
      errorCode: err instanceof DomainError ? err.errorCode : "UNKNOWN",
      errorMessage: err instanceof Error ? err.message : "unknown",
    });
    throw err;
  }
}

// Usage
export function validateJWT(token: string, secret?: string): Claims {
  return withSpan("validateJWT", { token_length: token.length }, () => {
    // ... validation logic
  });
}
```

### Distributed Tracing

```typescript
function createTraceContext(existingTraceId?: string) {
  return {
    traceId: existingTraceId || generateTraceId(),
    spanId: generateSpanId(),
    parentSpanId: undefined,
  };
}

app.use((req, res, next) => {
  const traceContext = createTraceContext(req.headers["x-trace-id"] as string);
  asyncLocalStorage.run(traceContext, () => next());
});

async function callAuthService(endpoint: string) {
  const traceContext = getTraceContext();
  const response = await fetch(endpoint, {
    headers: {
      "X-Trace-Id": traceContext.traceId,
      "X-Span-Id": traceContext.spanId,
    },
  });
  return response;
}
```

---

## Production Debugging

### Error Recovery with Context

```typescript
async function retryWithBackoff<T>(
  operation: () => Promise<T>,
  maxAttempts: number = 3,
  initialDelayMs: number = 100
): Promise<T> {
  const logger = getLogger();

  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      logger.debug("attempt", { attempt, maxAttempts });
      return await operation();
    } catch (err) {
      const isLastAttempt = attempt === maxAttempts;
      const delayMs = initialDelayMs * Math.pow(2, attempt - 1);

      logger.warn("attempt_failed", {
        attempt,
        isLastAttempt,
        errorMessage: err instanceof Error ? err.message : "unknown",
        nextRetryDelayMs: isLastAttempt ? undefined : delayMs,
      });

      if (isLastAttempt) throw err;
      await new Promise((r) => setTimeout(r, delayMs));
    }
  }
  throw new Error("unreachable");
}
```

### Health Checks

```typescript
app.get("/health", (req, res) => {
  const checks = {
    database: checkDatabaseConnection(),
    cache: checkCacheConnection(),
    disk: checkDiskSpace(),
  };

  const allHealthy = Object.values(checks).every((v) => v.status === "healthy");

  res.status(allHealthy ? 200 : 503).json({
    status: allHealthy ? "healthy" : "degraded",
    timestamp: new Date().toISOString(),
    checks,
  });
});

app.get("/ready", (req, res) => {
  if (isInitializationComplete() && !isShuttingDown()) {
    res.json({ ready: true });
  } else {
    res.status(503).json({ ready: false, reason: "startup in progress" });
  }
});
```

---

## Quality Checklist

- [ ] All significant operations have structured JSON logging.
- [ ] Correlation IDs generated and propagated through all calls.
- [ ] All secrets redacted from logs (passwords, tokens, API keys).
- [ ] PII logged only on allowlist (user ID ok, email/address only if necessary).
- [ ] Assertions check invariants at critical points.
- [ ] Rich error objects include userMessage, errorCode, context.
- [ ] Minimal repro tests for all bugfixes.
- [ ] Debug flags/toggles available for deep troubleshooting.
- [ ] Log level overrides work (DEBUG_MODULES env var).
- [ ] Diagnostics endpoint available (protected).
- [ ] Health/readiness probes implemented.
- [ ] Span tagging in place for tracing.
- [ ] Error recovery (retry logic) logs each attempt.

---

## Deliverable Summary

```json
{
  "skill": "debuggable-by-default",
  "completed": true,
  "structured_logging": {
    "coverage": "100%",
    "logs_with_correlation_id": true,
    "secrets_redacted": true,
    "pii_allowlist_enforced": true
  },
  "assertions": {
    "count": 5,
    "safe_in_production": true
  },
  "error_capture": {
    "rich_error_objects": true,
    "minimal_repro_tests": true
  },
  "debug_features": {
    "feature_flags": true,
    "log_level_overrides": true,
    "diagnostics_endpoint": true,
    "health_checks": true,
    "readiness_probes": true
  },
  "tracing": {
    "span_tagging": true,
    "correlation_id_propagation": true,
    "distributed_tracing_ready": true
  }
}
```

---

## Related Skills

- @observability-pack-implementer (logging schema spec)
- @audit-first-commentary (documentation of debugging features)
- @test-engineering-suite (minimal repro test patterns)
- /triage-prod-issue (uses debugging features to diagnose issues)
