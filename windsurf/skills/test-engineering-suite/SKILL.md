---
name: test-engineering-suite
description: Design and write tests that meaningfully constrain behavior, provide fast feedback, and assist debugging. Invoke as @test-engineering-suite.
---

# Skill: Test Engineering Suite

## Purpose
Tests should detect regressions quickly, explain failures clearly, and help you debug without re-running scenarios manually. Every behavior change needs a test that would fail if the behavior regressed.

## When to Use This Skill
- Writing new features or functions
- Fixing bugs (write regression test first)
- Refactoring code
- Adding error handling
- Modifying integrations

## Steps

### 1) Understand what you're testing
- What behavior should the code exhibit?
- What are the success and failure cases?
- What are the edge cases?
- What invariants must always hold?

### 2) Write tests before code (when possible)
For bug fixes and new features:
- Write a test that fails with the current code
- Implement the fix or feature
- Verify the test passes
- This ensures your fix actually addresses the issue

Example:
```javascript
// BEFORE: Test fails (demonstrates the bug)
test('should reject password with less than 8 characters', () => {
  expect(() => validatePassword('short')).toThrow('Password must be at least 8 characters');
});

// AFTER: Code passes the test
function validatePassword(pwd) {
  if (pwd.length < 8) {
    throw new Error('Password must be at least 8 characters');
  }
}
```

### 3) Unit tests: test pure functions in isolation
For functions without side effects:
- Call the function with different inputs
- Assert the output is correct
- Keep tests deterministic (no random data, fixed timestamps)

Example:
```javascript
import { calculateDiscount } from './pricing';

test('should calculate 10% discount for $100 purchase', () => {
  expect(calculateDiscount(100, 0.1)).toEqual(10);
});

test('should handle $0 purchases', () => {
  expect(calculateDiscount(0, 0.1)).toEqual(0);
});

test('should reject negative discounts', () => {
  expect(() => calculateDiscount(100, -0.1)).toThrow();
});
```

### 4) Integration tests: test boundaries and interactions
For code that touches external services (DB, HTTP, files):
- Mock or stub external dependencies
- Test the full request→response cycle
- Verify error handling for failed dependencies
- Verify structured logs are emitted

Example:
```javascript
test('should create user and return 201', async () => {
  const mockDb = { insert: jest.fn().mockResolvedValue({ id: 1, email: 'test@example.com' }) };
  const app = createApp(mockDb);
  
  const res = await app.request.post('/users').send({ email: 'test@example.com' });
  
  expect(res.status).toBe(201);
  expect(mockDb.insert).toHaveBeenCalledWith({ email: 'test@example.com' });
});

test('should return 500 if database fails', async () => {
  const mockDb = { insert: jest.fn().mockRejectedValue(new Error('DB down')) };
  const app = createApp(mockDb);
  
  const res = await app.request.post('/users').send({ email: 'test@example.com' });
  
  expect(res.status).toBe(500);
});
```

### 5) Contract tests: verify external service behavior
For code that calls external services:
- Test against real or well-mocked service
- Verify request format and response parsing
- Verify error handling for service failures

Example:
```javascript
test('should parse Stripe API response correctly', async () => {
  const mockStripe = nock('https://api.stripe.com')
    .post('/v1/charges')
    .reply(200, { id: 'ch_123', amount: 1000, status: 'succeeded' });
  
  const result = await chargeCard('ch_123', 1000);
  
  expect(result.id).toBe('ch_123');
  expect(mockStripe.isDone()).toBe(true);
});
```

### 6) Error path tests: verify failures are handled
For every code path that can fail:
- Write a test that triggers the failure
- Verify the error is handled (not thrown unexpectedly)
- Verify logs are emitted with error details

Example:
```javascript
test('should log error and return 503 on timeout', async () => {
  const logs = [];
  jest.spyOn(console, 'error').mockImplementation(msg => logs.push(msg));
  
  const mockDb = { query: jest.fn().mockRejectedValue(new Error('timeout')) };
  const result = await queryUsers(mockDb);
  
  expect(result).toEqual({ error: 'Service temporarily unavailable' });
  expect(logs[0]).toContain('timeout');
});
```

### 7) Test structure: Arrange-Act-Assert
Every test should follow this pattern:
```javascript
test('description of behavior', () => {
  // Arrange: Set up the test environment
  const input = { email: 'test@example.com' };
  const expected = { id: 1, email: 'test@example.com' };
  
  // Act: Call the function
  const result = createUser(input);
  
  // Assert: Verify the result
  expect(result).toEqual(expected);
});
```

### 8) Avoid test anti-patterns
- **Don't**: Skip tests with `.skip` in committed code
- **Don't**: Use `any` mocking that doesn't verify behavior
- **Don't**: Create flaky tests that pass/fail randomly
- **Don't**: Test implementation details instead of behavior
- **Do**: Make tests deterministic (use fixed seeds for randomness)
- **Do**: Test observable behavior, not internals

### 9) Coverage targets
- Aim for 80% statement coverage globally
- Aim for 90%+ coverage on critical paths (auth, payments, physics)
- Don't chase coverage; focus on meaningful tests

### 10) Run tests frequently
- Run tests locally before committing
- Run full suite in CI on every PR
- Run nightly test suite with stricter checks

## Quality Checklist

- [ ] Tests exist for all new functions
- [ ] Regression test exists for every bug fix
- [ ] Error handling is tested
- [ ] Logs are verified in tests
- [ ] Mocks/stubs are used for external services
- [ ] Tests are deterministic (no flakiness)
- [ ] Tests are fast (<5 seconds for unit tests)
- [ ] Coverage is >=80% globally, >=90% for critical paths
- [ ] Tests follow Arrange-Act-Assert structure
- [ ] Test names describe the expected behavior

## Verification Commands

```bash
# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run integration tests (if separate)
npm run test:integration

# Run tests in watch mode during development
npm test -- --watch

# Generate coverage report
npm test -- --coverage --coverageReporters=html
open coverage/index.html
```

## How to Recover if You Violate This Skill

If you add code without tests:
1. Stop and write tests first
2. Ensure the test fails without the code
3. Implement the code
4. Verify the test passes
5. Check coverage

## KAIZA-AUDIT Compliance

When using this skill, your KAIZA-AUDIT block must include:
- **Scope**: Functions/modules with new or updated tests
- **Verification**: Include test output showing all tests pass
- **Coverage**: Include coverage percentages for changed code
- **Results**: Confirm no flaky tests; all tests are deterministic
