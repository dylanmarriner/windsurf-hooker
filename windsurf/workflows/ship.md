sudo tee /etc/windsurf/workflows/ship.md >/dev/null <<'MD'
# /ship — AUDIT → REPAIR → VERIFY → SHIP (System)

Hard rules:
- No code edits until Gates 0–3 are satisfied.
- Defects in scope are blocking.
- No containment. No deferral. No relocation.
- If safe repair cannot be proven: REFUSE.

## Gate 0 — DEFECT AUDIT (MANDATORY)
Before anything else:
- Scan the affected scope for:
  - TODO / FIXME / XXX
  - mock/fake/demo/hardcoded test data
  - placeholder/stub logic (pass/..., unimplemented, empty handlers)
  - commented-out executable logic
  - "assume", "for now", "temporary", "hack"

Output EXACTLY:

DEFECT AUDIT
- File: path:line
  Type: <TODO|FIXME|Mock data|Placeholder|Commented-out logic|Assumption|Hack>
  Description: <what is missing / unsafe>

If the list is non-empty:
- Enter REPAIR MODE (below).
If empty:
- Proceed to Gate 1.

After completing Gate 0, include the audit token line:
[AUDIT_OK]

## REPAIR MODE (only if defects exist)
Rules:
- No new features.
- No unrelated refactors.
- No stylistic changes.
- Only eliminate the listed defects.

For each defect item, output one:
✅ FIXED — describe the real implementation
🗑 REMOVED — justify deletion
⛔ BLOCKED — explain why it cannot be fixed safely; STOP (no further output)

After repairs, rerun Gate 0 (audit again) until DEFECT AUDIT is empty.

When DEFECT AUDIT becomes empty, include:
[REPAIR_OK]

## Gate 1 — Requirement Lock
Restate:
- Inputs
- Outputs
- Constraints (security/compat/correctness)
- Performance expectations
- Failure modes (typed/structured)
- External dependencies (explicit list)

If anything is missing/ambiguous: stop and ask OR refuse.

## Gate 2 — Dependency Reality Check
For every external API/dependency:
- Source (repo path or pinned package)
- Version evidence (lockfile/manifest)
- License/OS/runtime compatibility

If not provable: refuse.

## Gate 3 — Architecture Plan
- File structure and module boundaries
- Data models / schemas touched
- Error model + context propagation
- Logging strategy + redaction

## Gate 4 — Implementation (only now)
Proceed with minimal production change.
No placeholders. No containment. No guessing.

## Verification (Mandatory)
Run: ./scripts/verify
- Must pass.
- If failing: fix and rerun until green or refuse.

Finally include token:
[SHIP:GATES_OK]
MD
