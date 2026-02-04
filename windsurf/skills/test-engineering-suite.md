# Skill: @test-engineering-suite

**Purpose:** Implement comprehensive, production-grade testing strategy: unit tests, integration tests, contract tests, property-based tests, and failure replay tests. Achieve >80% coverage with tests that catch real bugs.

**Invocation:** `/use-skill test-engineering-suite` or automatic for all features/bugfixes.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** Before merge; CI enforces test requirements.
- **Dependencies:** @no-placeholders-production-code, @audit-first-commentary.
- **Owner:** Test & quality engineering.

---

## Test Pyramid & Strategy

```
                  /\
                 /  \
                /E2E \          < 10% (slow, brittle, high-value)
               /      \
              /--------\
             /  Integration \ < 20-30% (moderate speed, good coverage)
            /                \
           /------------------\
          /    Unit Tests       \ > 50-60% (fast, deterministic)
         /________________________\
```

- **Unit Tests (>60%):** Individual functions/modules in isolation. Target: fast (<100ms each), deterministic, no I/O.
- **Integration Tests (20-30%):** Multiple modules working together. Target: cover real workflows, catch misconfigurations.
- **E2E Tests (<10%):** Full stack from API boundary. Target: high-value flows only (happy path + critical failures).
- **Contract Tests:** Verify APIs match caller expectations (especially for internal services).

### Testing Principles

1. **Test Names Describe Behavior:** `test_rejects_expired_tokens`, not `test_jwt_validation`.
2. **Arrange-Act-Assert:** Clear test structure (setup, action, verification).
3. **One Assertion Per Test (Ideally):** Avoid cascade failures.
4. **Test Real Behavior:** Don't test implementation details.
5. **Minimal Fixtures:** Use real objects when possible; mock only external dependencies.
6. **Error Paths Explicitly Tested:** Each error code/type has its own test.

---

## Unit Testing Example

```typescript
describe("validateJWT", () => {
  const testSecret = "test-secret-key";
  const validClaims = { userId: "user-123", role: "admin" };

  describe("valid tokens", () => {
    test("returns decoded claims for valid token", () => {
      const token = jwt.sign(validClaims, testSecret);
      const result = validateJWT(token, testSecret);
      expect(result).toEqual(validClaims);
    });

    test("handles claims with exp field", () => {
      const futureExp = Math.floor(Date.now() / 1000) + 3600;
      const claims = { ...validClaims, exp: futureExp };
      const token = jwt.sign(claims, testSecret);
      const result = validateJWT(token, testSecret);
      expect(result.exp).toBe(futureExp);
    });
  });

  describe("expired tokens", () => {
    test("throws JWTValidationError with TOKEN_EXPIRED code", () => {
      const expiredToken = jwt.sign(validClaims, testSecret, { expiresIn: "-1h" });
      expect(() => validateJWT(expiredToken, testSecret)).toThrow(
        expect.objectContaining({ code: "TOKEN_EXPIRED" })
      );
    });
  });

  describe("invalid signature", () => {
    test("throws JWTValidationError with INVALID_TOKEN code", () => {
      const token = jwt.sign(validClaims, testSecret);
      expect(() => validateJWT(token, "wrong-secret")).toThrow(
        expect.objectContaining({ code: "INVALID_TOKEN" })
      );
    });
  });

  describe("malformed tokens", () => {
    test("throws MALFORMED code for non-JWT string", () => {
      expect(() => validateJWT("not-a-jwt", testSecret)).toThrow(
        expect.objectContaining({ code: "MALFORMED" })
      );
    });
  });

  describe("configuration", () => {
    test("uses HMAC_SECRET env var if secret param not provided", () => {
      const savedEnv = process.env.HMAC_SECRET;
      process.env.HMAC_SECRET = testSecret;
      try {
        const token = jwt.sign(validClaims, testSecret);
        const result = validateJWT(token);
        expect(result).toEqual(validClaims);
      } finally {
        process.env.HMAC_SECRET = savedEnv;
      }
    });

    test("throws error if secret not provided and HMAC_SECRET not set", () => {
      const savedEnv = process.env.HMAC_SECRET;
      delete process.env.HMAC_SECRET;
      try {
        expect(() => validateJWT("token")).toThrow("HMAC_SECRET not configured");
      } finally {
        process.env.HMAC_SECRET = savedEnv;
      }
    });
  });

  describe("repro: issue #789 - error context missing userId", () => {
    test("error includes context even when token invalid", () => {
      const malformedToken = "invalid";
      try {
        validateJWT(malformedToken, testSecret);
        fail("should have thrown");
      } catch (err) {
        expect((err as JWTValidationError).context).toBeTruthy();
        expect((err as JWTValidationError).context).toHaveProperty("correlationId");
      }
    });
  });
});
```

