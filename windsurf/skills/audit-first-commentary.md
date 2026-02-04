# Skill: @audit-first-commentary

**Purpose:** Ensure all code includes detailed, meaningful, audit-ready commentary that explains intent, invariants, tradeoffs, and design decisions.

**Invocation:** `/use-skill audit-first-commentary` or automatic gate in all code reviews.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Part of code review; blocks merge if commentary insufficient.
- **Dependencies:** GLOBAL_RULES.md, other code context.
- **Owner:** Code quality team.

---

## Step-Based Instructions

### Step 1: Module-Level Documentation

Every module must have a top-level docstring describing purpose, key types, usage example, error handling, dependencies, and invariants.

**Example (TypeScript):**
```typescript
/**
 * JWT Authentication Module
 *
 * Provides secure JWT token validation with structured error handling and logging.
 * Tokens must be HS256-signed with a secret stored in HMAC_SECRET env var.
 *
 * Key Types:
 * - Claims: { userId: string, role: "admin" | "user", exp: number }
 * - JWTValidationError: Thrown when token is invalid, expired, or malformed
 *
 * Usage:
 *   import { validateJWT } from "./jwt";
 *   try {
 *     const claims = validateJWT(tokenString);
 *     console.log("User ID:", claims.userId);
 *   } catch (err) {
 *     if (err instanceof JWTValidationError && err.code === "TOKEN_EXPIRED") {
 *       // Handle expired token (e.g., redirect to login)
 *     }
 *   }
 *
 * Error Handling:
 * - JWTValidationError("token expired", "TOKEN_EXPIRED"): Token exp < now
 * - JWTValidationError("invalid signature", "INVALID_TOKEN"): Signature mismatch
 * - JWTValidationError("malformed token", "MALFORMED"): Not a valid JWT format
 *
 * Dependencies:
 * - jsonwebtoken (npm package): HS256 signing/verification
 * - logger (internal): Structured logging
 *
 * Invariants:
 * - exp field always a Unix timestamp (seconds)
 * - Claims.userId never null or empty string
 * - Errors always include errorCode for programmatic handling
 */
```

### Step 2: Function-Level Documentation

Every non-trivial function must have a docstring including: purpose, preconditions, postconditions, parameters, returns, throws/errors, side effects, and tradeoffs.

**Example:**
```typescript
/**
 * Validates a JWT token and extracts claims.
 *
 * Purpose: Verify token signature, check expiration, return decoded claims.
 *
 * Preconditions:
 * - token is a non-empty string
 * - HMAC_SECRET env var is set (or secret param provided for testing)
 * - Token format: Base64.URL(header).Base64.URL(payload).Base64.URL(signature)
 *
 * Postconditions:
 * - Returns Claims object with userId, role, exp fields
 * - exp field verified to be > now (token not expired)
 * - Signature verified with HMAC_SECRET
 *
 * @param token - JWT string, expected format header.payload.signature
 * @param secret - HMAC secret override (for testing); uses HMAC_SECRET env var if not provided
 * @param correlationId - Request ID for logging; generated if not provided
 *
 * Returns: Claims object: { userId, role, exp }. Never null; throws on any error.
 *
 * Throws:
 * - JWTValidationError("token expired", "TOKEN_EXPIRED") if exp < now
 * - JWTValidationError("invalid signature", "INVALID_TOKEN") if signature doesn't match
 * - JWTValidationError("malformed token", "MALFORMED") if not valid JWT format
 * - Error("HMAC_SECRET not configured") if secret not provided and env var not set
 *
 * Side Effects: Logs structured JSON (operation, status, userId, duration, errors)
 *
 * Tradeoff: Uses synchronous jwt.verify (blocks on computation). Alternative: async version
 * if called in hot path; cost is Promise overhead. Current choice suitable for auth middleware.
 */
export function validateJWT(token: string, secret?: string, correlationId?: string): Claims {
  // Implementation
}
```

### Step 3: Inline Comments for Complex Logic

Explain the "why" not the "what":

```typescript
// Increment i to process all tokens in the chain (not just the first)
i++;

// Admin users bypass cost limits; necessary for infra team to recover from incidents
if (user.role === "admin") {
  user.permissions.push("delete");
}

// Resolve hostname to IP to catch DNS rebinding attacks
// (attacker might have DNS return different IP on second lookup)
const ip = resolveHostSync(parsed.hostname);

// Check against deny list of private/reserved ranges
// SSRF attack vectors: localhost, private networks, cloud metadata
const denyList = [
  "127.0.0.1",
  "::1",
  /^10\./, // 10.0.0.0/8
  /^172\.(1[6-9]|2[0-9]|3[01])\./, // 172.16.0.0/12
];
```

### Step 4: Error Handling Documentation

