# Skill: @no-placeholders-production-code

**Purpose:** Enforce that all code output is production-ready with zero placeholders, stubs, mocks, or scaffolding.

**Invocation:** `/use-skill no-placeholders-production-code` or automatic gate in all coding tasks.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Before any code is committed or submitted.
- **Dependencies:** Global rules (GLOBAL_RULES.md), Kaiza MCP.
- **Owner:** Governance layer.

---

## Step-Based Instructions

### Step 1: Scan for Prohibited Patterns
Before finalizing any code, scan all modified files for prohibited patterns:

```bash
PROHIBITED=(
  "\\bTODO\\b"
  "\\bFIXME\\b"
  "\\bstub\\b"
  "\\bmock\\b"
  "\\bplaceholder\\b"
  "\\bnot.{0,10}implement"
  "\\breturn\\s+null"
  "\\breturn\\s+None"
  "\\bpass\\b\\s*$"
  "\\braise\\s+NotImplementedError"
  "fake.*response"
  "dummy.*data"
  "temporary.*hack"
  "quickfix"
)

for pattern in "${PROHIBITED[@]}"; do
  if grep -r -E "$pattern" --include="*.ts" --include="*.tsx" --include="*.rs" --include="*.py" --include="*.js" --include="*.jsx" --include="*.go" --include="*.java" src/ crates/ apps/ agents/ 2>/dev/null | grep -v '\[EXAMPLE' | grep -v '\[LEGACY'; then
    echo "ERROR: Prohibited pattern found: $pattern"
    exit 1
  fi
done
```

### Step 2: Validate Code Completeness

For each modified file, verify:

1. **All imports/dependencies wired:** No unresolved symbols.
2. **All functions have implementations:** No `pass`, `return null`, `unimplemented!()`, etc.
3. **Error paths handled:** Every error case has explicit handling (not silently ignored).
4. **Configuration wired:** All config files included, environment variables documented.
5. **Tests included:** Unit tests for new logic, integration tests for module interactions.

### Step 3: Enforce Detailed Commentary

For every non-trivial function (>5 lines or >1 branch):

1. **Module-level docstring:** Describe module purpose, key types, invariants.
2. **Function docstring:** Describe inputs, outputs, side effects, exceptions, preconditions/postconditions.
3. **Inline comments:** For complex logic, explain the "why" (not just "what").
4. **Error messages:** Explicit, actionable text (not generic "error").

### Step 4: Verify Test Coverage

1. **Unit tests:** Core logic, edge cases, error paths (target ≥80%).
2. **Test names describe behavior:** e.g., `test_rejects_expired_tokens`, not `test_jwt`.
3. **Error tests:** Each error path tested explicitly.
4. **Snapshot tests:** For complex output; version-control carefully.

### Step 5: Observability Compliance Check

Verify structured logging and debug hooks:

1. **Logging:** All significant operations (auth, DB queries, API calls) log structured JSON.
2. **Correlation IDs:** Request/span IDs propagated through call chain.
3. **Error capture:** Errors include stack trace, context, and user-facing message.
4. **Debug flags:** Feature flags or log-level overrides available (safe in production).

### Step 6: Kaiza MCP Audit Trail

Before committing:

1. **Prepare audit summary:**
   ```json
   {
     "change_id": "PR-123",
     "files_modified": ["src/auth/jwt.ts", "src/auth/jwt.test.ts"],
     "changes_summary": "Refactored JWT validation with detailed error handling and structured logging",
     "test_coverage": "new: 100%, modified: 85%",
     "quality_gates_passed": ["lint", "typecheck", "tests", "security-scan", "placeholder-scan"],
     "observability_compliance": true,
     "kaiza_mcp_used": true,
     "notes": "All error paths now explicitly tested and logged."
   }
   ```

2. **Record via Kaiza MCP:** Pass audit summary to Kaiza file API; Kaiza logs immutably.

3. **Verify CI:** Kaiza triggers CI checks; confirm all pass before declaring done.

---

## Quality Checklist

