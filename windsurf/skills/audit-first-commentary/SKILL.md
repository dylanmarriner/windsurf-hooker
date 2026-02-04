---
name: audit-first-commentary
description: Write code with clear, high-signal documentation that explains invariants, failure modes, and design tradeoffs. Invoke as @audit-first-commentary.
---

# Skill: Audit-First Commentary

## Purpose
Make every non-trivial function, module, and config file understandable to future readers (and auditors). Document why decisions were made, what invariants must hold, and what failure modes exist.

## When to Use This Skill
- Writing new modules, functions, or classes
- Refactoring complex logic
- Adding new configuration
- Creating or updating CI scripts
- Writing API handlers or job runners

## Steps

### 1) File-level documentation
At the top of every non-trivial file, include:
- **Purpose**: What does this file exist to do?
- **Invariants**: What must always be true?
- **Failure Modes**: What can go wrong and how will it surface?
- **Debug Notes**: How to troubleshoot if something breaks?

Example (JavaScript):
```javascript
/**
 * Purpose
 * - Handle JWT validation for incoming requests.
 *
 * Invariants
 * - Every request must have an Authorization header (or error).
 * - Tokens must be valid and not expired.
 * - Token claims must include 'sub' (subject) and 'scope'.
 *
 * Failure Modes
 * - Missing or malformed Authorization header → 401 Unauthorized
 * - Expired token → 401 Unauthorized
 * - Invalid signature → 401 Unauthorized
 * - Missing required claims → 401 Unauthorized
 *
 * Debug Notes
 * - Check JWT_SECRET is set and matches the issuer's key.
 * - Tokens are logged (redacted) in structured logs with request_id.
 * - Check expiry_timestamp in logs to diagnose expiration issues.
 */
```

Example (Python):
```python
"""
Purpose
- Parse and validate incoming form submissions.

Invariants
- All required fields must be present in the request.
- Email addresses must be valid (basic regex check).
- Passwords must be at least 12 characters.
- No request should be processed twice (idempotency key check).

Failure Modes
- Missing required field → 400 Bad Request with field name
- Invalid email → 400 Bad Request with error message
- Weak password → 400 Bad Request with requirements
- Duplicate request (repeated idempotency key) → 409 Conflict

Debug Notes
- All failures log the form data (redacted) for audit.
- Check logs for invalid_field or weak_password errors.
"""
```

### 2) Function-level documentation
For every function with:
- **Multiple branches** (if/else, loops)
- **Complex logic** (>10 lines)
- **External dependencies** (DB, HTTP, files)
- **Boundary crossings** (HTTP handler, CLI entrypoint, job runner)

Include:
- **Summary**: One-line description of what it does.
- **Preconditions**: What must be true for the function to work?
- **Postconditions**: What will be true after the function succeeds?
- **Error cases**: How does it fail and what does it return/throw?

Example:
```javascript
/**
 * validateAndHashPassword(plaintext, saltRounds = 12)
 * 
 * Summary: Hash a plaintext password using bcrypt.
 * 
 * Preconditions:
 * - plaintext must be a non-empty string (>= 8 chars, < 128 chars)
 * - saltRounds must be an integer >= 10
 * 
 * Postconditions:
 * - Returns a bcrypt hash string (60 chars, always distinct)
 * - Hash is deterministic only with same salt rounds
 * 
 * Error cases:
 * - plaintext length invalid → throws Error("password must be 8-128 chars")
 * - bcrypt fails (rare) → rejects with bcrypt error
 * 
 * Idempotency: Not idempotent (different hash each call)
 * Side effects: None (pure function, but slow ~100ms)
 */
export async function validateAndHashPassword(plaintext, saltRounds = 12) {
  if (!plaintext || plaintext.length < 8 || plaintext.length > 128) {
    throw new Error('Password must be 8-128 characters');
  }
  return bcrypt.hash(plaintext, saltRounds);
}
```

### 3) Inline comments for tricky logic
For logic that is not immediately obvious:
- Explain the **why**, not the **what**.
- Reference design docs or RFCs if applicable.
- Explain non-obvious algorithm choices.

Bad example:
```javascript
if (x > 10) {
  x = x * 2;  // multiply by 2
}
```

Good example:
```javascript
// If we have more than 10 items, double the batch size to reduce round-trips.
// See capacity planning doc for why 10 is the threshold.
if (x > 10) {
  x = x * 2;
}
```

### 4) Tradeoff documentation
If you made a deliberate choice to accept a tradeoff, document it:
- What was the alternative?
- Why did you choose this approach?
- What are the risks or limitations?

Example:
```javascript
/**
 * Why we use a simple in-memory cache instead of Redis:
 * - Tradeoff: Memory-bound (doesn't scale to 100M items)
 * - Benefit: Zero operational overhead, no network latency
 * - Risk: Cache is lost on restart (mitigation: cache is warm on demand)
 * - Review trigger: If cache miss rate exceeds 20%, reconsider Redis
 */
```

### 5) Verify documentation with linters
- Enable ESLint rule `require-jsdoc` (or equivalent)
- Enable TypeScript strict mode and require parameter/return types
- Run a documentation coverage tool if available

## Quality Checklist

- [ ] File-level doc comment exists for non-trivial files
- [ ] Purpose, Invariants, Failure Modes documented
- [ ] Every public function has a summary and preconditions
- [ ] Complex logic has inline comments explaining the why
- [ ] Tradeoffs are documented with design decisions
- [ ] No cryptic variable names; use descriptive names
- [ ] Error cases are documented with example messages
- [ ] Documentation is up-to-date with code

## Verification Commands

```bash
# Linting for documentation
npm run lint              # May enforce JSDoc or TSDoc

# Check for missing comments
grep -r "function\|class\|export" src/ | grep -v "^\s*//" | head -20

# Type checking (includes doc string validation in TS)
npm run typecheck
```

## How to Recover if You Violate This Skill

If you commit code with poor documentation:
1. Go back and add the missing comments.
2. Update file-level docs if invariants or failure modes changed.
3. Re-run linters to confirm.

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Key Decisions**: Document non-obvious choices and tradeoffs
- **Verification**: Confirm all linters pass
- **Risk Notes**: Call out any assumptions or limitations in documentation
