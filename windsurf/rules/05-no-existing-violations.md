# NO EXISTING VIOLATIONS — SYSTEM RULE (ALWAYS ON)

The codebase must not contain unresolved placeholders or mock artifacts.

Prohibited in existing code:
- TODO / FIXME / XXX
- pass / ... / unimplemented
- stub functions
- commented-out logic
- mock or fake data
- hardcoded demo values

When violations are present:
- Windsurf MUST treat remediation as mandatory work
- Windsurf MUST NOT isolate, defer, or compartmentalize violations
- Windsurf MUST remove or fully implement them
- If safe remediation cannot be proven → REFUSE

It is not acceptable to:
- move violations
- wrap them
- document them
- defer them
- annotate them

Violation elimination is required before any new functionality.
