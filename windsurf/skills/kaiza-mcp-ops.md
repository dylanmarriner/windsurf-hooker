# Skill: @kaiza-mcp-ops

**Purpose:** Operate safely within Kaiza MCP constraints: plan work, request permissions, execute changes, record provenance, validate results, and audit all modifications.

**Invocation:** `/use-skill kaiza-mcp-ops` before any file modifications, repo changes, or deployments.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Mandatory for all changes when Kaiza MCP is active.
- **Dependencies:** @no-placeholders-production-code, all other skills.
- **Owner:** DevOps + governance.

---

## Core Operating Mode

### 1. Plan First (No Direct Action)

Before any work, produce a concrete plan:

```json
{
  "work_id": "PR-123",
  "title": "Refactor JWT validation with detailed error handling",
  "affected_modules": ["src/auth/jwt.ts", "src/auth/jwt.test.ts"],
  "changes": [
    {
      "file": "src/auth/jwt.ts",
      "operation": "modify",
      "description": "Add detailed error types, structured logging, and correlation ID support",
      "lines_changed": "+45 lines, -12 lines"
    },
    {
      "file": "src/auth/jwt.test.ts",
      "operation": "modify",
      "description": "Add 12 new unit tests covering error paths and edge cases",
      "lines_changed": "+120 lines"
    }
  ],
  "risk_assessment": {
    "breakage_risk": "low",
    "security_risk": "none",
    "performance_impact": "negligible",
    "migration_required": false
  },
  "testing_strategy": "All existing tests pass + 12 new tests",
  "rollback_plan": "Revert commits via git; no data migration required",
  "estimated_effort_minutes": 45
}
```

### 2. Request Permissions via Kaiza MCP Gate

```
REQUEST TO KAIZA MCP:

{
  "operation": "request_modifications",
  "work_id": "PR-123",
  "requestor": "agent",
  "reason": "Implement JWT validation refactor per GLOBAL_RULES.md @no-placeholders-production-code",
  "files_to_modify": [
    {
      "path": "src/auth/jwt.ts",
      "type": "modify",
      "justification": "Add error handling, logging, and correlation ID support"
    },
    {
      "path": "src/auth/jwt.test.ts",
      "type": "modify",
      "justification": "Add 12 regression and new-feature tests"
    }
  ],
  "pre_flight_checks": ["lint", "typecheck", "test", "security-scan", "placeholder-scan"],
  "audit_metadata": {
    "skill_used": ["@no-placeholders-production-code", "@audit-first-commentary", "@debuggable-by-default", "@test-engineering-suite"],
    "rules_compliance": "GLOBAL_RULES.md section: Standard Operating Procedure"
  }
}
```

Kaiza MCP response:

```json
{
  "status": "approved",
  "request_id": "kaiza-req-789",
  "timestamp": "2026-01-15T10:30:45.123Z",
  "approver": "governance_bot",
  "notes": "Request approved. Pre-flight checks will run automatically. Audit trail created.",
  "next_steps": "Execute changes via Kaiza file APIs. Report results when complete."
}
```

### 3. Execute Changes via Kaiza File APIs

```
NO DIRECT FILE EDITS. Use Kaiza MCP file operations:

REQUEST:
{
  "operation": "write_file",
  "request_id": "kaiza-req-789",
  "path": "src/auth/jwt.ts",
  "content": "...",
  "reason": "Refactor JWT validation with error handling and logging",
  "audit_metadata": {
    "work_id": "PR-123",
    "files_in_batch": ["src/auth/jwt.ts", "src/auth/jwt.test.ts"],
    "batch_sequence": 1,
    "batch_total": 2
  }
}

RESPONSE:
{
  "status": "success",
  "file_id": "f-123",
  "path": "src/auth/jwt.ts",
  "timestamp": "2026-01-15T10:30:46.123Z",
  "audit_log_id": "audit-log-456"
}
```

Repeat for all files in the batch.

### 4. Record Provenance

Kaiza automatically logs:
- **What:** File path, old content hash, new content hash, line changes.
- **Who:** Agent identity, request timestamp.
- **Why:** Reason/justification (from request).
- **When:** Exact timestamp (UTC).
- **How:** Verification (pre-flight checks run).

This is **immutable**; cannot be retroactively modified or deleted.

### 5. Run Pre-Flight Checks via Kaiza CI Integration

