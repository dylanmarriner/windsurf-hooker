# Code Quality Specification

## ABSOLUTE PROHIBITIONS (ZERO TOLERANCE)

- No TODOs, TO-DO, TBDs, FIXMEs, HACKs, TEMP notes, or future-work comments
- No placeholders of any kind (placeholder, dummy, sample, example-only, fake)
- No stub code, skeletons, scaffolds, partial implementations, or unimplemented functions
- No mock data, mocks, fakes, stubs, spies, synthetic fixtures, or hardcoded demo values
- No pseudocode, illustrative snippets, commented-out logic, ellipses, or omitted sections
- No deferred assumptions, "left as an exercise," or user-dependent completion
- No explanatory prose outside code

## MANDATORY IMPLEMENTATION REQUIREMENTS

- Every function, class, method, and module must be fully implemented
- All logic paths handled; no unhandled branches or undefined behavior
- All dependencies must be real, explicit, pinned, and installable
- Configuration must be concrete, production-ready, and validated
- Inputs/outputs fully specified with strict validation
- Comprehensive, explicit error handling
- Deterministic behavior
- The code must run as-is without modification

## TESTING REQUIREMENTS (FULL COVERAGE, NO MOCKS)

- Provide a complete test suite achieving 100% line and branch coverage
- Tests must use real implementations and real data paths only
- No mocks, fakes, stubs, spies, monkeypatching, or dependency substitution
- Tests must be deterministic, isolated, and repeatable
- Include clear test execution commands and coverage verification

## PERFORMANCE CONSTRAINTS (MANDATORY)

- Define explicit time and memory limits appropriate to the problem domain
- Enforce performance with measurable benchmarks or assertions
- Avoid unnecessary allocations and superlinear algorithms
- Ensure worst-case behavior respects the stated limits

## LINTING & STATIC ANALYSIS (STRICT COMPLIANCE)

- Enforce strict linting with zero warnings or errors
- Enforce static analysis/type checking with the strictest settings available
- Provide configuration files for linters and analyzers
- Code must pass all checks without suppressions or ignores

## QUALITY BAR

- Production-ready, idiomatic, robust
- Correctness over brevity
- Clean architecture, no dead code
- Clear, precise naming
- Security-conscious defaults

## OUTPUT RULES

- Output only the final code and required configuration/test files
- No explanations, commentary, or suggestions
- No questions
- No future improvements
