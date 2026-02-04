---
name: kaiza-mcp-ops
description: Operate Windsurf Cascade in Kaiza-first mode with plan selection, provenance tracking, and audit trails. Invoke as @kaiza-mcp-ops.
---

# Skill: Kaiza MCP Operations

## Purpose
Ensure all code modifications are made within approved plans, tracked via Kaiza MCP, and auditable via KAIZA-AUDIT blocks.

## When to Use This Skill
- Starting any coding task (feature, bug fix, refactoring, release)
- When Kaiza MCP is available in the environment
- Before reading or writing files

## Steps

### 1) Kaiza preflight
- Call Kaiza `read_prompt` to load `WINDSURF_CANONICAL` (authoritative config)
- Call Kaiza `list_plans` to see approved plans for this workspace
- Select a plan that matches the scope of your task

If no matching plan exists:
- Stop and propose a plan
- Do not proceed until the plan is approved

### 2) Understand plan boundaries
Each plan has:
- **scope**: What files/modules it covers
- **authority**: Which rules govern it
- **risk level**: How much change is permitted
- **verification**: What checks must pass

Example plan:
```
Plan: "implement-feature-x"
Scope: src/features/x, tests/features/x, docs/features/x
Authority: AGENTS.md, GLOBAL_RULES.md, @no-placeholders-production-code
Risk: moderate (new code, within isolated feature)
Verification: all tests pass, lint clean, coverage >80%
```

### 3) Read files using Kaiza
Use Kaiza `read_file` for all reads (not standard file operations).
This ensures:
- Reads are tracked for audit
- Permissions are checked against the plan
- Context is loaded into the MCP session

### 4) Write files with provenance metadata
For every file write using Kaiza `write_file`, include:
- **plan**: Name of the approved plan (e.g., "implement-feature-x")
- **role**: executable | boundary | library | infra | test | docs
- **purpose**: What does this file exist to do?
- **usedBy**: What imports/invokes it?
- **connectedVia**: How it integrates (routes, DI, CLI, job scheduler)
- **executedVia**: How it runs (node, python, docker, CI)
- **failureModes**: Known failure patterns
- **authority**: Which rules govern this file

Example write metadata:
```
plan: "implement-feature-x"
role: "boundary"
purpose: "HTTP handler for feature X endpoints"
usedBy: "app.js (main router), tests/features/x.test.js"
connectedVia: "Express route registration in /features route group"
executedVia: "Node.js, runs on every HTTP request"
failureModes: "Invalid input → 400, Database down → 500, Timeout → 504"
authority: "AGENTS.md (route patterns), @secure-by-default (input validation)"
```

### 5) Run verification gates after every change
After each write:
```bash
npm test
npm run lint
npm run typecheck
python scripts/ci/forbidden_markers_scan.py --root .
```

If any gate fails, stop and fix before continuing.

### 6) Produce KAIZA-AUDIT block
After all changes are complete, produce a machine-checkable audit block:

```
KAIZA-AUDIT
Plan: implement-feature-x
Scope: src/features/x/handler.js, src/features/x/model.js, tests/features/x.test.js
Intent: Add HTTP API for feature X with structured logging and input validation
Key Decisions:
  - Used Express middleware for input validation (familiar, proven)
  - Stored feature X in new module to avoid tight coupling
  - Added correlation ID propagation for observability
Verification:
  - npm test: PASS (all tests pass, +3 new test cases)
  - npm run lint: PASS
  - npm run typecheck: PASS
  - forbidden_markers_scan.py: PASS
  - Coverage: 92% for feature X module (target: >80%)
Results: All gates pass. Code is ready for review.
Risk Notes: Feature X depends on external service Y; timeouts configured to 5s
Rollback: Revert commits or feature-flag can disable feature X via ENV var
KAIZA-AUDIT-END
```

### 7) Embed KAIZA-AUDIT in PR description
If using GitHub/GitLab:
- Paste the KAIZA-AUDIT block into the PR description
- CI will validate it has all required fields
- Reviewers use it to understand the scope and safety checks

## Quality Checklist

- [ ] Approved plan selected (or proposed)
- [ ] All reads use Kaiza `read_file`
- [ ] All writes use Kaiza `write_file` with provenance metadata
- [ ] All verification gates pass after each change
- [ ] KAIZA-AUDIT block is produced with all required fields
- [ ] Plan scope is respected (no out-of-scope changes)
- [ ] Risk level is appropriate for the change
- [ ] Authority rules are referenced in KAIZA-AUDIT

## Verification Commands

```bash
# Check that Kaiza tools are available
which kaiza || echo "Kaiza not available"

# Check that plans can be listed
kaiza list_plans

# Verify KAIZA-AUDIT format (locally)
grep -A 8 "^KAIZA-AUDIT$" PR_DESCRIPTION.md | grep -E "Plan:|Scope:|Intent:|Key Decisions:|Verification:|Results:|Risk Notes:|Rollback:"
```

## How to Recover if Plan Boundary is Breached

If you realize you've made changes outside the plan scope:
1. Revert the out-of-scope changes
2. Propose a new or amended plan
3. Wait for approval
4. Resume the task with the updated plan

If a verification gate fails:
1. Stop and fix the issue
2. Re-run the gate
3. Continue only after gate passes

## KAIZA-AUDIT Compliance

Every task using this skill must produce a KAIZA-AUDIT block with:
- **Plan**: Approved plan name
- **Scope**: Files/modules touched
- **Intent**: What outcome is delivered
- **Key Decisions**: Why these choices
- **Verification**: Exact commands executed and results
- **Results**: Pass/fail with artifacts
- **Risk Notes**: Remaining risks + mitigations
- **Rollback**: How to revert safely
