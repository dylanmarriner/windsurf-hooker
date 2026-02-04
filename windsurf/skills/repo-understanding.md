# Skill: @repo-understanding

**Purpose:** Quickly understand repository structure, conventions, architecture, dependencies, and constraints before making changes.

**Invocation:** `/use-skill repo-understanding` before implementing features, fixing bugs, or refactoring.

---

## Metadata

- **Scope:** Global (applies to all workspaces).
- **Trigger:** First step of any coding task.
- **Dependencies:** None (foundational).
- **Owner:** Architecture team.

---

## Step-Based Instructions

### Step 1: Understand Repository Structure

```bash
# Explore directory layout
find . -type f -name "*.md" | head -20  # Documentation files
ls -la                                   # Top-level files
tree -d -L 2                            # Directory structure (2 levels)

# Identify project type
cat package.json | grep -E '"name"|"type"|"description"'  # NPM project
cat Cargo.toml | grep -E '^\[package\]' -A 5              # Rust project
cat go.mod | head -5                                        # Go project
```

Key directories to identify:
- **Source code:** `src/`, `lib/`, `app/`, `packages/`, `crates/`
- **Tests:** `__tests__/`, `test/`, `tests/`, `spec/`
- **Configuration:** `.github/workflows/`, `tsconfig.json`, `jest.config.js`, `Cargo.toml`
- **Documentation:** `docs/`, `README.md`, `CONTRIBUTING.md`
- **CI/CD:** `.github/workflows/`, `.gitlab-ci.yml`, `Justfile`
- **Build/Package:** `dist/`, `build/`, `target/`

### Step 2: Identify Project Architecture & Tech Stack

```typescript
/**
 * Document the architecture in your workspace memory:
 */

const PROJECT_PROFILE = {
  name: "my-app",
  type: "full-stack web application",
  frontend: {
    language: "TypeScript",
    framework: "React",
    bundler: "Webpack",
    testing: "Jest + React Testing Library",
  },
  backend: {
    language: "TypeScript",
    framework: "Express",
    database: "PostgreSQL",
    orm: "Prisma",
    testing: "Jest + Supertest",
  },
  monorepo: {
    tool: "Yarn Workspaces",
    packages: ["packages/ui", "packages/api", "packages/core"],
  },
  ci_cd: {
    platform: "GitHub Actions",
    workflows: ["ci.yml", "release.yml"],
  },
  key_conventions: {
    naming: "camelCase for functions/variables, PascalCase for classes/components",
    testing: "__.test.ts suffix for test files",
    logging: "structured JSON via StructuredLogger",
    errors: "Domain-specific error classes extending Error",
  },
};
```

### Step 3: Examine Existing Code Patterns

```typescript
/**
 * Read representative files to understand patterns:
 */

// 1. Find main entry point
cat src/index.ts          // or main.ts, app.ts, etc.

// 2. Read core business logic (not tests)
cat src/auth/jwt.ts       // Authentication
cat src/db/models.ts      // Data models
cat src/api/routes.ts     // API endpoints

// 3. Read test examples (to understand testing style)
cat src/auth/jwt.test.ts  // Unit test pattern
cat src/api/routes.integration.test.ts  // Integration test pattern

// 4. Read configuration files
cat tsconfig.json         // TypeScript config
cat jest.config.js        // Testing config
cat .eslintrc.json        // Linting config

// Document patterns found:
const PATTERNS = {
  error_handling: "domain-specific error classes (PaymentError, AuthError, etc.)",
  logging: "structured JSON with requestId correlation",
  testing: "AAA pattern (Arrange-Act-Assert), one assertion per test",
  async: "async/await (not callbacks or .then() chains)",
  imports: "ES6 imports (not CommonJS require)",
  types: "strict TypeScript (no any, noImplicitAny: true)",
};
```

### Step 4: Map Dependencies & External Services

```typescript
/**
 * Understand what this project depends on:
 */

// External dependencies
npm list --depth=0  // Top-level dependencies

// Internal modules (how code is organized)
// Document module structure:
const MODULES = {
  auth: {
    exports: ["validateJWT", "generateTokens", "JWTValidationError"],
    internal_deps: ["logger", "config"],
    external_deps: ["jsonwebtoken", "bcrypt"],
  },
  payment: {
    exports: ["processPayment", "PaymentError"],
    internal_deps: ["auth", "db", "logger"],
    external_deps: ["stripe"],
  },
  db: {
    exports: ["prisma", "migrate", "seed"],
    internal_deps: ["logger"],
    external_deps: ["@prisma/client", "postgres"],
  },
};

// External services
const EXTERNAL_SERVICES = {
  stripe: {
    purpose: "Payment processing",
    auth: "API key in STRIPE_SECRET_KEY env var",
    error_codes: ["card_declined", "rate_limited", "authentication_error"],
    docs: "https://stripe.com/docs/api",
  },
  email: {
    purpose: "Send emails (reset password, receipts, etc.)",
    provider: "SendGrid or similar",
    config: "SENDGRID_API_KEY env var",
  },
};
```

