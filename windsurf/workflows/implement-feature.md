# /implement-feature
Implement a feature end-to-end with tests, security, and observability.

## Prerequisites
- Approved plan exists for the feature scope.

## Inputs
- Feature description
- Expected user journeys / API contracts
- Performance/security constraints

## Steps
1) Kaiza preflight
   - Call `read_prompt` (`WINDSURF_CANONICAL`), then `list_plans`, choose approved plan.

2) Context loading (read-only)
   - Read AGENTS.md (root + relevant subdir).
   - Read the main entrypoints and adjacent modules.
   - Identify: data models, boundaries, auth, validation, error surfaces.

3) Design in-repo (lightweight)
   - Write a short design note into the plan's allowed docs area if required by repo standards.
   - Identify invariants and failure modes.

4) Implement (complete integration)
   - Add/modify code with detailed doc comments.
   - Add validation and secure defaults.
   - Add structured logs and correlation propagation.
   - Add metrics/traces where relevant.

5) Test strategy (debuggable)
   - Unit tests for pure logic.
   - Integration tests for boundaries.
   - Contract tests for external boundaries.
   - Ensure failures provide actionable output.

6) Verify
   - Run lint/format check, typecheck, tests, scanners, and security audit.
   - Capture test reports/artifacts on failures.

7) Deliver
   - Provide KAIZA-AUDIT block.

## Success Criteria
- Feature works end-to-end and is test-constrained.
- Observability compliance is present.
- Security posture improved or maintained.
- All quality gates pass.
