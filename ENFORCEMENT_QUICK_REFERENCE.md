# 15-Language Enforcement — Quick Reference

## What Gets Blocked

| Category | Examples | Hook |
|----------|----------|------|
| Placeholders | TODO, FIXME, XXX, dummy, null, TBD, pass, unimplemented | `pre_write_code_policy.py` |
| Incomplete Code | stub, skeleton, scaffold, partial, ... (ellipsis) | `pre_write_code_policy.py` |
| Mock/Fakes | Mock(), fake data, demo data, stub(), spy() | `pre_write_code_policy.py` + `post_write_coverage_enforcement.py` |
| Comments | HACK, TEMP, "left as exercise", explanatory prose | `pre_write_code_policy.py` |
| Missing Tests | No test file found for source code | `post_write_coverage_enforcement.py` |
| Test Mocks | Mock/Stub/Fake in test code | `post_write_coverage_enforcement.py` |
| Missing Docs | No docstring on function/class | `pre_write_comprehensive_comments.py` |
| Missing Config | No pytest.ini, tsconfig.json, .eslintrc, etc. | `pre_write_language_compliance.py` |

## Checklist Before Commit

- [ ] No TODO/FIXME/XXX comments
- [ ] No placeholder code (dummy, null, pass, stub)
- [ ] All functions have docstrings
- [ ] Complex code has WHY comments
- [ ] All variables meaningfully named
- [ ] Tests exist for all code
- [ ] No mocks/fakes in tests (real implementations only)
- [ ] Test coverage = 100% (line + branch)
- [ ] Linting passes with zero warnings
- [ ] Type checking passes with zero errors
- [ ] Code compiles/runs without modification
- [ ] `./scripts/verify` passes

## By Language

### Python
```bash
# Test: pytest --cov=src --cov-branch --cov-report=term-missing
# Lint: mypy --strict, ruff, flake8
# Files: pytest.ini, pyproject.toml, .flake8
```

### JavaScript/TypeScript
```bash
# Test: jest --coverage
# Lint: eslint (strict), prettier
# Files: package.json, tsconfig.json, .eslintrc.js
```

### Java
```bash
# Test: mvn clean test jacoco:report
# Lint: SpotBugs, Checkstyle
# Files: pom.xml, checkstyle.xml
```

### C/C++
```bash
# Test: cmake --build . && ctest && gcov .
# Lint: clang-tidy, -Wall -Werror
# Files: CMakeLists.txt, .clang-tidy
```

### Go
```bash
# Test: go test -covermode=atomic -coverprofile=coverage.out ./...
# Lint: go vet, staticcheck
# Files: go.mod, golangci.yml
```

### Rust
```bash
# Test: cargo test
# Lint: cargo clippy -- -D warnings
# Files: Cargo.toml, clippy.toml
```

### C#
```bash
# Test: dotnet test /p:CollectCoverage=true
# Lint: Roslyn analyzers
# Files: .csproj, .editorconfig
```

### PHP
```bash
# Test: phpunit --coverage-html=coverage
# Lint: PHPStan level 9
# Files: composer.json, phpstan.neon
```

### Ruby
```bash
# Test: bundle exec rspec --coverage
# Lint: rubocop
# Files: Gemfile, .rubocop.yml
```

### Swift
```bash
# Test: swift test --coverage
# Lint: swiftlint
# Files: Package.swift, .swiftlint.yml
```

### Kotlin
```bash
# Test: gradle test jacocoTestReport
# Lint: detekt
# Files: build.gradle, detekt.yml
```

### R
```bash
# Test: covr::package_coverage()
# Lint: lintr
# Files: DESCRIPTION, .lintr
```

### MATLAB
```bash
# Test: runtests('Tests')
# Lint: checkcode() with all warnings
# Files: (built-in)
```

## Policy File

Located: `windsurf/policy/policy.json`

Contains:
- All prohibited patterns (per category)
- Language-specific test framework requirements
- Language-specific linting tool requirements
- Implementation requirements
- Performance constraints

## Hooks Execution Order

1. `pre_write_code_policy.py` — prohibitions + logic
2. `pre_write_language_compliance.py` — config files
3. `pre_write_comprehensive_comments.py` — documentation
4. Code is written
5. `post_write_coverage_enforcement.py` — tests + mocks
6. `post_write_verify.py` — runs `./scripts/verify`

## If Tests Fail

1. Ensure 100% coverage: `./scripts/verify`
2. Remove all mocks: use real implementations
3. Add missing tests: create test files
4. Fix linting: run tool with `--fix` if available
5. Fix type errors: strict mode enabled

## If Documentation Missing

1. Add docstrings to all functions/classes
2. Explain WHY in comments (not WHAT)
3. Use meaningful variable names
4. Remove placeholder/generic names

## If Configuration Missing

1. Create `pytest.ini`, `package.json`, `tsconfig.json`, etc.
2. Enable strict mode in all tools
3. Add `.eslintrc`, `.flake8`, `.clang-tidy`, etc.
4. Verify tools run with zero warnings