### Step 5: Understand Testing Strategy

```typescript
/**
 * How is this project tested?
 */

// Unit tests
grep -r "describe\|test\|it(" src/**/*.test.ts | head -10

// Integration tests
ls src/**/*.integration.test.ts

// Test coverage targets
cat jest.config.js | grep -A 5 coverageThreshold

// Test patterns observed:
const TEST_PATTERNS = {
  unit_tests: {
    location: "same directory as implementation (__.test.ts)",
    structure: "describe blocks per function, test per scenario",
    assertions: "expect(...).toBe(...), expect(...).toThrow(...), etc.",
  },
  integration_tests: {
    location: "same directory as integration (__.integration.test.ts)",
    setup: "beforeAll() to start test database, afterAll() to cleanup",
    pattern: "use real database, real HTTP client (supertest), mock external services",
  },
  coverage_target: 80, // percent
  key_strategies: [
    "one assertion per test (avoid cascade failures)",
    "test names describe behavior (rejects_expired_tokens, not test_jwt)",
    "error paths tested explicitly",
  ],
};
```

### Step 6: Identify Quality Gates & CI/CD

```typescript
/**
 * What checks must pass before merge?
 */

// Read CI configuration
cat .github/workflows/ci.yml

// Document gates:
const QUALITY_GATES = {
  lint: {
    tool: "eslint",
    config: ".eslintrc.json",
    command: "npm run lint",
  },
  typecheck: {
    tool: "tsc",
    config: "tsconfig.json",
    command: "npm run typecheck",
  },
  test: {
    runner: "jest",
    config: "jest.config.js",
    coverage_threshold: 80,
    command: "npm test -- --coverage",
  },
  security_scan: {
    tool: "npm audit",
    command: "npm audit --audit-level moderate",
  },
  placeholder_scan: {
    patterns: ["TODO", "FIXME", "stub", "mock", "placeholder"],
    command: "npm run check:placeholders",
  },
};

// Deployment process
cat .github/workflows/release.yml

const RELEASE_PROCESS = {
  trigger: "tag created (v*.*.*)  or manual dispatch",
  steps: [
    "Build artifacts",
    "Run full test suite",
    "Verify signatures/checksums",
    "Generate changelog",
    "Publish to npm/docker/etc.",
    "Deploy to production",
  ],
};
```

### Step 7: Document Architectural Decisions

```typescript
/**
 * Why was this project built this way?
 */

// Read CONTRIBUTING.md, docs/, or architecture docs
cat CONTRIBUTING.md
cat docs/ARCHITECTURE.md

// Document key decisions:
const ARCHITECTURAL_DECISIONS = {
  monorepo_structure: {
    why: "Share code between frontend and backend",
    tool: "Yarn Workspaces",
    cost: "More complex build, harder to parallelize",
  },
  typescript: {
    why: "Type safety reduces bugs in large codebase",
    strict: true,
  },
  prisma_orm: {
    why: "Type-safe database queries, auto-generated types",
    alternative_considered: "TypeORM, Sequelize",
  },
  structured_logging: {
    why: "Easier to parse logs, correlate requests, debug production issues",
    format: "JSON with requestId, userId, operationName, etc.",
  },
  test_coverage_80: {
    why: "Catches most bugs without excessive test maintenance",
    exceptions: ["generated code", "trivial getters", "UI components"],
  },
};
```

### Step 8: Identify Known Issues & Constraints

