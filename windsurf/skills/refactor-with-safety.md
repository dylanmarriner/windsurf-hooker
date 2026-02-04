# Skill: @refactor-with-safety

**Purpose:** Execute refactors that improve code quality while maintaining correctness: regression testing, behavior preservation verification, incremental rollout, and easy rollback.

**Invocation:** `/use-skill refactor-with-safety` for any code reorganization, optimization, or modernization.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Before any large code change that doesn't add features.
- **Dependencies:** @test-engineering-suite, @debuggable-by-default, @kaiza-mcp-ops.
- **Owner:** Code quality team.

---

## Core Principles

### 1. Regression Testing

Every refactor must prove no behavior changed.

```typescript
/**
 * Strategy: Write comprehensive regression tests BEFORE refactoring.
 * Run tests after refactor to verify behavior identical.
 *
 * If tests pass before and after, behavior is preserved.
 */

// BEFORE: Original implementation
export function calculateDiscount(subtotal: number, couponCode: string): number {
  const coupon = coupons[couponCode];
  if (!coupon) return 0;
  if (coupon.type === "percentage") {
    return Math.round(subtotal * (coupon.value / 100));
  }
  if (coupon.type === "fixed") {
    return coupon.value;
  }
  return 0;
}

// Comprehensive regression tests (run BEFORE refactoring)
describe("calculateDiscount regression", () => {
  test("returns 0 for unknown coupon", () => {
    expect(calculateDiscount(100, "UNKNOWN")).toBe(0);
  });

  test("handles percentage coupon correctly", () => {
    expect(calculateDiscount(100, "PERCENT_10")).toBe(10); // 10% off
  });

  test("handles fixed coupon correctly", () => {
    expect(calculateDiscount(100, "FIXED_5")).toBe(5); // $5 off
  });

  test("rounds correctly for percentage calculations", () => {
    expect(calculateDiscount(33, "PERCENT_10")).toBe(3); // 3.3 rounded to 3
  });

  test("works with edge case values", () => {
    expect(calculateDiscount(0, "PERCENT_10")).toBe(0);
    expect(calculateDiscount(1, "PERCENT_50")).toBe(0); // 0.5 rounds to 0
  });
});

// AFTER: Refactored implementation (behavior identical)
export function calculateDiscount(subtotal: number, couponCode: string): number {
  const coupon = coupons.get(couponCode); // Changed from array to Map for O(1) lookup
  if (!coupon) return 0;

  return coupon.type === "percentage"
    ? Math.round(subtotal * (coupon.value / 100))
    : coupon.type === "fixed"
      ? coupon.value
      : 0;
}

// All regression tests still pass → behavior preserved ✓
```

### 2. Incremental Refactoring

Break large refactors into small, testable steps.

```typescript
/**
 * Example: Refactoring payment processing to use async/await instead of callbacks.
 *
 * Step 1: Create new async version alongside old callback version
 * Step 2: Add tests for new async version
 * Step 3: Migrate callers one-by-one (with feature flags if needed)
 * Step 4: Remove old callback version once all callers migrated
 *
 * Benefits: Easy to roll back at any step; isolated testing for each change.
 */

// Step 1: New async version created alongside old callback version
export async function processPaymentAsync(userId: string, amount: number): Promise<PaymentResult> {
  try {
    const result = await stripeClient.charge({ userId, amount });
    return { success: true, chargeId: result.id };
  } catch (err) {
    return { success: false, error: (err as Error).message };
  }
}

// OLD callback version (kept for now)
export function processPayment(
  userId: string,
  amount: number,
  callback: (err: Error | null, result?: PaymentResult) => void
): void {
  stripeClient.charge({ userId, amount }, (err, result) => {
    if (err) callback(err);
    else callback(null, { success: true, chargeId: result.id });
  });
}

// Step 2: New async version tested thoroughly
describe("processPaymentAsync", () => {
  test("returns success on successful charge", async () => {
    const result = await processPaymentAsync("user-123", 2000);
    expect(result.success).toBe(true);
    expect(result.chargeId).toBeTruthy();
  });

  test("returns error on failed charge", async () => {
    const result = await processPaymentAsync("user-123", 2000); // Mock Stripe to fail
    expect(result.success).toBe(false);
    expect(result.error).toBeTruthy();
  });
});

// Step 3: Migrate callers (use feature flag to control rollout)
export async function checkout(userId: string, amount: number) {
  if (process.env.USE_ASYNC_PAYMENT === "true") {
    // Use new async version
    return await processPaymentAsync(userId, amount);
  } else {
    // Use old callback version
    return new Promise((resolve, reject) => {
      processPayment(userId, amount, (err, result) => {
        if (err) reject(err);
        else resolve(result);
      });
    });
  }
}

// Step 4: Once all callers migrated, remove old callback version
```

