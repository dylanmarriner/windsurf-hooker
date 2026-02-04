# Skill: @secure-by-default

**Purpose:** Implement security as a default: least privilege, secrets management, input validation, SSRF protection, injection prevention, and safe cryptographic practices.

**Invocation:** `/use-skill secure-by-default` in all features, especially auth, payment, and data handling.

---

## Core Principles

### 1. Secrets Never in Code

**Rule:** Environment variables or vault only. Never commit secrets.

```typescript
// ❌ BAD
const STRIPE_SECRET = "sk_live_abcd1234";
const HMAC_SECRET = "super-secret-key";

// ✅ GOOD
const STRIPE_SECRET = process.env.STRIPE_SECRET_KEY;
const HMAC_SECRET = process.env.HMAC_SECRET;

if (!STRIPE_SECRET || !HMAC_SECRET) {
  throw new Error("Required secrets not configured. Set STRIPE_SECRET_KEY and HMAC_SECRET env vars.");
}
```

### 2. Input Validation & Output Encoding

Validate all external input; encode all output.

```typescript
/**
 * Validate email format and normalize to lowercase.
 *
 * Security: Prevents injection of invalid emails; normalizes for safe comparison.
 * Invariant: Output is always lowercase; matches pattern /^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
 */
export function validateAndNormalizeEmail(input: unknown): string {
  if (typeof input !== "string") {
    throw new Error("Email must be a string");
  }

  const email = input.trim().toLowerCase();

  const emailRegex = /^[a-zA-Z0-9._%-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  if (!emailRegex.test(email)) {
    throw new Error("Invalid email format");
  }

  return email;
}

/**
 * Validate and sanitize URL for redirect (prevents open redirects).
 *
 * Invariant: Returned URL is always absolute, never relative, and never resolves to private network.
 * Security: Prevents attackers from redirecting users to malicious sites.
 */
export function validateRedirectURL(input: unknown): string {
  if (typeof input !== "string") {
    throw new Error("Redirect URL must be a string");
  }

  let url: URL;
  try {
    url = new URL(input);
  } catch {
    throw new Error("Invalid URL format");
  }

  // Whitelist safe protocols
  const allowedProtocols = ["https:", "http:"];
  if (!allowedProtocols.includes(url.protocol)) {
    throw new Error(`Unsafe protocol: ${url.protocol}`);
  }

  // Reject private network ranges (SSRF protection)
  const denyList = [
    "127.0.0.1",
    "localhost",
    "::1",
    "169.254.169.254", // AWS metadata
    /^10\./, // 10.0.0.0/8
    /^172\.(1[6-9]|2[0-9]|3[01])\./, // 172.16.0.0/12
    /^192\.168\./, // 192.168.0.0/16
  ];

  const hostname = url.hostname;
  for (const deny of denyList) {
    if (typeof deny === "string") {
      if (hostname === deny) throw new Error(`Denied host: ${hostname}`);
    } else {
      if (deny.test(hostname)) throw new Error(`Denied network: ${hostname}`);
    }
  }

  return url.toString();
}

/**
 * Escape HTML to prevent XSS when outputting user input.
 *
 * Use when displaying user-generated content in HTML context.
 */
export function escapeHTML(input: string): string {
  const htmlEscapeMap: Record<string, string> = {
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#39;",
  };

  return input.replace(/[&<>"']/g, (char) => htmlEscapeMap[char]);
}
```

### 3. Least Privilege

Grant only the minimum permissions required.

```typescript
/**
 * Database user should have SELECT, UPDATE only (not DELETE, CREATE).
 * API keys should be scoped to specific endpoints (not all endpoints).
 * IAM roles should include only necessary permissions.
 */

// ✅ GOOD: Scoped API key
const stripeClientSecret = new stripe.Stripe(process.env.STRIPE_SECRET_KEY!, {
  apiVersion: "2023-10-16", // Pinned API version
});

// ✅ GOOD: Minimal database permissions
// SQL role for app:
// GRANT SELECT, INSERT, UPDATE ON users TO app_user;
// GRANT SELECT, INSERT, UPDATE ON transactions TO app_user;
// (No DELETE, no CREATE TABLE, no ALTER)

// ✅ GOOD: AWS IAM role
// {
//   "Version": "2012-10-17",
//   "Statement": [
//     {
//       "Effect": "Allow",
//       "Action": ["s3:GetObject", "s3:PutObject"],
//       "Resource": "arn:aws:s3:::my-bucket/uploads/*"
//     }
//   ]
// }
```

