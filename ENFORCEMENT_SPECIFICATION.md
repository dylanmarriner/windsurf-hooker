# 15-Language Code Enforcement Specification

## Scope

This specification applies uniformly across the following 15 languages and their standard ecosystems:

1. Python
2. JavaScript
3. TypeScript
4. Java
5. C
6. C++
7. C#
8. Go
9. Rust
10. PHP
11. Ruby
12. Swift
13. Kotlin
14. R
15. MATLAB

**The rules below are mandatory regardless of language, framework, or platform.**

---

## ABSOLUTE PROHIBITIONS (ZERO TOLERANCE)

- No TODOs, TO-DO, TBDs, FIXMEs, HACKs, TEMP notes, or future-work comments
- No placeholders of any kind (placeholder, dummy, sample, example-only, fake)
- No stub code, skeletons, scaffolds, partial implementations, or unimplemented members
- No mock data, mocks, fakes, stubs, spies, synthetic fixtures, or demo-only values
- No pseudocode, illustrative snippets, commented-out logic, ellipses, or omitted sections
- No deferred assumptions, "left as an exercise," or user-dependent completion
- No explanatory prose outside code artifacts
- No escape attempts (os.system, subprocess, exec, eval, open, Runtime.exec, etc.)

**Enforcement:** `pre_write_code_policy.py` — blocks all absolute prohibitions

---

## MANDATORY IMPLEMENTATION REQUIREMENTS (ALL LANGUAGES)

1. Every function, class, method, module, and entrypoint must be **fully implemented**
2. All logic paths handled explicitly; no undefined or implicit behavior
3. All dependencies must be real, explicit, version-pinned, and installable
4. Configuration must be concrete, validated, and production-ready
5. Inputs and outputs must be strictly defined and validated
6. Error handling must be comprehensive and explicit
7. Deterministic behavior only
8. Code must compile/run as-is without modification

**Enforcement:** `pre_write_code_policy.py` — checks logic preservation and undefined behavior

---

## TESTING REQUIREMENTS — FULL COVERAGE, NO MOCKS

### Universal Requirements

- Provide a complete test suite achieving **100% line and branch coverage**
- Tests must use **real implementations and real data paths only**
- No mocks, fakes, stubs, spies, monkeypatching, or dependency substitution
- Tests must be deterministic, isolated, and repeatable
- Include exact commands to run tests and verify coverage

**Enforcement:** `post_write_coverage_enforcement.py` — verifies test existence and bans mocks

### Language-Specific Test Standards (Mandatory)

| Language   | Framework | Coverage Tool | Command |
|-----------|-----------|---------------|---------|
| Python    | pytest    | coverage.py (branch enabled) | `pytest --cov=src --cov-branch --cov-report=term-missing` |
| JavaScript | Jest or Vitest | built-in coverage | `jest --coverage --collectCoverageFrom='src/**/*.js'` |
| TypeScript | Jest or Vitest | built-in coverage | `jest --coverage --collectCoverageFrom='src/**/*.ts'` |
| Java      | JUnit 5   | JaCoCo (branch coverage) | `mvn clean test jacoco:report` |
| C         | Catch2 or GoogleTest | gcov or llvm-cov | `cmake --build . && ctest && gcov .` |
| C++       | Catch2 or GoogleTest | gcov or llvm-cov | `cmake --build . && ctest && gcov .` |
| C#        | xUnit or NUnit | coverlet | `dotnet test /p:CollectCoverage=true` |
| Go        | go test   | go coverage | `go test -covermode=atomic -coverprofile=coverage.out ./...` |
| Rust      | cargo test | tarpaulin or llvm-cov | `cargo tarpaulin --out Stdout --timeout 120` |
| PHP       | PHPUnit   | PHPUnit coverage | `phpunit --coverage-html=coverage` |
| Ruby      | RSpec or Minitest | simplecov | `bundle exec rspec --coverage` |
| Swift     | XCTest    | Xcode code coverage | `swift test --coverage` |
| Kotlin    | JUnit     | JaCoCo | `gradle test jacocoTestReport` |
| R         | testthat  | covr | `covr::package_coverage()` |
| MATLAB    | matlab.unittest | matlab.codetools.coverage | `runtests('Tests')` |

---

## LINTING & STATIC ANALYSIS — STRICT MODE

### Universal Requirement

- Enforce **strict linting with zero warnings or errors**
- Enforce **static analysis/type checking at the strictest available level**
- Provide concrete configuration files for all tools
- **No suppressions, ignores, or disabled rules allowed**

**Enforcement:** `pre_write_language_compliance.py` — verifies configuration files exist

### Language-Specific Analysis Standards (Mandatory)

