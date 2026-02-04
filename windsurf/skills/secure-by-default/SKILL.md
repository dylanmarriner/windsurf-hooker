---
name: secure-by-default
description: Write code that enforces security guardrails by default with input validation, least privilege, and redaction. Invoke as @secure-by-default.
---

# Skill: Secure by Default

## Purpose
Security should be automatic, not optional. Every piece of code should validate inputs, respect privilege boundaries, redact secrets, and fail safely when security constraints are violated.

## When to Use This Skill
- Handling user input (forms, API payloads, file uploads)
- Authenticating or authorizing requests
- Storing or transmitting secrets
- Building SQL queries or file paths
- Implementing access controls
- Creating cryptographic operations

## Steps

### 1) Validate all external input
At every boundary (HTTP, form, file upload, API response), validate:
- Type: is it the expected type? (string, number, array, object)
- Format: does it match the expected format? (email, UUID, JSON)
- Length: is it within acceptable bounds? (max 10000 chars for a username)
- Content: does it contain only allowed characters?

Example (JavaScript):
```javascript
function validateEmail(email) {
  // Type check
  if (typeof email !== 'string') {
    throw new Error('Email must be a string');
  }
  // Length check
  if (email.length > 254) {
    throw new Error('Email too long');
  }
  // Format check (basic regex, not RFC compliant)
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    throw new Error('Invalid email format');
  }
  return email;
}

// Use it
const email = validateEmail(req.body.email);
```

Example (Python):
```python
import re
from typing import str

def validate_email(email: str) -> str:
    if not isinstance(email, str):
        raise ValueError('Email must be a string')
    if len(email) > 254:
        raise ValueError('Email too long')
    if not re.match(r'^[^\s@]+@[^\s@]+\.[^\s@]+$', email):
        raise ValueError('Invalid email format')
    return email
```

### 2) Never store secrets in code
Secrets (passwords, API keys, tokens) must come from environment variables only.

Bad:
```javascript
const apiKey = 'sk_live_abc123def456';  // NEVER!
```

Good:
```javascript
const apiKey = process.env.STRIPE_API_KEY;
if (!apiKey) {
  throw new Error('STRIPE_API_KEY environment variable is required');
}
```

Provide `.env.example` with placeholder values:
```
STRIPE_API_KEY=sk_test_your_key_here
DATABASE_PASSWORD=your_password_here
JWT_SECRET=your_secret_here
```

### 3) Use parameterized queries to prevent SQL injection
Never concatenate user input into SQL queries.

Bad:
```javascript
const query = `SELECT * FROM users WHERE email = '${email}'`;  // VULNERABLE!
db.query(query);
```

Good:
```javascript
const query = 'SELECT * FROM users WHERE email = $1';
db.query(query, [email]);  // Email is passed as a parameter, not interpolated
```

### 4) Prevent path traversal attacks
When handling file paths, validate that they don't escape the intended directory.

Bad:
```javascript
const filePath = `/uploads/${req.body.filename}`;  // VULNERABLE to ../../../etc/passwd
fs.readFile(filePath);
```

Good:
```javascript
import path from 'path';

const uploadDir = path.resolve('/uploads');
const filePath = path.resolve('/uploads', req.body.filename);

// Ensure the resolved path is within uploadDir
if (!filePath.startsWith(uploadDir)) {
  throw new Error('Invalid file path');
}

fs.readFile(filePath);
```

### 5) Enforce least privilege
Users and services should only have access to what they need.
- API tokens should be scoped to specific resources and actions
- Database users should have only the permissions required
- File permissions should be restrictive (0600, not 0644)
- Environment variables should be restricted to services that need them

Example (Database):
```sql
-- Bad: overly permissive
GRANT ALL ON *.* TO 'app'@'localhost';

-- Good: minimal required permissions
GRANT SELECT, INSERT, UPDATE ON mydb.users TO 'app'@'localhost';
GRANT SELECT ON mydb.products TO 'app'@'localhost';
```

### 6) Hash passwords, never store plain text
Always hash passwords using a strong, slow algorithm (bcrypt, Argon2).

Example:
```javascript
import bcrypt from 'bcrypt';

// When user registers
const plainPassword = req.body.password;
const hash = await bcrypt.hash(plainPassword, 12);  // 12 rounds, ~100ms
await db.insert('users', { email, password_hash: hash });

// When user logs in
const plainPassword = req.body.password;
const user = await db.query('SELECT password_hash FROM users WHERE email = $1', [email]);
const isValid = await bcrypt.compare(plainPassword, user.password_hash);
if (!isValid) {
  throw new Error('Invalid credentials');
}
```

### 7) Implement rate limiting
Protect against brute force and DoS attacks by limiting request rates.

Example (Express):
```javascript
import rateLimit from 'express-rate-limit';

// Limit login attempts
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,  // 15 minutes
  max: 5,  // 5 attempts per window
  message: 'Too many login attempts, try again later',
});

app.post('/login', loginLimiter, async (req, res) => {
  // Login logic
});
```

### 8) Use HTTPS in production
Enforce TLS/SSL for all communication in production.

Example (Express):
```javascript
// Redirect HTTP to HTTPS
app.use((req, res, next) => {
  if (process.env.NODE_ENV === 'production' && !req.secure) {
    return res.redirect(301, `https://${req.hostname}${req.url}`);
  }
  next();
});
```

### 9) Redact sensitive data in logs
Never log passwords, tokens, API keys, or PII (except internally hashed IDs).

Bad:
```javascript
logger.info('login attempt', { email, password });  // EXPOSES PASSWORD!
```

Good:
```javascript
logger.info('login attempt', { email, user_id: user.id });  // Safe
// Or use the obs.js redaction function:
const logger = createLogger({
  service: 'auth',
  env: 'prod',
  version: '1.0.0',
  denyKeys: ['password', 'token', 'api_key']
});
logger.info('login attempt', { email, password: 'secret' });  // password is redacted
```

### 10) Implement CSRF protection
For state-changing operations (POST, PUT, DELETE), require a CSRF token.

Example (Express):
```javascript
import csrf from 'csurf';

const csrfProtection = csrf({ cookie: false });

app.post('/users', csrfProtection, (req, res) => {
  // Token is validated automatically
  res.json({ created: true });
});
```

## Quality Checklist

- [ ] All external input is validated (type, format, length, content)
- [ ] No secrets in code or committed files
- [ ] All SQL queries are parameterized
- [ ] File paths are resolved and checked against intended directory
- [ ] Passwords are hashed with bcrypt or similar
- [ ] Least privilege is enforced for users and services
- [ ] Rate limiting is in place for sensitive endpoints
- [ ] Sensitive data is redacted in logs
- [ ] HTTPS is enforced in production
- [ ] CSRF protection is in place for state-changing operations
- [ ] Security tests exist (e.g., injection attack scenarios)

## Verification Commands

```bash
# Check for hardcoded secrets
grep -r "password\|secret\|api_key\|token" src/ | grep -v "^\s*//\|^\s*//" | head -20

# Run security audit for dependencies
npm audit --audit-level=high

# Run static security scanner (if installed)
npm run security:scan  # if available
```

## How to Recover if You Violate This Skill

If you commit code with security issues:
1. Immediately remove or rotate any exposed secrets
2. Fix the code to validate input or redact secrets
3. Add security tests to prevent regression
4. Notify the security team if sensitive data was exposed

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: Security-sensitive functions or boundaries modified
- **Key Decisions**: Explain why validation/redaction/encryption was chosen
- **Verification**: Confirm security audit passes; no hardcoded secrets
- **Risk Notes**: Call out any security assumptions or residual risks