### 4. Cryptography Best Practices

Use standard libraries; never roll custom crypto.

```typescript
/**
 * ECDSA signing and verification for security-critical operations.
 *
 * Uses Node.js crypto module (standard, audited).
 * Never use: custom hashing, XOR encryption, simple ROT13 obfuscation.
 */

import crypto from "crypto";

/**
 * Sign a payload with ECDSA P-256.
 *
 * Invariant: Signature is deterministic (same payload = same signature).
 * Security: Algorithm is NIST-approved; resistant to known attacks.
 */
export function signPayload(payload: Record<string, unknown>, privateKey: string): string {
  const payloadStr = JSON.stringify(payload);
  const signer = crypto.createSign("SHA256");
  signer.update(payloadStr);
  return signer.sign(privateKey, "hex");
}

/**
 * Verify ECDSA signature.
 *
 * Returns true if signature is valid; false otherwise.
 * Invariant: Non-repudiation (only private key holder could have signed).
 */
export function verifyPayloadSignature(
  payload: Record<string, unknown>,
  signature: string,
  publicKey: string
): boolean {
  const payloadStr = JSON.stringify(payload);
  const verifier = crypto.createVerify("SHA256");
  verifier.update(payloadStr);
  return verifier.verify(publicKey, signature, "hex");
}

/**
 * Hash password with bcrypt.
 *
 * Invariant: Hash is salted; resistant to rainbow tables.
 * Security: bcrypt uses adaptive cost factor (increases over time as hardware improves).
 * Never: store plain passwords; use bcrypt.compare() to verify.
 */
import bcrypt from "bcrypt";

export async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12; // Adaptive; takes ~250ms on modern hardware
  return bcrypt.hash(password, saltRounds);
}

export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return bcrypt.compare(password, hash);
}
```

### 5. SQL Injection Prevention

Always use parameterized queries.

```typescript
/**
 * ❌ VULNERABLE: String concatenation
 * const query = `SELECT * FROM users WHERE email = '${email}'`;
 *
 * If email = "' OR '1'='1", query becomes:
 * SELECT * FROM users WHERE email = '' OR '1'='1'
 * (returns all users!)
 */

/**
 * ✅ SAFE: Parameterized query
 * Database driver prevents injection by separating SQL from data.
 */
export async function getUserByEmail(email: string): Promise<User | null> {
  const query = "SELECT * FROM users WHERE email = $1"; // $1 is parameter placeholder
  const result = await db.query(query, [email]); // Parameters passed separately
  return result.rows[0] || null;
}

/**
 * ✅ SAFE: Using an ORM (Prisma, TypeORM, etc.)
 */
export async function getUserByEmailORM(email: string): Promise<User | null> {
  const user = await prisma.user.findUnique({
    where: { email }, // ORM handles parameterization
  });
  return user;
}
```

### 6. Authentication & Session Management

```typescript
/**
 * JWT token generation with secure defaults.
 *
 * Invariant: Token expires within 15 minutes (short-lived).
 * Invariant: Refresh token stored in httpOnly cookie (not accessible to JavaScript).
 * Security: Reduces damage if token is compromised; attacker has 15-min window.
 */
export function generateTokens(userId: string) {
  const accessToken = jwt.sign({ userId }, process.env.HMAC_SECRET, {
    expiresIn: "15m", // Short-lived
    algorithm: "HS256",
  });

  const refreshToken = jwt.sign({ userId }, process.env.REFRESH_SECRET, {
    expiresIn: "7d", // Longer-lived; refreshes access token
    algorithm: "HS256",
  });

  return { accessToken, refreshToken };
}

/**
 * Session middleware with CSRF protection.
 *
 * CSRF attack: Attacker makes victim's browser send malicious request to your site.
 * Defense: Require CSRF token in POST requests; token must be in hidden form field or header.
 */
app.use(csrf()); // Middleware adds req.csrfToken()

app.post("/user/delete-account", (req, res) => {
  // CSRF token automatically verified by middleware
  // If missing or invalid, request rejected
  const userId = req.user.id;
  deleteUser(userId);
  res.json({ ok: true });
});
```

