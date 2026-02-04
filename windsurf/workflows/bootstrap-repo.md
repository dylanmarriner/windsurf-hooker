# /bootstrap-repo
Initialize or harden a repository for production-grade development (tooling, gates, observability foundations).

## Prerequisites
- Kaiza MCP is configured for the repository root.
- A valid approved plan exists for bootstrapping.

## Inputs
- Target repo root (workspace)
- Primary stack (Node/TS, Python, mixed)
- Services (api, web, worker) if known

## Steps
1) Kaiza preflight
   1. Call Kaiza `read_prompt` with `WINDSURF_CANONICAL`.
   2. Call Kaiza `list_plans` and select the approved bootstrap plan.

2) Discover repo reality
   - Read: root AGENTS.md (if present), package manifests, build scripts, existing CI, runtime configs.
   - Record: entrypoints, commands, test runners, linters, typecheckers.

3) Install enforcement package (minimum)
   - Add `.github/workflows/` CI files (ci, code scanning, release, nightly).
   - Add `scripts/ci/` scanners and validators.
   - Add `.windsurf/` local workflows/rules if the repo should share them with collaborators.
   - Add `observability/` pack specs and optional reference utilities.

4) Observability foundations
   - Ensure a structured log schema is adopted.
   - Ensure correlation IDs exist for API boundaries and job boundaries.
   - Ensure redaction policy exists and is referenced from code.

5) Run local-equivalent gates
   - Execute the repo's canonical lint/format/typecheck/test commands.
   - Run scanners: forbidden markers scan, secret scan (where available), dependency audit.

6) Produce outputs
   - KAIZA-AUDIT block including plan used, files created/updated, verification commands and results.

## Success Criteria
- Repo has deterministic CI enforcement and passes gates.
- Observability conventions are present and referenced.
- Audit trail format is produced.
