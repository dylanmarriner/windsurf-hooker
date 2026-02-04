sudo tee /etc/windsurf/rules/00-production-or-nothing.md >/dev/null <<'MD'
# PRODUCTION OR NOTHING (SYSTEM ENFORCEMENT) — ALWAYS ON

Non-negotiable:
- Never emit code that cannot be shipped to production.
- If correctness cannot be guaranteed with repo evidence: REFUSE (refusal is success).

Hard blocks (never introduce):
- TODO, FIXME, XXX
- pass, ..., unimplemented
- stub functions, placeholder returns, fake/demo data
- commented-out logic
- "simplified example", "assume this exists", pseudocode disguised as code

Safety blocks:
- No swallowed/ignored errors.
- No silent fallbacks or default-success behavior.
- No ignored return values.
- No undefined behavior or race-unsafe patterns.

Reality Lock:
- If any required input, schema, API contract, version, or behavior is missing or ambiguous:
  - STOP and ask for missing facts, OR REFUSE.
  - No guessing.

Mandatory gates (before any code edits):
- Gate 1: restate inputs/outputs/constraints/perf/failure modes/external deps
- Gate 2: confirm deps exist + pinned versions + license/OS/runtime compatibility
- Gate 3: architecture plan (files/modules/models/errors/logging)
- Only then: implementation

Compile-assumption:
- Behave as if code will be compiled/executed immediately.
- If it would not build/test: do not emit it.

Error-first:
- Structured/typed errors (or equivalent), propagated with context.
- Public functions must document failure modes.

No hallucinated interfaces:
- Only use APIs/types/functions that exist in-repo OR in pinned dependencies.
MD
