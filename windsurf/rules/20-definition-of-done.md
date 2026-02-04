# Definition of Done (Global)

A task is done only when:
- Implementation is end-to-end and fully integrated.
- No incomplete scaffolding exists anywhere in the change.
- Tests exist that meaningfully constrain behavior and assist debugging.
- Observability compliance is implemented for changed flows:
  - structured logs,
  - correlation propagation,
  - metrics/traces when applicable,
  - redaction enforced.
- Secure-by-default posture is maintained or improved.
- All verification gates pass (local parity with CI).
- KAIZA-AUDIT block is produced and included in the PR description.
