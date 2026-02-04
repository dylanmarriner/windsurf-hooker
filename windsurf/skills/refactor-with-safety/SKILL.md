---
name: refactor-with-safety
description: Refactor code incrementally while maintaining test coverage and behavior equivalence. Invoke as @refactor-with-safety.
---

# Skill: Refactor with Safety

## Purpose
Refactoring should improve code clarity, performance, or maintainability without changing observable behavior. This skill ensures refactorings are small, testable, and verifiable.

## When to Use This Skill
- Simplifying logic or removing duplication
- Renaming variables or functions for clarity
- Reorganizing module structure
- Updating to new APIs or frameworks
- Performance optimization
- Debt reduction

## Steps

### 1) Establish baseline behavior
Before refactoring, ensure:
- All tests pass
- Performance baselines are captured (if optimization is the goal)
- Coverage is high enough to detect regressions

```bash
npm test
npm test -- --coverage
# Capture baseline metrics if optimization is the goal
```

### 2) Write characterization tests
For code you're refactoring, write tests that capture the current behavior, even if it seems wrong.

Example:
```javascript
// These tests document current behavior before refactoring
test('calculateTotal with empty items returns 0', () => {
  expect(calculateTotal([])).toEqual(0);
});

test('calculateTotal applies 10% discount to items over $100', () => {
  const items = [{ price: 150, quantity: 1 }];
  expect(calculateTotal(items)).toEqual(135);  // 150 * 0.9
});
```

These tests become your safety net: if the refactored code changes behavior, the tests fail.

### 3) Plan the refactoring
Break the refactoring into small, logical steps:
- Each step should be committable and testable
- Each step should take <1 hour to code and verify
- No step should require multiple files to be changed simultaneously

Example plan:
```
Step 1: Extract calculateDiscount function
Step 2: Rename itemTotal to lineTotal for clarity
Step 3: Simplify the loop using reduce
Step 4: Add memoization for repeated calls
Step 5: Run full suite and verify performance improvement
```

### 4) Refactor incrementally
For each step:
1. Make one small change
2. Run tests to verify behavior is preserved
3. Commit the change
4. Move to next step

Example refactoring:

Before:
```javascript
function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    let itemTotal = item.price * item.quantity;
    if (itemTotal > 100) {
      itemTotal = itemTotal * 0.9;  // 10% discount
    }
    total += itemTotal;
  }
  return total;
}
```

Step 1: Extract discount calculation:
```javascript
function calculateDiscount(price) {
  return price > 100 ? price * 0.9 : price;
}

function calculateTotal(items) {
  let total = 0;
  for (let i = 0; i < items.length; i++) {
    const item = items[i];
    let itemTotal = item.price * item.quantity;
    itemTotal = calculateDiscount(itemTotal);
    total += itemTotal;
  }
  return total;
}
```
Test: `npm test` ✓ All tests pass

Step 2: Rename for clarity:
```javascript
function calculateLineTotal(price, quantity) {
  const lineTotal = price * quantity;
  return calculateDiscount(lineTotal);
}

function calculateTotal(items) {
  let total = 0;
  for (const item of items) {
    total += calculateLineTotal(item.price, item.quantity);
  }
  return total;
}
```
Test: `npm test` ✓ All tests pass

Step 3: Use reduce:
```javascript
function calculateTotal(items) {
  return items.reduce(
    (total, item) => total + calculateLineTotal(item.price, item.quantity),
    0
  );
}
```
Test: `npm test` ✓ All tests pass

### 5) Verify behavior is unchanged
After each step, run tests:
```bash
npm test
npm test -- --coverage
```

Ensure:
- All tests pass
- Coverage does not decrease
- No new failures or warnings

### 6) Verify performance (if optimization is the goal)
Compare baseline metrics with refactored code:
```bash
# Baseline (before refactoring)
time npm test
# Output: real 0m2.345s

# After refactoring
time npm test
# Output: real 0m2.310s
# ✓ Slightly faster
```

### 7) Property-based testing (for complex logic)
For algorithms or complex transformations, use property-based testing to verify invariants are preserved:

```javascript
import fc from 'fast-check';

test('calculateTotal is invariant under order of items', () => {
  fc.assert(
    fc.property(fc.array(fc.record({
      price: fc.integer(1, 10000),
      quantity: fc.integer(1, 100),
    })), (items) => {
      const shuffled = [...items].sort(() => Math.random() - 0.5);
      expect(calculateTotal(items)).toEqual(calculateTotal(shuffled));
    })
  );
});
```

### 8) Commit small, logical changes
Each commit should be:
- Testable in isolation
- Understandable without reading the diff
- Safe to revert if needed

Good commit messages:
```
Extract calculateDiscount function for clarity

- calculateDiscount isolates the 10% discount logic
- Tested by existing test suite
- No behavior change
```

Bad commit messages:
```
Refactor calculateTotal

- Cleaned up code
- Made it better
```

## Quality Checklist

- [ ] All tests pass before refactoring
- [ ] Characterization tests capture current behavior
- [ ] Refactoring is broken into small steps
- [ ] Each step runs tests and passes
- [ ] Coverage does not decrease
- [ ] Performance baselines are compared (if optimization)
- [ ] Commits are small and logical
- [ ] No unrelated changes mixed in
- [ ] Property-based tests pass (if applicable)
- [ ] Full suite passes at the end

## Verification Commands

```bash
# Before refactoring
npm test -- --coverage
git log --oneline | head -5

# After each step
npm test

# Final verification
npm test -- --coverage
npm run lint
npm run typecheck

# Performance check (if optimization)
time npm test
# Compare with baseline
```

## How to Recover if Refactoring Breaks

If tests fail during refactoring:
1. Revert the last commit: `git revert HEAD`
2. Identify what broke
3. Plan a smaller step
4. Try again

If you discover a bug during refactoring:
1. Stop the refactoring
2. Commit the refactoring changes (even if incomplete)
3. Fix the bug in a separate PR
4. Resume refactoring in a new PR

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: Modules/functions refactored
- **Key Decisions**: Why this refactoring improves the code (clarity, performance, testability)
- **Verification**: All tests pass, coverage maintained or improved, performance baselines compared
- **Risk Notes**: Any assumptions about behavior preservation; edge cases to watch
