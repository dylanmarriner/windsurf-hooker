# /fix-bug
Fix a defect using evidence-first diagnosis and regression protection.

## Prerequisites
- Approved plan exists for the bug fix scope.

## Inputs
- Symptom description
- Logs/traces/metrics snippets if available
- Reproduction steps (if available)

## Steps
1) Kaiza preflight
   - `read_prompt` → `list_plans` → select approved fix plan.

2) Evidence capture
   - Identify the failing boundary and capture:
     - structured logs around the failure window,
     - trace spans (if present),
     - relevant metrics.
   - Create a minimal reproduction harness if feasible (deterministic).

3) Hypothesis + narrowing
   - Maintain a short hypothesis list in the plan notes.
   - Confirm/deny with targeted instrumentation and tests.

4) Implement fix
   - Fix the code.
   - Add a regression test that fails without the fix.
   - Add observability improvements if the bug was hidden.

5) Verify
   - Run full suite.
   - Confirm regression test passes with fix.
   - Run scanners and audits.

6) Deliver
   - Provide KAIZA-AUDIT block with RCA summary.

## Success Criteria
- Regression test exists and passes.
- Root cause documented.
- Fix is minimal and scoped.
- All gates pass.
