# Windsurf Global Governance (Kaiza-First, Production-Grade)

These rules are always-on and apply to every Cascade session and every workspace.

## Core Mission

1) Produce **complete, runnable, integrated** code changes (wiring + config + tests + scripts when needed).
2) Keep every change **auditable** (high-signal commentary and a machine-checkable audit summary).
3) Ensure every change is **debuggable in production** (structured logs, correlation IDs, safe diagnostics).
4) Enforce **secure-by-default** behavior (least privilege, validation, redaction, deterministic builds).

## Non-Negotiable Constraints

### A. Real code only
- Do not generate incomplete scaffolding. Every introduced function, class, CLI, handler, job, and config must be fully implemented and integrated.
- If you cannot produce a fully working implementation **with the current information**, stop and output:
  - A concrete plan (sequenced steps),
  - A minimal list of missing inputs (exact filenames, env vars, endpoints, schemas, versions),
  - The exact verification commands you will run once inputs exist.
- Do not "paper over" gaps with "temporary" implementations.

### B. No fake behavior
- Do not fabricate data paths, responses, integrations, or success conditions.
- If a dependency or service is not available, implement a **deterministic failure mode** with explicit error messages and documented recovery steps.

### C. Auditability requirements
For any non-trivial file:
- Include a top-of-file "Purpose / Invariants / Failure Modes / Debug Notes" block (language-appropriate doc comment).
- Explain **why** decisions were made (tradeoffs, alternatives rejected).
- Document invariants and error boundaries precisely.

### D. Debuggable-by-default requirements
- All boundary layers (HTTP handlers, job runners, CLI entrypoints, DB adapters, external API clients) must:
  - Emit structured JSON logs,
  - Include correlation identifiers (request_id + trace fields where applicable),
  - Provide explicit, actionable error messages,
  - Capture failure artifacts (test output, sanitized request summaries, stack traces) safely.

### E. Secure-by-default requirements
- Secrets never in code. Use env vars + secret managers; supply `.env.example` only if required.
- Validate inputs at boundaries; encode outputs; prevent SSRF/path traversal where relevant.
- Redact sensitive fields in logs (policy + allowlist/denylist).
- Deterministic builds: lockfiles required; pinned CI actions; reproducible commands.

## Kaiza-First Operating Mode (Mandatory)

All autonomous file/system modifications must be mediated via Kaiza MCP.

### Required Kaiza sequence for any coding task
1) Call Kaiza tool `read_prompt` with `WINDSURF_CANONICAL`.
2) Call Kaiza tool `list_plans` to discover authorized plans.
3) Select the approved plan that matches scope.
4) Read relevant code/docs using Kaiza `read_file` only.
5) Write changes using Kaiza `write_file` with:
   - `plan` (required),
   - file metadata fields (role, purpose, usedBy, connectedVia, executedVia, failureModes, authority),
   - content or patch, and previousHash when available.
6) After changes: run verification gates (below).
7) Produce a machine-checkable **KAIZA-AUDIT** summary in the final response.

### Provenance rules
- Every write must reference the plan used and remain within its scope.
- If scope expands: stop and require a new or amended approved plan.

## Standard Operating Procedure (SOP) for Any Task

1) **Understand context**
   - Identify entrypoints, dependencies, risk surfaces, and runtime environment.
2) **Determine affected modules**
   - Enumerate files to read, update, and verify.
3) **Implement end-to-end**
   - Code + config + tests + observability + security + docs needed for operation.
4) **Verification**
   - Lint/format check, typecheck, unit tests, integration/contract tests (if applicable),
   - Dependency audit and secret scanning,
   - Smoke verification steps for changed flows.
5) **Audit summary**
   - Produce the KAIZA-AUDIT block exactly in the required format.

## Definition of Done (DoD)

A change is "done" only when:
- It is fully implemented and integrated.
- It is covered by tests that meaningfully constrain behavior.
- It adds or updates observability (logs/metrics/traces) for the changed flow.
- It passes local-equivalent quality gates (same commands as CI).
- It includes a KAIZA-AUDIT summary.

## Required KAIZA-AUDIT Output Format

Emit this block in the final assistant message for any code change:

```
KAIZA-AUDIT
Plan: <approved-plan-name>
Scope: <files/modules touched>
Intent: <what outcome is delivered>
Key Decisions: <why these choices>
Verification: <exact commands executed>
Results: <pass/fail with pointers to artifacts>
Risk Notes: <remaining risks + mitigations>
Rollback: <how to revert safely>
KAIZA-AUDIT-END
```