---

## Integration Testing Example

```typescript
import request from "supertest";
import app from "./app";
import { db } from "./db";

describe("Auth Service Integration", () => {
  beforeAll(async () => {
    await db.connect("test");
    await db.migrate();
  });

  afterAll(async () => {
    await db.disconnect();
  });

  beforeEach(async () => {
    await db.clear();
  });

  describe("POST /auth/login", () => {
    test("returns token for valid credentials", async () => {
      await db.users.create({
        email: "user@example.com",
        passwordHash: await hashPassword("correct-password"),
      });

      const response = await request(app).post("/auth/login").send({
        email: "user@example.com",
        password: "correct-password",
      });

      expect(response.status).toBe(200);
      expect(response.body.token).toBeTruthy();
      expect(response.body.token).toMatch(/^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$/);
    });

    test("rejects invalid credentials", async () => {
      await db.users.create({
        email: "user@example.com",
        passwordHash: await hashPassword("correct-password"),
      });

      const response = await request(app).post("/auth/login").send({
        email: "user@example.com",
        password: "wrong-password",
      });

      expect(response.status).toBe(401);
      expect(response.body.error).toBeTruthy();
    });
  });

  describe("end-to-end workflow", () => {
    test("user can register, login, and access protected resource", async () => {
      const registerResponse = await request(app).post("/auth/register").send({
        email: "newuser@example.com",
        password: "secure-password-123",
      });
      expect(registerResponse.status).toBe(201);

      const loginResponse = await request(app).post("/auth/login").send({
        email: "newuser@example.com",
        password: "secure-password-123",
      });
      expect(loginResponse.status).toBe(200);
      const token = loginResponse.body.token;

      const protectedResponse = await request(app)
        .get("/user/profile")
        .set("Authorization", `Bearer ${token}`);
      expect(protectedResponse.status).toBe(200);
      expect(protectedResponse.body.email).toBe("newuser@example.com");
    });
  });
});
```

---

## Contract Testing Example

```typescript
import nock from "nock";

describe("Stripe API Contract", () => {
  const stripeClient = new stripe.Stripe(process.env.STRIPE_SECRET_KEY!);

  describe("POST /v1/charges", () => {
    test("returns charge object with expected fields on success", async () => {
      const mockResponse = {
        id: "ch_1234567890",
        object: "charge",
        amount: 2000,
        currency: "usd",
        status: "succeeded",
        created: 1234567890,
        paid: true,
      };

      nock("https://api.stripe.com").post("/v1/charges").reply(200, mockResponse);

      const charge = await stripeClient.charges.create({
        amount: 2000,
        currency: "usd",
        source: "tok_visa",
      });

      expect(charge.id).toBeTruthy();
      expect(typeof charge.id).toBe("string");
      expect(charge.amount).toBe(2000);
      expect(charge.status).toBe("succeeded");
    });

    test("throws specific error type on card decline", async () => {
      const mockErrorResponse = {
        error: {
          type: "card_error",
          code: "card_declined",
          message: "Your card was declined",
        },
      };

      nock("https://api.stripe.com").post("/v1/charges").reply(402, mockErrorResponse);

      expect(async () => {
        await stripeClient.charges.create({
          amount: 2000,
          currency: "usd",
          source: "tok_chargeDeclined",
        });
      }).rejects.toThrow(stripe.errors.StripeCardError);
    });
  });
});
```