- [ ] No prohibited patterns found in code.
- [ ] All functions have complete implementations (no stubs, `pass`, `return null`).
- [ ] All imports wired, no unresolved symbols.
- [ ] All config loaded from environment/vault, not hard-coded.
- [ ] Error paths handled explicitly (try/catch, Result, Optional, etc.).
- [ ] Module and function docstrings present, describe contract and invariants.
- [ ] Inline comments explain "why" for complex logic.
- [ ] Unit tests ≥80% coverage, test names describe behavior.
- [ ] Error paths tested explicitly (each error type tested).
- [ ] Structured logging with correlation IDs present.
- [ ] Secrets not logged; PII redacted.
- [ ] Debug hooks / feature flags present where appropriate.
- [ ] Kaiza MCP audit summary prepared.
- [ ] Local quality gates pass (lint, typecheck, tests, security, placeholder scan).

---

## Debugging Instrumentation

### Rich Error Messages
Every error includes:
- **User-facing message:** Non-technical, actionable.
- **Error code:** Machine-readable identifier (e.g., "TOKEN_EXPIRED").
- **Context:** What was being attempted (user ID, resource ID, etc.).
- **Stack trace:** Included in logs (not displayed to user).

### Diagnostic Hooks
Feature flags for deep debugging (safe in production):
```typescript
if (process.env.DEBUG_JWT === "true" || globalDebugFlags.includes("jwt")) {
  logger.debug("jwt token parts", {
    header: token.split(".")[0],
    payloadDecoded: Buffer.from(token.split(".")[1], "base64").toString("utf-8"),
  });
}
```

### Minimal Repro Helpers
For each bug fix, include a test that reproduces the original issue.

---

## Observability Pack Compliance Section

### Required Logging Fields
Every log entry must include:
```json
{
  "timestamp": "2026-01-15T10:30:45.123Z",
  "level": "info",
  "message": "jwt token valid",
  "service": "auth-service",
  "env": "production",
  "version": "1.0.0",
  "requestId": "req-abc123",
  "userId": "user-456",
  "operation": "validateJWT",
  "duration_ms": 5,
  "tokenLength": 256
}
```

### Correlation ID Propagation
- **Generated:** On request entry; stored in context (AsyncLocalStorage, thread-local, etc.).
- **Passed:** Through function arguments, HTTP headers (X-Request-ID), message queues.
- **Logged:** Every log entry includes `requestId` field.

---

## Kaiza MCP Usage Section

### File Modifications
```json
{
  "operation": "write_file",
  "path": "src/auth/jwt.ts",
  "content": "...",
  "reason": "Add detailed error handling and structured logging to JWT validation",
  "audit_metadata": {
    "change_id": "PR-123",
    "files_modified": ["src/auth/jwt.ts", "src/auth/jwt.test.ts"]
  }
}
```

### Pre-Flight Checks via Kaiza
```json
{
  "operation": "run_quality_gates",
  "gates": ["lint", "typecheck", "test", "security-scan", "placeholder-scan"],
  "reason": "Validate JWT refactor before commit",
  "audit_metadata": { "change_id": "PR-123" }
}
```

---

## Verification Commands

### Local Verification
```bash
npm run check:placeholders
npm run lint
npm run typecheck
npm test -- --coverage --threshold 80
npm audit --audit-level moderate
npx snyk test
```

### CI Verification
```bash
gh pr checks <PR_NUMBER>
```

---

## Deliverable Summary Format

```json
{
  "skill": "no-placeholders-production-code",
  "completed": true,
  "files_modified": ["src/auth/jwt.ts", "src/auth/jwt.test.ts"],
  "checks_passed": [
    {"name": "placeholder_scan", "status": "passed", "details": "0 prohibited patterns found"},
    {"name": "lint", "status": "passed", "details": "0 errors, 0 warnings"},
    {"name": "typecheck", "status": "passed", "details": "0 errors"},
    {"name": "test", "status": "passed", "details": "24/24 tests passed, coverage 100%"},
    {"name": "security_scan", "status": "passed", "details": "0 vulnerabilities"}
  ],
  "audit_trail": {
    "change_id": "PR-123",
    "kaiza_audit_log_id": "audit-789",
    "timestamp": "2026-01-15T10:30:45.123Z"
  }
}
```

---

## Related Skills & Workflows

- @audit-first-commentary (detailed documentation)
- @test-engineering-suite (testing best practices)
- @secure-by-default (security hardening)
- /pre-pr-review (comprehensive review checklist)
- /implement-feature (feature development workflow)