Every error path documented:

```typescript
try {
  const result = await stripeClient.processCharge({ userId, amount, cardToken });
  logger.info("payment processed", { userId, amount, chargeId: result.id });
  return result;
} catch (err) {
  // Handle expected errors with domain-specific logic

  if (err instanceof Stripe.CardError) {
    // Card declined, invalid, or expired; user should retry with different card
    logger.warn("card error", { userId, code: err.code });
    throw new PaymentError("Card declined. Please try another card.", "CARD_DECLINED", { userMessage: true });
  }

  if (err instanceof Stripe.RateLimitError) {
    // Stripe API throttled; retry with backoff
    logger.warn("stripe rate limit", { userId });
    throw new PaymentError("Service temporarily busy. Please try again.", "RATE_LIMITED", { retryable: true });
  }

  // Unexpected error; log fully for debugging
  logger.error("payment failed", {
    userId,
    amount,
    errorType: err.constructor.name,
    errorMessage: err instanceof Error ? err.message : "unknown",
    stack: err instanceof Error ? err.stack : undefined,
  });
  throw new PaymentError("Payment failed. Contact support.", "UNKNOWN");
}
```

### Step 5: Design Decision Documentation

Document decision, why, alternatives considered, why chosen, and future reconsideration:

```typescript
/**
 * Token Refresh Strategy
 *
 * DECISION: Use short-lived access tokens (15 min) + long-lived refresh tokens (7 days).
 *
 * WHY:
 * - Short access tokens limit damage if token is compromised (15 min exposure window).
 * - Refresh tokens kept secure (httpOnly cookie); attacker needs to steal the cookie.
 * - Allows server to revoke access quickly (only invalidate refresh token on logout).
 *
 * ALTERNATIVES CONSIDERED:
 * 1. Single long-lived token (7 days):
 *    - Pro: Simpler (no refresh logic needed).
 *    - Con: If token leaked, attacker has access for 7 days (too risky).
 * 2. Session-based auth (server-side sessions):
 *    - Pro: Fine-grained revocation (immediately log out by invalidating session).
 *    - Con: Doesn't scale to multiple servers without shared session store (Redis overhead).
 *
 * CHOSEN BECAUSE:
 * - Balances security (short lived), scalability (no session store), and revocation.
 * - Fits our serverless architecture (no shared state).
 *
 * FUTURE RECONSIDERATION:
 * - If we move to monolithic server with Redis, session-based might be simpler.
 * - If token compromise becomes common, move to 5-min tokens.
 */
```

### Step 6: Review Checklist

During code review, verify:

- [ ] Module has top-level docstring (purpose, types, usage, dependencies, invariants).
- [ ] Every non-trivial function has docstring (purpose, preconditions, postconditions, parameters, returns, errors, side effects, tradeoffs).
- [ ] Inline comments explain "why" for complex logic (not just "what").
- [ ] Error paths documented (what each error means, how handled, what user sees).
- [ ] Design decisions documented (what, why, alternatives, future reconsideration).
- [ ] Terminology consistent with domain.
- [ ] No misleading comments (comments must match code).
- [ ] Security-relevant logic explicitly documented.

---

## Quality Checklist

- [ ] Module-level docstring present and complete.
- [ ] Function-level docstrings for all non-trivial functions.
- [ ] Inline comments explain "why" for complex logic.
- [ ] Error handling documented (each error type and how handled).
- [ ] Design decisions documented (decision, why, alternatives, future reconsideration).
- [ ] Terminology consistent throughout.
- [ ] No stale or misleading comments.
- [ ] Security-relevant logic explicitly documented.
- [ ] Preconditions and postconditions clear.
- [ ] Tradeoffs documented (current choice and why alternatives rejected).

---

## Deliverable Summary

```json
{
  "skill": "audit-first-commentary",
  "completed": true,
  "module_docstring": {
    "status": "complete",
    "includes": ["purpose", "key_types", "usage_example", "error_handling", "dependencies", "invariants"]
  },
  "function_docstrings": {
    "count": 5,
    "status": "all_complete",
    "includes": ["purpose", "preconditions", "postconditions", "parameters", "returns", "throws", "side_effects", "tradeoffs"]
  },
  "inline_comments": {
    "count": 8,
    "status": "all_complete"
  },
  "design_decisions": {
    "documented": true,
    "format": "DECISION/WHY/ALTERNATIVES/REASON/FUTURE_RECONSIDERATION"
  }
}
```

---

## Related Skills & Workflows

- @no-placeholders-production-code (ensures code is complete before documentation)
- @test-engineering-suite (test documentation complements code documentation)
- @debuggable-by-default (logging and error capture documentation)
- /pre-pr-review (code review includes documentation checks)