```
REQUEST:
{
  "operation": "run_quality_gates",
  "request_id": "kaiza-req-789",
  "work_id": "PR-123",
  "gates": [
    "lint",
    "typecheck",
    "test",
    "security-scan",
    "placeholder-scan"
  ],
  "environment": "ci"
}

RESPONSE:
{
  "status": "all_passed",
  "gates_results": {
    "lint": {
      "status": "passed",
      "details": "0 errors, 0 warnings",
      "duration_seconds": 3
    },
    "typecheck": {
      "status": "passed",
      "details": "0 errors (tsc)",
      "duration_seconds": 8
    },
    "test": {
      "status": "passed",
      "details": "36/36 tests passed. Coverage: 89%",
      "duration_seconds": 15
    },
    "security_scan": {
      "status": "passed",
      "details": "0 vulnerabilities (npm audit)",
      "duration_seconds": 5
    },
    "placeholder_scan": {
      "status": "passed",
      "details": "0 prohibited patterns found",
      "duration_seconds": 2
    }
  },
  "total_duration_seconds": 33,
  "audit_log_id": "audit-log-457"
}
```

**If any gate fails:**
- Kaiza blocks the commit
- Agent must fix failures
- Rerun gates until all pass

### 6. Verify Results Comprehensively

Agent confirms:
- All pre-flight checks passed
- Code is complete, functional, not scaffolding
- Tests added/updated for all changes
- Observability (logging, error handling) present
- No regression from refactoring

```json
{
  "operation": "submit_verification_results",
  "request_id": "kaiza-req-789",
  "work_id": "PR-123",
  "status": "verified_complete",
  "verification_details": {
    "code_quality": {
      "status": "complete",
      "no_placeholders": true,
      "all_functions_documented": true,
      "error_paths_handled": true
    },
    "testing": {
      "status": "comprehensive",
      "unit_tests_added": 12,
      "integration_tests_added": 2,
      "coverage_total": 89,
      "coverage_meets_threshold": true
    },
    "observability": {
      "status": "implemented",
      "structured_logging": true,
      "correlation_ids": true,
      "error_capture": true,
      "debug_hooks": true
    },
    "security": {
      "status": "verified",
      "no_secrets_in_code": true,
      "input_validation_present": true,
      "no_vulnerabilities": true
    },
    "pre_flight_checks": "all_passed"
  },
  "notes": "All GLOBAL_RULES.md requirements satisfied. Code ready for merge."
}
```

### 7. Produce Audit Summary

```json
{
  "operation": "submit_audit_summary",
  "request_id": "kaiza-req-789",
  "work_id": "PR-123",
  "timestamp": "2026-01-15T10:35:20.123Z",
  "summary": {
    "title": "Refactor JWT validation with detailed error handling",
    "description": "Refactored JWT validation to include comprehensive error types, structured logging, correlation ID support, and detailed test coverage.",
    "files_modified": [
      {
        "path": "src/auth/jwt.ts",
        "changes": "Added error types (JWTValidationError), structured logging with correlation IDs, improved error messages, and comprehensive error handling",
        "lines_changed": "+45, -12"
      },
      {
        "path": "src/auth/jwt.test.ts",
        "changes": "Added 12 unit tests covering error paths (expired tokens, invalid signatures, malformed tokens), configuration validation, and edge cases",
        "lines_changed": "+120, -0"
      }
    ],
    "testing": {
      "unit_tests_count": 36,
      "integration_tests_count": 4,
      "coverage_percent": 89,
      "all_tests_pass": true,
      "regression_tests_pass": true
    },
    "quality_gates": {
      "lint": "passed",
      "typecheck": "passed",
      "tests": "passed",
      "security_scan": "passed",
      "placeholder_scan": "passed"
    },
    "skills_applied": [
      "@no-placeholders-production-code",
      "@audit-first-commentary",
      "@debuggable-by-default",
      "@test-engineering-suite",
      "@secure-by-default"
    ],
    "rules_compliance": "GLOBAL_RULES.md",
    "breaking_changes": false,
    "migration_required": false,
    "deployment_impact": "none"
  }
}
```

---

## Common Operations via Kaiza MCP

### Feature Implementation

```
1. PLAN: Document feature requirements, affected modules, testing strategy
2. REQUEST: Ask Kaiza for permission to modify files
3. IMPLEMENT: Write complete, tested code via Kaiza file APIs
4. PRE-FLIGHT: Run lint, typecheck, tests, security scan via Kaiza CI
5. VERIFY: Confirm all checks pass, code is complete
6. AUDIT: Submit audit summary with changes, testing, compliance info
7. COMMIT: Kaiza commits with audit summary in message body
```

### Bugfix with Regression Test

```
1. PLAN: Identify root cause, affected modules, regression test needed
2. REQUEST: Ask Kaiza for permission to modify code and tests
3. WRITE_TEST: Add test that reproduces the bug (will fail with old code)
4. IMPLEMENT_FIX: Fix the bug (test now passes)
5. PRE-FLIGHT: All tests pass (including new regression test)
6. VERIFY: Confirm fix correct, no side effects
7. AUDIT: Submit summary with root cause, fix, test, verification
8. COMMIT: Kaiza commits with bug ID and regression test reference
```