### 3. Behavior Preservation Verification

Use multiple validation techniques.

```typescript
/**
 * Validation techniques (apply multiple for high-confidence refactors):
 *
 * 1. Regression tests (before/after run same tests)
 * 2. Property-based tests (verify invariants hold)
 * 3. Output comparison (run old + new in parallel, compare outputs)
 * 4. Performance benchmarks (verify no regression in speed)
 * 5. Integration tests (verify in real environment)
 */

// Technique 1: Regression tests
describe("calculateDiscount regression", () => {
  // ... tests that must pass before and after refactor
});

// Technique 2: Property-based tests (invariants must hold)
import fc from "fast-check";

describe("calculateDiscount properties", () => {
  test("discount is always non-negative", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 1000 }),
        fc.string(),
        (subtotal, coupon) => {
          const discount = calculateDiscount(subtotal, coupon);
          expect(discount).toBeGreaterThanOrEqual(0);
        }
      )
    );
  });

  test("discount never exceeds subtotal", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 0, max: 1000 }),
        fc.string(),
        (subtotal, coupon) => {
          const discount = calculateDiscount(subtotal, coupon);
          expect(discount).toBeLessThanOrEqual(subtotal);
        }
      )
    );
  });
});

// Technique 3: Output comparison (run old + new in parallel)
export function validateRefactor<T>(
  oldImpl: (input: T) => unknown,
  newImpl: (input: T) => unknown,
  testInputs: T[]
): { matches: number; diffs: number } {
  let matches = 0;
  let diffs = 0;

  for (const input of testInputs) {
    const oldOutput = oldImpl(input);
    const newOutput = newImpl(input);

    if (JSON.stringify(oldOutput) === JSON.stringify(newOutput)) {
      matches++;
    } else {
      diffs++;
      console.error("Output mismatch for input:", input, {
        old: oldOutput,
        new: newOutput,
      });
    }
  }

  return { matches, diffs };
}

// Usage in tests
test("refactored calculateDiscount matches original", () => {
  const testCases = [
    { subtotal: 100, coupon: "UNKNOWN" },
    { subtotal: 100, coupon: "PERCENT_10" },
    { subtotal: 33, coupon: "PERCENT_10" },
  ];

  const result = validateRefactor(
    (input) => calculateDiscountOld(input.subtotal, input.coupon),
    (input) => calculateDiscount(input.subtotal, input.coupon),
    testCases
  );

  expect(result.diffs).toBe(0);
  expect(result.matches).toBe(testCases.length);
});

// Technique 4: Performance benchmarks
import benchmark from "benchmark";

const suite = new benchmark.Suite();

suite
  .add("calculateDiscountOld", () => {
    calculateDiscountOld(100, "PERCENT_10");
  })
  .add("calculateDiscount (refactored)", () => {
    calculateDiscount(100, "PERCENT_10");
  })
  .on("complete", function () {
    console.log("Performance comparison:");
    for (const bench of this) {
      console.log(
        `${bench.name}: ${Math.round(bench.hz)} ops/sec`
      );
    }

    // Verify refactored version is not significantly slower
    const oldHz = this[0].hz;
    const newHz = this[1].hz;
    const slowdown = (1 - newHz / oldHz) * 100;

    if (slowdown > 10) {
      console.warn(`WARNING: Refactored version is ${slowdown.toFixed(1)}% slower`);
    }
  })
  .run({ async: true });
});
```

### 4. Safe Rollback

Every refactor includes a rollback plan.

```typescript
/**
 * Rollback strategy: Feature flags + git history
 *
 * 1. Refactor is behind a feature flag (new code path)
 * 2. If issues found in production, flip flag to immediately revert to old code
 * 3. Root cause analysis conducted offline
 * 4. Once fixed, re-enable with confidence
 */

// Feature flag to control which code path is used
export const FEATURE_FLAGS = {
  USE_NEW_PAYMENT_PROCESSING: process.env.USE_NEW_PAYMENT_PROCESSING === "true",
};

export async function processPayment(userId: string, amount: number) {
  if (FEATURE_FLAGS.USE_NEW_PAYMENT_PROCESSING) {
    // NEW: Refactored async version
    return await processPaymentNewImpl(userId, amount);
  } else {
    // OLD: Original callback-based version
    return await processPaymentOldImpl(userId, amount);
  }
}

// In production, if issues occur:
// 1. Toggle feature flag: USE_NEW_PAYMENT_PROCESSING=false
// 2. Immediately reverts to old code (no code deploy needed)
// 3. Investigate issue offline
// 4. Fix and re-enable with confidence

// Monitoring to detect issues
export async function safeProcessPayment(userId: string, amount: number) {
  const startTime = performance.now();

  try {
    const result = await processPayment(userId, amount);
    const duration = performance.now() - startTime;

    logger.info("payment processed", {
      userId,
      amount,
      duration_ms: duration,
      impl: FEATURE_FLAGS.USE_NEW_PAYMENT_PROCESSING ? "new" : "old",
    });

    return result;
  } catch (err) {
    logger.error("payment failed", {
      userId,
      amount,
      errorCode: err instanceof DomainError ? err.errorCode : "UNKNOWN",
      impl: FEATURE_FLAGS.USE_NEW_PAYMENT_PROCESSING ? "new" : "old",
    });

    throw err;
  }
}

// Alert on increased error rate
// If error_rate[impl=new] > error_rate[impl=old] * 1.5, page on-call engineer
```

