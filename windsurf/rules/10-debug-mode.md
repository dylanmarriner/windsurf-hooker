sudo tee /etc/windsurf/rules/10-debug-mode.md >/dev/null <<'MD'
# DEBUG-ONLY MODE (MANUAL)

Activation: Manual via @debug_only

When active:
- DO NOT write or modify code.
- Only: diagnose, trace failure chains, propose fixes as verified steps.
- Provide reproduction steps, likely root cause, and prevention strategy.
MD
