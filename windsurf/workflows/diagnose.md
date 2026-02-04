sudo tee /etc/windsurf/workflows/diagnose.md >/dev/null <<'MD'
# /diagnose — Debug-Only (No Code)

Rules:
- Do not write or modify code.
- Only diagnose using repo facts and logs.

Steps:
1) Reproduction steps (exact commands, inputs)
2) Observed vs expected behavior
3) Failure chain (where it breaks, why)
4) Root cause hypothesis ranked by evidence
5) Proposed fixes as verified steps (no code)
6) Prevention: tests, guards, monitoring, docs
MD
