# Hard Fail Criteria — Non-Negotiable Standards

## Zero-Tolerance Absolute Prohibitions

Any of these = **IMMEDIATE HARD FAIL**:

### Placeholder Code
- TODO, TO-DO, TBD, FIXME, XXX, HACK, TEMP
- future-work, left-as-exercise, deferred, user-dependent
- pass, NotImplementedError, unimplemented!(), todo!()
- dummy, null, placeholder, sample, example-only, fake

### Incomplete Implementation
- Empty functions/methods `{ }`
- Stub implementations (just `return`, `raise`, or `throw`)
- Partially implemented code
- Missing branches/logic paths
- Ellipses `...` indicating omitted code
- Commented-out logic
- Pseudocode

### Unsafe/Unhandled Behavior
- Functions with external I/O missing try/catch/error handling
- Undefined return values
- Implicit type conversions without validation
- Unhandled error conditions

### Non-Production Code
- Mock implementations
- Fake/demo data
- Test-only values hardcoded in production code
- Conditionally disabled code (`if False:`, `if DEBUG:`)

### Undefined/Malformed Code
- Syntax errors
- Unresolved imports/dependencies
- Type mismatches (in strict mode)
- Logic errors

---

## Implementation Completeness Requirements

Must **ALL** be true:

1. **Every function/class/method is fully implemented**
   - No stubs, no empty bodies, no partial logic
   
2. **All logic paths are handled**
   - All branches defined
   - All error cases handled
   - No implicit undefined behavior
   
3. **All dependencies are real and pinned**
   - No placeholder dependencies
   - Version constraints explicit
   - All imports resolve
   
4. **Configuration is concrete and validated**
   - No hardcoded test/demo values
   - No magic numbers without justification
   - All config loaded and validated on startup
   
5. **All I/O and external operations are error-handled**
   - File operations in try/catch/with blocks
   - Network calls with timeout and error handling
   - Database operations with transaction handling
   
6. **Behavior is deterministic**
   - No random defaults without seed control
   - No timing-dependent behavior
   - Outputs consistent for same inputs
   
7. **Code runs as-is without modification**
   - No setup scripts needed
   - No manual fixes required
   - All requirements installable

---

## Documentation Requirements

Must **ALL** be true:

1. **Every function has complete docstring**
   - Purpose clearly explained
   - Parameters documented
   - Return value documented
   - Exceptions listed
   
2. **Complex logic has WHY comments**
   - Not WHAT (code shows that)
   - Not HOW (code shows that)
   - WHY (non-obvious design decisions, business logic)
   
3. **Variable names are meaningful**
   - No single-letter variables (except loop indices)
   - No `x`, `y`, `z`, `temp`, `data`, `obj`, `val`
   - Names express intent/purpose
   
4. **No explanatory prose outside code**
   - No readme-style comments in code
   - No future improvement notes
   - No "this could be better" comments

---

## Testing Requirements

Must **ALL** be true:

1. **Complete test coverage: 100% line AND branch**
   - All functions tested
   - All branches tested
   - All error paths tested
   - All edge cases tested
   
2. **No mocks, fakes, stubs, spies, or synthetic fixtures**
   - Tests use real implementations
   - Tests use real data paths
   - Tests are deterministic and repeatable
   
3. **Tests are fast and isolated**
   - Each test independent
   - Tests don't depend on execution order
   - Tests can run in any order
   - Tests are repeatable
   
4. **Test commands documented and working**
   - Clear command to run all tests
   - Clear command to check coverage
   - Coverage reports generated
   - Results verifiable

---

## Linting & Static Analysis

Must **ALL** be true:

1. **Zero warnings or errors**
   - All linter checks pass
   - All type checks pass
   - All analysis tools pass
   
2. **Strict mode enabled everywhere**
   - mypy --strict (Python)
   - TypeScript strict mode
   - ESLint strict config
   - All tools at highest level
   
3. **Configuration files present**
   - .flake8, pyproject.toml, .eslintrc, tsconfig.json, etc.
   - All tools configured explicitly
   - No default configs
   
4. **No suppressions or ignores**
   - No `# type: ignore` comments
   - No `# noqa` pragmas
   - No `@SuppressWarnings`
   - No `eslint-disable`
   - All issues fixed, not hidden

---

## Hook Enforcement Points

### Pre-Write (Block Before Code Accepted)

#### `pre_write_code_policy.py`
- ✗ Any prohibited pattern (TODO, FIXME, dummy, null, etc.) → **HARD FAIL**
- ✗ Empty implementations → **HARD FAIL**
- ✗ Logic removal or deletion → **HARD FAIL**
- ✗ Unhandled exceptions → **HARD FAIL**
- ✗ Test/demo code in production → **HARD FAIL**

#### `pre_write_language_compliance.py`
- ✗ Missing test config (pytest.ini, package.json, etc.) → **HARD FAIL**
- ✗ Missing lint config (.eslintrc, .flake8, etc.) → **HARD FAIL**

#### `pre_write_comprehensive_comments.py`
- ✗ Missing docstrings on functions → **HARD FAIL**
- ✗ Missing WHY comments on complex logic → **HARD FAIL**
- ✗ Bad variable names (x, y, temp, data, etc.) → **HARD FAIL**
- ✗ Incomplete implementation markers → **HARD FAIL**

### Post-Write (Block After Code Written)

#### `post_write_self_contained_enforcement.py` (Self-contained, no ./scripts/verify dependency)
- ✗ Syntax errors in code → **HARD FAIL**
- ✗ Missing test file for source code → **HARD FAIL**
- ✗ Mocks/stubs/fakes in test files → **HARD FAIL**
- ✗ Empty or stub test files → **HARD FAIL**
- ✗ No actual test functions in tests → **HARD FAIL**
- ✗ Missing lint configuration → **HARD FAIL**
- ✗ Missing type checking config (mypy, tsconfig.json) → **HARD FAIL**

#### `post_write_coverage_enforcement.py`
- ✗ No test file found → **HARD FAIL**
- ✗ Mocks in tests → **HARD FAIL**
- ✗ Empty test file → **HARD FAIL**
- ✗ No test functions → **HARD FAIL**

#### `post_write_verify.py` (Self-contained, no ./scripts/verify dependency)
- ✗ Syntax errors → **HARD FAIL**
- ✗ Unmatched braces/brackets/parentheses → **HARD FAIL**
- ✗ Mocks/stubs/fakes in test files → **HARD FAIL**
- ✗ Incomplete code markers (TODO, FIXME, pass, etc.) → **HARD FAIL**

---

## Failure = No Code Commit

If **any** hard fail condition is triggered:

1. Code write is **rejected**
2. No code committed
3. Errors displayed with specific violations
4. No workarounds or suppressions allowed
5. Fix violations and resubmit

---

## Quick Checklist Before Submit

- [ ] Zero TODO/FIXME/XXX comments
- [ ] Zero stub/empty implementations
- [ ] All functions have complete docstrings
- [ ] Complex logic has WHY comments
- [ ] All variables meaningfully named
- [ ] All error paths handled with try/catch
- [ ] Test file exists for all code
- [ ] Tests use real implementations (no mocks)
- [ ] 100% line and branch coverage
- [ ] `./scripts/verify` passes completely
- [ ] All linters pass (zero warnings)
- [ ] All type checks pass (zero errors)
- [ ] Code runs as-is without modification

**If any item is unchecked: HARD FAIL**
