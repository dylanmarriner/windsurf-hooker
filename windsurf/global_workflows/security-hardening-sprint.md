# Workflow: /security-hardening-sprint

**Purpose:** Implement security improvements: vulnerability remediation, hardening critical paths, and audit coverage gaps.

**Prerequisites:** Security audit completed, vulnerabilities identified, prioritized.

**Inputs:**
- Sprint goal: `<security-goal>`
- Vulnerabilities: `<list-of-cves-or-issues>`
- Priority: `<critical|high|medium>`

---

## Steps

### 1. Prioritize Security Issues
Prioritize by severity and exploitability:

```json
{
  "critical": [
    {
      "id": "CVE-2025-1234",
      "title": "SQL injection in user search endpoint",
      "severity": "critical",
      "exploitability": "high",
      "impact": "Complete database compromise",
      "status": "not_patched"
    }
  ],
  "high": [
    {
      "id": "SSRF-001",
      "title": "Open redirect vulnerability",
      "severity": "high",
      "exploitability": "high",
      "impact": "Phishing attacks",
      "status": "not_fixed"
    }
  ]
}
```

### 2. Understand Each Vulnerability
```
[ ] Read CVE details / security advisory
[ ] Identify affected code
[ ] Understand attack vector
[ ] Determine scope (how many users affected)
[ ] Assess exploitability (is this easy to exploit?)
```

### 3. Create Security Tests
**Before fixing, create tests that verify the vulnerability.**

```typescript
describe("SQL injection prevention", () => {
  test("rejects SQL injection attempts in user search", () => {
    const maliciousInput = "'; DROP TABLE users; --";
    
    // This should NOT execute the SQL injection
    const results = searchUsers(maliciousInput);
    
    // Should safely treat input as literal search term
    expect(results.length).toBe(0);
    
    // Verify table still exists (not dropped)
    const allUsers = getAllUsers();
    expect(allUsers.length).toBeGreaterThan(0);
  });

  test("correctly escapes SQL special characters", () => {
    const input = "user's name";
    const results = searchUsers(input);
    // Should find users with apostrophes in names
    expect(results).toContain(expect.objectContaining({ name: "John's User" }));
  });
});

describe("SSRF protection", () => {
  test("rejects redirect to private IP addresses", () => {
    expect(() => validateRedirectURL("http://127.0.0.1:8080")).toThrow("Denied host");
    expect(() => validateRedirectURL("http://10.0.0.1")).toThrow("Denied network");
    expect(() => validateRedirectURL("http://172.16.0.1")).toThrow("Denied network");
    expect(() => validateRedirectURL("http://192.168.0.1")).toThrow("Denied network");
  });

  test("rejects redirect to AWS metadata service", () => {
    expect(() => validateRedirectURL("http://169.254.169.254/latest/meta-data")).toThrow("Denied host");
  });

  test("allows redirect to public URLs", () => {
    expect(validateRedirectURL("https://example.com")).toBeTruthy();
    expect(validateRedirectURL("https://google.com")).toBeTruthy();
  });
});
```

### 4. Fix Vulnerabilities
Use skill: **@secure-by-default**

```typescript
// VULNERABLE: SQL injection possible
export function searchUsers(query: string): User[] {
  const sql = `SELECT * FROM users WHERE name LIKE '%${query}%'`;
  return db.execute(sql);
}

// FIXED: Parameterized query
export function searchUsers(query: string): User[] {
  const sql = `SELECT * FROM users WHERE name LIKE $1`;
  return db.execute(sql, [`%${query}%`]); // Parameters passed separately
}

// VULNERABLE: Open redirect
export function redirect(url: string, res: Response) {
  res.redirect(url);
}

// FIXED: SSRF protection
export function redirect(url: string, res: Response) {
  const validated = validateRedirectURL(url); // Check against allowlist
  res.redirect(validated);
}
```

### 5. Verify Security Tests Pass
```bash
npm test -- --testNamePattern="security|injection|ssrf|csrf"
# All security tests must pass after fix
```

### 6. Run Security Scans
```bash
# Dependency vulnerability scan
npm audit --audit-level moderate
npx snyk test

# SAST (static analysis for code vulnerabilities)
npx semgrep --config "p/security-audit" src/

# Container scanning (if Docker)
trivy image my-app:latest

# DAST (dynamic analysis - in staging)
# Run security scanning tools against running app
```

### 7. Add to CI Security Gates
Ensure security checks run on every PR:

```yaml
# .github/workflows/ci.yml
- name: Security Scan (npm audit)
  run: npm audit --audit-level moderate

- name: Dependency Scan (snyk)
  run: npx snyk test

- name: SAST (semgrep)
  run: npx semgrep --config "p/security-audit" src/

- name: License Check
  run: npx licensee --production

- name: Secret Scanning
  run: npx detect-secrets scan --baseline .secretbase
```

### 8. Document Security Changes
Document: `docs/security/hardening-<sprint-date>.md`

