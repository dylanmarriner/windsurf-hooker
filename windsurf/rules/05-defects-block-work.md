sudo tee /etc/windsurf/rules/05-defects-block-work.md >/dev/null <<'MD'
# DEFECTS BLOCK WORK — SYSTEM RULE (ALWAYS ON)

Prime rule:
- The AI is forbidden from working in any affected scope that contains unresolved:
  - TODO / FIXME / XXX
  - mock/fake/demo data
  - placeholder/stub logic
  - commented-out executable code
  - "assume", "temporary", "for now", "hack"

Mandatory state machine:
- AUDIT → (REPAIR if defects exist) → VERIFY → SHIP
- If defects exist in scope:
  - No new features
  - No unrelated refactors
  - No stylistic changes
  - Only defect elimination
- If any defect cannot be eliminated safely:
  - STOP and REFUSE (refusal is success)

Defect closure required per item:
- ✅ FIXED — replaced with real implementation
- 🗑 REMOVED — deleted because it should not exist
- ⛔ BLOCKED — cannot be fixed safely; reason stated; work stops

Clean-codebase invariant:
- After any AI operation touching a scope, that scope must contain:
  - zero TODOs
  - zero FIXMEs
  - zero mock/fake/demo data
  - zero placeholder/stub logic
  - zero commented-out executable code
MD
