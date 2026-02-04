---
name: no-placeholders-production-code
description: Enforce production-ready code with no incomplete scaffolding, stubs, or placeholder implementations. Invoke as @no-placeholders-production-code.
---

# Skill: No Placeholders — Production Code Only

## Purpose
Every function, handler, CLI command, job runner, config file, and module must be fully implemented and integrated. No stubs, `todo!()`, `unimplemented!()`, TODO comments in source, or half-finished integration.

## When to Use This Skill
- Writing new features or modules
- Modifying existing code
- Creating configuration files
- Adding scripts or handlers

## Steps

### 1) Understand the requirement completely
- Read the specification, design doc, or user story.
- Identify all inputs, outputs, error cases, and failure modes.
- Clarify any ambiguities before implementing.

### 2) Design the implementation
- Sketch the data structures, interfaces, and flow.
- Identify dependencies and boundaries.
- Document invariants and preconditions.

### 3) Implement end-to-end
- Write complete, functional code for every function and handler.
- Include all error handling and edge cases.
- Add validation and secure defaults.
- Integrate with existing modules (no isolated stubs).

### 4) Integration checklist
- All imports and dependencies are wired correctly.
- All endpoints/handlers are registered and routed.
- All config values are read and applied.
- All environment variables have defaults or are required with clear errors.

### 5) No incomplete markers
- Block all `TODO`, `FIXME`, `XXX`, and `future` comments in source code.
- When these markers are found, **implement the feature/fix completely**, not just remove the comment.
- Replace `todo!()`, `unimplemented!()`, `panic!()` with deterministic error handling.
- Do not use placeholder variables, mock data, or stubbed functions in production code paths.
- Each marker requires full implementation with tests before code is considered done.

### 6) Test all code paths
- Unit tests for pure logic.
- Integration tests for boundaries.
- Tests that exercise error cases.

### 7) Document and verify
- Verify that `scripts/ci/forbidden_markers_scan.py` passes.
- Verify that all linters and type checkers pass.
- Verify that tests pass.

## Quality Checklist

- [ ] Every function has a body (no stubs).
- [ ] Every error case is handled explicitly.
- [ ] No `TODO`, `FIXME`, `XXX`, `future`, or `unimplemented!()` in source.
- [ ] All incomplete markers were fully implemented (not just removed).
- [ ] All dependencies are imported and wired.
- [ ] All configuration is loaded and applied.
- [ ] Tests cover all code paths and all implementations.
- [ ] Forbidden markers scan passes.
- [ ] Type checker passes.

## Verification Commands

```bash
# Forbidden marker scan
python scripts/ci/forbidden_markers_scan.py --root .

# Type checker (language-dependent)
npm run typecheck        # Node/TS
python -m mypy src      # Python
cargo clippy --all      # Rust

# Tests
npm test
python -m pytest
cargo test --all
```

## How to Recover if You Violate This Skill

If you introduce a placeholder:
1. Immediately go back and implement it fully.
2. Do not commit or push with stubs.
3. If you realize you need more information, stop and output the missing inputs.

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: List of functions/modules touched.
- **Verification**: Include `forbidden_markers_scan.py` output.
- **Key Decisions**: Explain why each implementation choice was made.
- **Results**: Confirm all gates pass.
