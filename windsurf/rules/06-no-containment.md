sudo tee /etc/windsurf/rules/06-no-containment.md >/dev/null <<'MD'
# NO CONTAINMENT — SYSTEM RULE (ALWAYS ON)

Existing TODOs/FIXMEs/mocks/placeholders may not be:
- documented
- deferred
- moved
- isolated
- wrapped
- re-labeled
- "tracked for later"

They must be eliminated or cause refusal.

Forbidden behaviors:
- moving TODOs to new files
- replacing logic with comments
- adding "known limitation" sections
- creating "debt" notes instead of implementing
MD