### 5. Code Review Checklist for Refactors

```markdown
## Refactor Code Review Checklist

- [ ] Regression tests pass (all tests from before refactor still pass)
- [ ] No new TODOs, FIXMEs, or placeholders introduced
- [ ] Behavior verified identical (property tests, output comparison, or both)
- [ ] Performance not regressed (benchmark results or reasoning)
- [ ] Rollback plan documented (feature flag, git revert, etc.)
- [ ] Incremental refactor (not trying to change everything at once)
- [ ] All callsites updated (if API changed)
- [ ] Old code removed (only if new code is proven correct)
- [ ] New code has same test coverage as old code
- [ ] Commit message explains why (not just what)
```

---

## Step-by-Step Refactoring Process

### Step 1: Understand Current Behavior

- Read existing code thoroughly
- Run tests to understand expected behavior
- Document current invariants and edge cases

### Step 2: Write Comprehensive Regression Tests

- Test all code paths (happy path, error paths, edge cases)
- Run tests; confirm all pass with current code
- Keep these tests; they'll verify refactored code

### Step 3: Plan Refactor

- Document desired changes (what will be different, why)
- Identify risks and mitigation strategies
- Plan incremental steps (don't refactor everything at once)

### Step 4: Refactor Incrementally

- Make small, testable changes
- Run tests after each change
- Verify behavior identical to original

### Step 5: Add New Tests (if needed)

- Test new code paths (if refactor adds functionality)
- Do not remove old tests

### Step 6: Verify Equivalence

- Use multiple validation techniques (regression tests, property tests, benchmarks)
- Compare outputs of old and new implementations
- Verify performance acceptable

### Step 7: Deploy with Feature Flag

- Deploy behind feature flag (if significant change)
- Monitor error rates, latency, resource usage
- Gradually enable flag (e.g., 10% → 25% → 50% → 100%)
- Plan rollback (how to instantly revert if issues)

### Step 8: Remove Old Code

- Only remove old code once new code proven correct in production
- Keep old code in git history (for reference/rollback)
- Document deprecation (why old code no longer needed)

---

## Quality Checklist

- [ ] Regression tests written and passing before refactor.
- [ ] All tests still pass after refactor.
- [ ] Behavior verified identical (regression tests + property tests + benchmarks).
- [ ] No new placeholders, TODOs, or stubs introduced.
- [ ] Incremental refactoring (not trying to change everything at once).
- [ ] Rollback plan documented and tested.
- [ ] Performance benchmarked (no regression or justified).
- [ ] Code review confirms equivalence.
- [ ] Kaiza MCP audit trail recorded (before/after behavior, verification results).
- [ ] Old code removed only after new code proven in production.

---

## Deliverable Summary

```json
{
  "skill": "refactor-with-safety",
  "completed": true,
  "refactor_details": {
    "scope": "Refactored calculateDiscount to use Map instead of array",
    "lines_changed": 12,
    "files_modified": ["src/checkout/discount.ts"]
  },
  "regression_tests": {
    "total": 8,
    "all_pass": true
  },
  "behavior_verification": {
    "regression_tests": "passed",
    "property_tests": "passed",
    "output_comparison": { "matches": 20, "diffs": 0 },
    "performance_benchmark": "new is 5% faster"
  },
  "rollback_plan": {
    "mechanism": "Feature flag USE_NEW_DISCOUNT_CALC",
    "revert_time": "< 1 minute"
  },
  "old_code_removal": {
    "status": "removed",
    "git_history": "preserved",
    "archived_as": "calculateDiscountOld (kept for reference)"
  }
}
```

---

## Related Skills

- @test-engineering-suite (regression tests)
- @debuggable-by-default (monitoring during rollout)
- @kaiza-mcp-ops (deployment with feature flags)
- /pre-pr-review (code review for refactors)
