# Refusal Behavior (Internal Agent Rule)

If you cannot produce a fully functional implementation without violating the non-negotiables:
- Do not ask the user questions in the output.
- Stop and output:
  1) A concrete implementation plan (sequenced).
  2) A minimal list of missing inputs required (exact file paths, env vars, interfaces, versions).
  3) The exact verification commands that will be run once inputs exist.
  4) A risk note describing what is blocked and why.

Never fabricate missing information to proceed.
