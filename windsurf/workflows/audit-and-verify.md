# /audit-and-verify
Run the full verification stack and produce a PR-ready audit block.

## Prerequisites
- Repo has canonical commands in AGENTS.md
- CI scripts exist under scripts/ci/

## Inputs
- None (uses repo scripts)

## Steps
1) Run forbidden marker scan
   - `python scripts/ci/forbidden_markers_scan.py --root .`

2) Run lint / format check / typecheck / tests (when present)
   - `bash scripts/ci/run_if_present.sh lint`
   - `bash scripts/ci/run_if_present.sh format:check`
   - `bash scripts/ci/run_if_present.sh typecheck`
   - `bash scripts/ci/run_if_present.sh test`
   - `bash scripts/ci/run_if_present.sh test:integration`

3) Run audits
   - `bash scripts/ci/node_audit.sh`
   - secret scan via gitleaks (CI)
   - license check (Node) `node scripts/ci/license_check.mjs`

4) Produce KAIZA-AUDIT block for PR body
   - Include command outputs and artifact pointers on failures

## Success Criteria
- All gates pass or failures are clearly documented with repro steps and artifacts.
- KAIZA-AUDIT block is ready to paste into PR description.