---

## Property-Based Testing Example

```typescript
import fc from "fast-check";

describe("JWT encoding/decoding properties", () => {
  test("encoding then decoding preserves claims (round-trip property)", () => {
    fc.assert(
      fc.property(fc.object({ maxDepth: 2 }), (claims) => {
        const encoded = encodeJWT(claims, "secret");
        const decoded = decodeJWT(encoded, "secret");
        expect(decoded).toEqual(claims);
      })
    );
  });

  test("changing secret makes decoding fail", () => {
    const testData = fc.tuple(fc.object(), fc.string({ minLength: 10 }));

    fc.assert(
      fc.property(testData, ([claims, secret]) => {
        const encoded = encodeJWT(claims, secret);
        const wrongSecret = secret + "wrong";
        expect(() => decodeJWT(encoded, wrongSecret)).toThrow();
      })
    );
  });
});
```

---

## Snapshot Testing Example

```typescript
describe("Error message formatting", () => {
  test("JWT validation error formats correctly", () => {
    const error = new JWTValidationError("token expired", "TOKEN_EXPIRED", {
      correlationId: "req-123",
      userId: "user-456",
    });

    expect(error.toJSON()).toMatchSnapshot();
  });
});
```

---

## Coverage Requirements

```typescript
// jest.config.js
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80,
    },
    "src/auth/**": {
      branches: 90,
      functions: 90,
      lines: 90,
      statements: 90,
    },
    "src/payment/**": {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95,
    },
  },
};
```

---

## Test Organization

```
src/
  auth/
    jwt.ts          # Implementation
    jwt.test.ts     # Unit tests
    jwt.integration.test.ts  # Integration tests
    __mocks__/
      stripe.ts     # Mock for Stripe API
```

---

## Running Tests Locally

```bash
npm test
npm test -- --coverage
npm test -- jwt.test.ts
npm test -- --testNamePattern="expired"
npm test -- --watch
npm test -- --updateSnapshot
npm test -- --verbose
```

---

## CI Integration

```yaml
- name: Run tests
  run: npm test -- --coverage --ci

- name: Check coverage
  run: npm test -- --coverage --coverageReporters=text-summary

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    files: ./coverage/coverage-final.json
```

---

## Quality Checklist

- [ ] Unit tests for core logic (>60% of tests).
- [ ] Integration tests for workflows (20-30% of tests).
- [ ] E2E tests for critical paths (<10% of tests).
- [ ] Test names describe behavior (not implementation).
- [ ] Error paths explicitly tested (each error code has a test).
- [ ] Edge cases tested (empty input, null values, boundary conditions).
- [ ] Mocks used only for external dependencies (Stripe, email, etc.).
- [ ] Real objects used where possible (database, HTTP client).
- [ ] Coverage ≥80% (target 90% for auth/payment).
- [ ] Minimal repro test for each bugfix.
- [ ] Property tests for parsing/validation logic.
- [ ] Snapshot tests for complex output.
- [ ] Contract tests for third-party APIs.
- [ ] Tests deterministic (no flaky/random timeouts).
- [ ] Tests fast (<100ms for unit, <1s for integration).

---

## Deliverable Summary

```json
{
  "skill": "test-engineering-suite",
  "completed": true,
  "test_metrics": {
    "total_tests": 47,
    "unit_tests": 28,
    "integration_tests": 15,
    "e2e_tests": 4,
    "coverage": {
      "statements": 88,
      "branches": 85,
      "functions": 88,
      "lines": 88
    }
  },
  "test_types": {
    "unit": "28 (59.6%)",
    "integration": "15 (31.9%)",
    "contract": "2 (4.3%)",
    "property_based": "2 (4.3%)"
  },
  "all_tests_pass": true,
  "coverage_thresholds_met": true
}
```

---

## Related Skills

- @no-placeholders-production-code (complete, runnable code)
- @audit-first-commentary (test documentation)
- @debuggable-by-default (error capture in tests)
- /pre-pr-review (test coverage requirements)
