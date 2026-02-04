# /create-project-profile
Create a project profile and scoped AGENTS.md structure without duplicating global governance.

## Prerequisites
- Approved plan exists for project profiling.

## Inputs
- Project name
- Repo layout (dirs)
- Canonical commands

## Steps
1) Create `docs/project_profiles/<project>.md` based on template
2) Add root AGENTS.md canonical commands
3) Add scoped AGENTS.md only where conventions diverge
4) Add repo-local delta skills under `.windsurf/skills/` if needed
5) Verify CI gates are present and aligned

## Success Criteria
- Profile exists, scoped AGENTS.md in place, delta skills minimal and correct.