```markdown
## Security Hardening Sprint: <Date>
**Lead:** <your-name>
**Duration:** <sprint-dates>
**Vulnerabilities Fixed:** 5

### Vulnerabilities Addressed

#### 1. SQL Injection in User Search (CVE-2025-1234) - CRITICAL
**Severity:** Critical
**Status:** Fixed ✓

**Vulnerability:**
User search endpoint vulnerable to SQL injection via query parameter.

**Attack:**
```
GET /api/users/search?q='; DROP TABLE users; --
```

**Fix:**
Changed from string concatenation to parameterized queries.

**Code Changes:**
- src/api/routes.ts: Use parameterized query (line 42)
- src/api/routes.test.ts: Added SQL injection test

**Verification:**
- SQL injection test: Passing ✓
- All 127 tests: Passing ✓
- Semgrep SAST scan: Clean ✓
- npm audit: 0 vulnerabilities ✓

#### 2. Open Redirect / SSRF (SSRF-001) - HIGH
**Severity:** High
**Status:** Fixed ✓

**Vulnerability:**
Redirect endpoint accepts arbitrary URLs, enabling phishing attacks.

**Attack:**
```
GET /api/redirect?url=https://evil.com (attacker controlled)
```

**Fix:**
Added allowlist validation, denies private IPs and cloud metadata services.

**Code Changes:**
- src/api/routes.ts: Added validateRedirectURL() (line 67)
- src/security/validation.ts: New SSRF protection module
- src/__tests__/security.test.ts: Added SSRF tests

**Verification:**
- SSRF tests: All passing ✓
- Allowlist validated against OWASP list ✓
- CI security gates: All passing ✓

### Security Gates Added to CI
- `npm audit --audit-level moderate`: Fail on vulnerabilities
- `npx snyk test`: Fail on known vulnerabilities
- `npx semgrep --config "p/security-audit"`: SAST scanning
- `npx licensee --production`: Ensure allowed licenses

### Testing
- Security tests added: 8 new tests
- Total test count: 135 (was 127)
- Coverage: 89% (maintained)
- All tests passing: ✓

### Deployment Impact
- Database migrations: None
- Breaking changes: None
- Backward compatibility: Full
- Rollback: Simple revert (no data changes)

### Recommendations for Future
1. Implement DAST (dynamic security testing) in staging
2. Add rate limiting on sensitive endpoints (login, payment)
3. Implement Web Application Firewall (WAF) rules
4. Conduct penetration testing quarterly

### Approval
- **Security Review:** @security-team (reviewed and approved)
- **Code Review:** @alice (reviewed and approved)
```

### 9. Push & Open PR
```bash
git add .
git commit -m "security: fix SQL injection and SSRF vulnerabilities

Fixes:
- SQL injection in user search (CVE-2025-1234)
- Open redirect / SSRF (SSRF-001)

Changes:
- Use parameterized queries for all database access
- Add URL validation (allowlist) for redirects
- Add SSRF protection module
- Add 8 security-specific tests

Testing:
- 8 new security tests
- All 135 tests passing
- Security scans: All clean
- npm audit: 0 vulnerabilities

See docs/security/hardening-<sprint-date>.md for full details."

git push origin security/hardening-sprint-<date>
```

### 10. Security Review
Security team verifies:
- [ ] Vulnerabilities correctly fixed
- [ ] Security tests comprehensive
- [ ] No new vulnerabilities introduced
- [ ] Scanning tools configured
- [ ] CI gates in place
- [ ] Documentation complete

### 11. Merge & Deploy
```bash
git checkout main
git pull
git merge security/hardening-sprint-<date>
git push origin main
```

### 12. Post-Deployment Monitoring
Monitor for exploitation attempts:

```
[ ] Watch logs for SQL injection patterns
[ ] Monitor for SSRF attempts (requests to 169.254.x.x, 10.x.x.x, etc.)
[ ] Track security-related alerts
[ ] Verify no false positives in legitimate traffic
```

---

## Success Criteria

- [ ] All identified vulnerabilities fixed
- [ ] Security tests created and passing
- [ ] No new vulnerabilities introduced
- [ ] Security scans passing (npm audit, snyk, semgrep)
- [ ] CI security gates in place
- [ ] Documentation complete and detailed
- [ ] Code review approved (including security team)
- [ ] All tests passing (no regression)
- [ ] Deployed to production
- [ ] Post-deployment monitoring in place

---

## Security Scan Tools

| Tool | Purpose | Command |
|------|---------|---------|
| npm audit | Dependency vulnerabilities | `npm audit --audit-level moderate` |
| snyk | Dependency + code vulnerabilities | `npx snyk test` |
| semgrep | SAST (code patterns) | `npx semgrep --config "p/security-audit"` |
| trivy | Container scanning | `trivy image my-app:latest` |
| licensee | License compliance | `npx licensee --production` |
| detect-secrets | Secret detection | `npx detect-secrets scan` |
| OWASP ZAP | DAST (dynamic) | `zaproxy-cli quick-scan -u https://staging.com` |

---

## Related Skills & Workflows

- @secure-by-default (security hardening practices)
- @test-engineering-suite (security tests)
- @debuggable-by-default (security logging)
- @kaiza-mcp-ops (security-critical code changes)
- /pre-pr-review (comprehensive security review)
