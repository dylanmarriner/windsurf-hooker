# Workflow: /refactor-module

**Purpose:** Refactor code safely: improve structure/performance while preserving behavior.

**Prerequisites:** Refactoring goal clear, behavior must be preserved.

**Inputs:**
- Module name: `<module-name>`
- Goal: `<what-will-improve>`
- Reason: `<why-needed>`

---

## Steps

### 1. Understand Current Implementation
Use skill: **@repo-understanding**
```
[ ] Read current module code thoroughly
[ ] Understand how it's used (grep for imports)
[ ] Document current behavior (docstrings)
[ ] Identify invariants and edge cases
```

### 2. Write Comprehensive Regression Tests
**BEFORE refactoring, write tests that cover current behavior completely.**

```typescript
describe("<module> regression tests (before refactor)", () => {
  test("happy path scenario", () => {
    const result = moduleFunction(input);
    expect(result).toEqual(expectedOutput);
  });

  test("edge case: empty input", () => {
    const result = moduleFunction("");
    expect(result).toEqual(defaultValue);
  });

  test("error case: invalid input", () => {
    expect(() => moduleFunction(null)).toThrow("Input required");
  });

  // Add many more tests covering all code paths
});
```

Verify all tests pass with current code:
```bash
npm test -- --testNamePattern="regression" --verbose
# All tests PASS ✓
```

### 3. Plan Refactoring
Use skill: **@refactor-with-safety**

Document refactoring plan:
```markdown
## Refactoring Plan: <Module>

### Goal
<What will improve> (e.g., "Improve performance from O(n²) to O(n log n)")

### Changes
- File1.ts: Replace nested loops with binary search
- File2.ts: Extract helper function for reusability
- File3.ts: Use Map instead of array for O(1) lookup

### Invariants to Preserve
- Function signature (inputs/outputs unchanged)
- Error behavior (same exceptions thrown for same inputs)
- Performance requirements (at least as fast, ideally faster)

### Risks
- Refactoring could introduce subtle behavioral changes
- Test coverage might not catch all edge cases

### Mitigation
- Regression tests validate behavior unchanged
- Property-based tests check invariants hold
- Output comparison: run old and new in parallel
- Performance benchmarks: verify no slowdown
```

### 4. Refactor Incrementally
Make small, testable changes. After each change:

```bash
npm test -- --testNamePattern="regression"
# Verify regression tests still pass
```

Example of incremental approach:
1. Extract helper function (small refactor, tests pass)
2. Use Map instead of array (small refactor, tests pass)
3. Replace nested loops with binary search (small refactor, tests pass)

**Never refactor everything at once.**

### 5. Validate Behavior Preservation
Use skill: **@refactor-with-safety**

Multiple validation techniques:

```typescript
// Technique 1: Regression tests (already passing)
npm test -- --testNamePattern="regression"

// Technique 2: Property-based tests (invariants hold)
import fc from "fast-check";
test("refactored module preserves invariants", () => {
  fc.assert(
    fc.property(fc.string(), (input) => {
      const oldOutput = moduleOld(input);
      const newOutput = moduleNew(input);
      expect(newOutput).toEqual(oldOutput);
    })
  );
});

// Technique 3: Output comparison (old vs new)
const testCases = [
  { input: "", expected: "default" },
  { input: "abc", expected: "ABC" },
  { input: "xyz", expected: "XYZ" },
];

for (const { input, expected } of testCases) {
  expect(moduleNew(input)).toEqual(moduleOld(input));
}

// Technique 4: Performance benchmark
console.time("old implementation");
for (let i = 0; i < 1000; i++) moduleOld(generateInput());
console.timeEnd("old implementation");

console.time("new implementation");
for (let i = 0; i < 1000; i++) moduleNew(generateInput());
console.timeEnd("new implementation");
```

### 6. Run Full Test Suite
```bash
npm run lint
npm run typecheck
npm test -- --coverage

# All must pass, coverage must not decrease
```

### 7. Create Audit Summary
Document: `docs/refactors/<module-name>.md`

```markdown
## Refactoring: <Module>
**Goal:** <What improved>
**Author:** <your-name>
**Date:** <date>

### What Changed
- File1.ts: Replaced nested loops with binary search
- File2.ts: Extracted helper function
- File3.ts: Use Map instead of array

### Why
<Reason for refactoring>
Performance improvement: O(n²) → O(n log n)
Readability: Extracted complex logic into named function
Maintainability: Map provides clearer intent than array

### Behavior Verification
- Regression tests: All 47 passing (behavior unchanged)
- Property tests: Invariants hold for random inputs
- Output comparison: Old vs new produce identical output
- Performance: New implementation 3x faster

### Code Review
Reviewed by: @alice
Comments: "Excellent incremental refactoring, tests comprehensive"

### Risks Mitigated
- Regression tests ensure no behavioral changes
- Incremental approach catches issues early
- Property tests validate invariants
```

### 8. Push & Open PR
```bash
git add .
git commit -m "refactor: <module> - <goal>

Improves: <what improved (performance, readability, maintainability)>

Changes:
- File1.ts: Replaced nested loops with binary search (O(n²) → O(n log n))
- File2.ts: Extracted helper function for clarity
- File3.ts: Use Map instead of array (O(n) → O(1) lookup)

Behavior preserved:
- All 47 regression tests passing
- Output comparison: old and new produce identical results
- Performance improvement: 3x faster for large inputs

See docs/refactors/<module-name>.md for full analysis."

git push origin refactor/<module-name>
```

### 9. Code Review
Reviewer verifies:
- [ ] Regression tests all passing (behavior preserved)
- [ ] Refactoring incremental (not trying to change everything)
- [ ] No new TODOs or placeholders
- [ ] Readability improved (not sacrificed)
- [ ] Performance verified (benchmarks shown)
- [ ] Risk mitigation in place

### 10. Merge & Deploy
```bash
git checkout main
git pull
git merge refactor/<module-name>
git push origin main
```

---

## Success Criteria

- [ ] Regression tests written and passing before refactor
- [ ] All regression tests pass after refactor
- [ ] Behavior verified identical (tests + property tests + output comparison)
- [ ] Refactoring incremental (not all-or-nothing)
- [ ] Performance verified (benchmarks or reasoning provided)
- [ ] No new TODOs, FIXMEs, or placeholders
- [ ] Code review approved
- [ ] CI all green
- [ ] Audit summary documented
- [ ] Merged and deployed

---

## Related Skills & Workflows

- @repo-understanding (understand current code)
- @refactor-with-safety (safe refactoring practices)
- @test-engineering-suite (comprehensive regression tests)
- @no-placeholders-production-code (complete refactoring)
- @kaiza-mcp-ops (pre-flight checks before merge)
- /pre-pr-review (comprehensive code review)