| Language   | Tools | Config Files | Strict Mode |
|-----------|-------|--------------|------------|
| Python    | mypy (strict), ruff, flake8 | .flake8, pyproject.toml, ruff.toml | `--strict (mypy)`, `extend-select=E,W,F (ruff)` |
| JavaScript | ESLint (strict), Prettier | .eslintrc.js, eslint.config.mjs | `extends: 'eslint:recommended'` |
| TypeScript | ESLint (strict), TypeScript strict mode, Prettier | tsconfig.json, .eslintrc.js | `strict: true (tsconfig.json)` |
| Java      | SpotBugs, Checkstyle | checkstyle.xml, spotbugs.xml | all rules enabled |
| C         | clang-tidy, compiler warnings as errors | .clang-tidy | `-Wall -Werror -Wextra -pedantic` |
| C++       | clang-tidy, compiler warnings as errors | .clang-tidy | `-Wall -Werror -Wextra -pedantic -std=c++17` |
| C#        | Roslyn analyzers, nullable reference types | .editorconfig | `<Nullable>enable</Nullable>` |
| Go        | go vet, staticcheck | golangci.yml | all linters enabled |
| Rust      | clippy (deny warnings) | clippy.toml | `#![deny(warnings)]` |
| PHP       | PHPStan (max level), PHP_CodeSniffer | phpstan.neon | `level: 9` |
| Ruby      | RuboCop | .rubocop.yml | all cops enabled |
| Swift     | SwiftLint | .swiftlint.yml | all rules enabled |
| Kotlin    | Detekt | detekt.yml | all rules enabled |
| R         | lintr | .lintr | all linters enabled |
| MATLAB    | code analyzer with all warnings enabled | (built-in) | all warnings enabled in checkcode() |

---

## PERFORMANCE CONSTRAINTS (MANDATORY)

- Define explicit time and memory limits suitable for the problem domain
- Enforce constraints with benchmarks, assertions, or tests
- Avoid superlinear algorithms where linear or log-linear is feasible
- Ensure worst-case behavior respects stated limits
- No unbounded memory growth

**Enforcement:** Custom benchmarks and performance tests required

---

## COMPREHENSIVE DOCUMENTATION (ALL LANGUAGES)

- Every function, class, method must have complete docstring (purpose, parameters, return value)
- Complex logic must have inline comments explaining WHY (not WHAT)
- All comments must be accurate and non-trivial
- No empty docstrings or one-liners for functions > 5 lines
- Variable names must be meaningful; no single-letter variables outside loops
- Code must be inherently debuggable through clear naming and documentation

**Enforcement:** `pre_write_comprehensive_comments.py` — enforced across all 15 languages

---

## OUTPUT RULES

- Output only final source code, tests, and required configuration files
- No explanations, notes, commentary, or questions
- No future improvements or suggestions

---

## FAILURE MODE

If any portion cannot be fully implemented under these rules, still produce a complete, working implementation that satisfies all constraints without placeholders.

---

## Hook Enforcement Points

### Pre-Write Hooks (Before Code Acceptance)

1. **pre_write_code_policy.py**
   - Checks: absolute prohibitions, logic preservation, undefined behavior
   - Languages: all 15
   - Exit Code: 2 (block)

2. **pre_write_language_compliance.py**
   - Checks: test configuration, linting configuration presence
   - Languages: all 15
   - Exit Code: 2 (block)

3. **pre_write_comprehensive_comments.py** (existing)
   - Checks: docstrings, inline comments, meaningful names
   - Languages: all 15
   - Exit Code: 2 (block)

### Post-Write Hooks (After Code Written)

1. **post_write_coverage_enforcement.py**
   - Checks: test file existence, mock/stub usage in tests
   - Languages: all 15
   - Exit Code: 2 (block)

2. **post_write_verify.py** (existing)
   - Checks: runs `./scripts/verify` if present
   - Must include: test suite, coverage verification, linting
   - Exit Code: 0 (pass) or 2 (block)

---

## Configuration

All configuration is centralized in `windsurf/policy/policy.json`:

```json
{
  "prohibited_patterns": { ... },
  "language_support": {
    "supported_languages": [
      "python", "javascript", "typescript", "java", "c", "cpp", "csharp",
      "go", "rust", "php", "ruby", "swift", "kotlin", "r", "matlab"
    ]
  },
  "testing_requirements": {
    "coverage_minimum": 100,
    "language_standards": { ... }
  },
  "linting_requirements": {
    "enforcement": "strict with zero warnings or errors",
    "language_standards": { ... }
  }
}
```

---

## Verification

Run verification for your project:

```bash
./scripts/verify
```

This script must execute and return 0 on success:
- Run all tests with coverage (100% required)
- Run all linters in strict mode (zero warnings required)
- Run all type checkers (zero errors required)
- Verify no prohibitions violated
- Compile/build successfully