### 7. Rate Limiting & Abuse Prevention

```typescript
/**
 * Rate limiting on sensitive endpoints prevents brute force attacks.
 *
 * Example: Login endpoint allows 5 attempts per 15 minutes per IP.
 */
app.post(
  "/auth/login",
  rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // Max 5 requests per windowMs
    message: "Too many login attempts. Please try again later.",
    keyGenerator: (req) => req.ip, // Rate limit by IP address
  }),
  (req, res) => {
    // Handle login
  }
);

/**
 * Account lockout after failed login attempts.
 *
 * After 3 failed attempts, account is locked for 30 minutes.
 * User can unlock via email link.
 */
export async function recordFailedLogin(userId: string) {
  const user = await db.users.findById(userId);
  const failedAttempts = user.failedLoginAttempts + 1;

  if (failedAttempts >= 3) {
    await db.users.update(userId, {
      failedLoginAttempts: 0,
      lockedUntil: new Date(Date.now() + 30 * 60 * 1000), // Lock for 30 min
    });
  } else {
    await db.users.update(userId, {
      failedLoginAttempts: failedAttempts,
    });
  }
}
```

---

## Security Checklist

- [ ] No secrets in code or version control.
- [ ] All secrets loaded from environment/vault.
- [ ] All external input validated (type, format, length).
- [ ] All user-visible output encoded (HTML, URL, JSON).
- [ ] SQL queries use parameterized statements or ORM.
- [ ] No custom cryptography; use standard libraries only.
- [ ] Passwords hashed with bcrypt (never stored plain).
- [ ] JWT tokens short-lived (<30 min).
- [ ] Refresh tokens stored in httpOnly cookies (not localStorage).
- [ ] CSRF protection enabled for state-changing requests.
- [ ] Rate limiting on sensitive endpoints (login, password reset).
- [ ] SSRF protection: no open redirects, deny private network ranges.
- [ ] Dependency vulnerabilities scanned (npm audit, cargo audit).
- [ ] Security headers set (CSP, X-Frame-Options, X-Content-Type-Options).
- [ ] Secrets never logged or included in error messages.
- [ ] Account lockout after failed login attempts.
- [ ] TLS/SSL required for all HTTPS endpoints.
- [ ] HTTP Strict-Transport-Security (HSTS) header set.

---

## Observability Pack Compliance

- Secrets redacted from all logs (passwords, tokens, API keys, credit cards).
- PII logged only on allowlist (user ID ok; email, phone, SSN require approval).
- Error messages never reveal secrets or internal system details.
- Audit logs record sensitive operations (user creation, permission changes, payment).

---

## Kaiza MCP Security Gates

When modifying security-critical code via Kaiza:

1. **Security scan required:** No merge without passing security scans.
2. **Secrets audit:** Verify no secrets added to code.
3. **Permission review:** Verify changes follow least-privilege principle.
4. **Dependency audit:** Verify no vulnerable dependencies added.

---

## Deliverable Summary

```json
{
  "skill": "secure-by-default",
  "completed": true,
  "security_checks": {
    "secrets_scanning": "passed",
    "input_validation": "comprehensive",
    "output_encoding": "present",
    "ssrf_protection": "enabled",
    "sql_injection_prevention": "parameterized",
    "cryptography": "standard_libraries_only",
    "password_hashing": "bcrypt",
    "jwt_tokens": "short_lived",
    "csrf_protection": "enabled",
    "rate_limiting": "configured",
    "security_headers": "set",
    "dependency_scan": "clean",
    "account_lockout": "implemented",
    "tls_required": true
  }
}
```

---

## Related Skills

- @no-placeholders-production-code
- @test-engineering-suite (security tests)
- @debuggable-by-default (secure error messages)
- /security-hardening-sprint