```typescript
/**
 * What limitations or known issues exist?
 */

// Read issues, PRs, docs
cat KNOWN_ISSUES.md  // if exists
grep -r "TODO\|HACK\|FIXME\|BUG" src/ | head -10

// Interview (via code/comments/docs):
const CONSTRAINTS_AND_ISSUES = {
  performance: {
    slow_query: "User list endpoint takes >2s for 100k users; needs pagination",
    mitigation: "Pagination added in PR #456, but not deployed yet",
  },
  tech_debt: {
    legacy_auth: "Old callback-based auth middleware still used in some routes",
    mitigation: "Migrating to async/await version (PR #789)",
  },
  operational: {
    database: "PostgreSQL 12, must maintain compatibility for 2+ more years",
    versions_supported: "Node.js 16+, not yet ready for 20",
  },
  security: {
    SSRF_protection: "Not yet implemented; needed before accepting user-provided URLs",
  },
};
```

### Step 9: Create Repository Memory

Store understanding in Windsurf Memory:

```json
{
  "repo_name": "my-app",
  "repo_url": "https://github.com/org/my-app",
  "understanding_date": "2026-01-15",
  "project_type": "Full-stack web application (React + Express + PostgreSQL)",
  "key_directories": {
    "src": "Source code",
    "src/auth": "Authentication logic (JWT, password hashing)",
    "src/api": "Express routes and middleware",
    "src/db": "Database models and migrations (Prisma)",
    "src/__tests__": "Tests"
  },
  "tech_stack": {
    "frontend": "TypeScript, React, Webpack",
    "backend": "TypeScript, Express, PostgreSQL, Prisma ORM",
    "testing": "Jest, Supertest, React Testing Library"
  },
  "naming_conventions": {
    "files": "camelCase for functions, PascalCase for classes",
    "tests": "__.test.ts or __.integration.test.ts",
    "errors": "Domain-specific classes (PaymentError, AuthError)"
  },
  "testing_strategy": {
    "unit_tests": "> 60% of tests, fast, no I/O",
    "integration_tests": "20-30% of tests, real database/HTTP",
    "coverage_threshold": 80
  },
  "quality_gates": [
    "npm run lint",
    "npm run typecheck",
    "npm test -- --coverage",
    "npm audit",
    "npm run check:placeholders"
  ],
  "known_constraints": [
    "User list endpoint slow for 100k+ users (pagination needed)",
    "Old callback-based auth middleware in some routes (migration in progress)",
    "SSRF protection not yet implemented (needed before URL processing)"
  ],
  "key_external_services": [
    "Stripe (payment processing)",
    "SendGrid (email)",
    "AWS S3 (file storage)"
  ]
}
```

---

## Verification Checklist

After understanding the repository, verify you can answer:

- [ ] What is the project's main purpose?
- [ ] What language(s) and framework(s) are used?
- [ ] What is the directory structure? (src/, tests/, docs/, etc.)
- [ ] How are tests organized and executed?
- [ ] What are the quality gates (lint, typecheck, test, security)?
- [ ] What naming conventions are used?
- [ ] What error handling patterns are used?
- [ ] What logging/observability is in place?
- [ ] What external services does the project depend on?
- [ ] What are known constraints or tech debt?
- [ ] How is the project deployed?
- [ ] Who are the maintainers/owners?

---

## Quality Checklist

- [ ] Repository structure understood (directories, files, organization).
- [ ] Project type identified (web app, library, CLI, microservice).
- [ ] Tech stack documented (languages, frameworks, databases, tools).
- [ ] Key modules and their dependencies mapped.
- [ ] Testing strategy understood (unit, integration, coverage targets).
- [ ] Quality gates identified (lint, typecheck, test, security).
- [ ] Naming conventions and patterns documented.
- [ ] External service dependencies understood.
- [ ] Known issues and constraints documented.
- [ ] CI/CD process understood (how code is tested and deployed).
- [ ] Architectural decisions recorded (why design is this way).
- [ ] Repository memory created (for future reference in this workspace).

---

## Deliverable Summary

```json
{
  "skill": "repo-understanding",
  "completed": true,
  "repository": {
    "name": "my-app",
    "type": "Full-stack web application",
    "url": "https://github.com/org/my-app"
  },
  "understanding": {
    "project_type": "identified",
    "tech_stack": "documented",
    "directory_structure": "mapped",
    "modules": "dependencies_documented",
    "testing_strategy": "understood",
    "quality_gates": "identified",
    "naming_conventions": "documented",
    "external_services": "enumerated",
    "known_constraints": "recorded",
    "architectural_decisions": "documented"
  },
  "memory_created": true,
  "ready_to_implement": true
}
```

---

## Related Skills

- All other skills (depend on repository understanding as foundation)
- /implement-feature (uses this understanding to plan feature)
- /fix-bug (uses this understanding to locate affected code)
- /refactor-module (uses this understanding to identify related code)