### Dependency Upgrade

```
1. PLAN: Identify dependency to upgrade, breaking changes to handle, testing needed
2. REQUEST: Ask Kaiza for permission to update package.json and code
3. UPDATE_DEPS: Modify package.json, run npm install via Kaiza
4. FIX_BREAKAGE: Update code for any breaking changes
5. PRE-FLIGHT: Run tests, security scan (checks for vulnerabilities in new version)
6. VERIFY: Confirm tests pass, no regressions
7. AUDIT: Submit summary with dependency version, breaking changes handled, testing
8. COMMIT: Kaiza commits with dependency upgrade info
```

### Security Hardening

```
1. PLAN: Identify security vulnerability, mitigation strategy, testing approach
2. REQUEST: Ask Kaiza for permission (security-critical changes)
3. IMPLEMENT: Add input validation, SSRF checks, rate limiting, etc.
4. TEST: Add security-specific tests (injection attempts, boundary cases, etc.)
5. PRE-FLIGHT: All tests pass + security scan clean
6. VERIFY: Confirm vulnerability addressed, no regression
7. AUDIT: Submit summary with vulnerability, mitigation, testing
8. COMMIT: Kaiza commits (may be marked as security fix for release notes)
```

---

## Error Handling via Kaiza MCP

### If Pre-Flight Checks Fail

```json
{
  "gate": "test",
  "status": "failed",
  "details": {
    "failures": 2,
    "output": "FAIL src/__tests__/auth.test.ts\n  validateJWT\n    expired tokens\n      ✗ throws TOKEN_EXPIRED code (15ms)"
  }
}
```

**Agent must:**
1. Review failed tests
2. Debug and fix the issue
3. Rerun pre-flight checks via Kaiza
4. Repeat until all pass

### If Code Review Finds Issues

```json
{
  "operation": "code_review_failure",
  "work_id": "PR-123",
  "reviewer": "human_engineer",
  "issues": [
    {
      "severity": "critical",
      "file": "src/auth/jwt.ts",
      "line": 42,
      "message": "Missing error handling for expired token case"
    }
  ]
}
```

**Agent must:**
1. Address each issue
2. Request permission again if files are modified
3. Rerun pre-flight checks
4. Submit updated audit summary

---

## Safe Defaults for Kaiza MCP Operations

### File Modification Constraints

- **No direct filesystem access:** All file I/O via Kaiza APIs
- **Immutable audit log:** Every operation logged; cannot be deleted
- **Automatic backups:** Kaiza keeps previous versions (git-backed)
- **Permission gates:** Agent can only modify what was approved

### Pre-Flight Gate Enforcement

- **Mandatory:** Lint, typecheck, tests, security scan, placeholder scan
- **No exceptions:** All gates must pass before commit
- **Automatic:** Kaiza runs gates; agent doesn't need to invoke them

### Audit Trail Requirements

- **Immutable:** Logged at Kaiza server; cannot be changed retroactively
- **Complete:** Includes what changed, why, who, when, verification results
- **Discoverable:** Can be queried by work_id, timestamp, file_path, etc.

---

## Quality Checklist

- [ ] Concrete plan created and reviewed before work starts.
- [ ] Permission requested via Kaiza MCP gate (not assumed).
- [ ] All file modifications via Kaiza file APIs (no direct edits).
- [ ] Pre-flight checks requested and passed (lint, typecheck, tests, security, placeholder scan).
- [ ] Verification results comprehensive (code quality, testing, observability, security).
- [ ] Audit summary submitted with changes, testing, compliance info.
- [ ] Audit summary includes skills applied and rules compliance.
- [ ] All files changed are documented in audit summary.
- [ ] Rollback plan documented (how to revert if issues).
- [ ] Breaking changes identified and communicated.

---

## Deliverable Summary

```json
{
  "skill": "kaiza-mcp-ops",
  "completed": true,
  "kaiza_operations_completed": 5,
  "audit_log_entries": 8,
  "requests_made": [
    {
      "request_id": "kaiza-req-789",
      "work_id": "PR-123",
      "status": "approved_and_completed",
      "timestamp": "2026-01-15T10:30:45.123Z",
      "files_modified": 2
    }
  ],
  "pre_flight_checks": {
    "lint": "passed",
    "typecheck": "passed",
    "tests": "passed",
    "security_scan": "passed",
    "placeholder_scan": "passed"
  },
  "audit_trail": {
    "immutable": true,
    "entries_logged": 8,
    "human_readable_summary": "submitted"
  }
}
```

---

## Related Skills

- @no-placeholders-production-code (ensures complete code)
- @test-engineering-suite (pre-flight tests)
- @secure-by-default (security scanning)
- All other skills (Kaiza gates them)
