# Security Policy

This document describes how to responsibly report security vulnerabilities and our security practices.

---

## Reporting Security Issues

### Do NOT

❌ Open a public GitHub issue  
❌ Post in discussions or forums  
❌ Share vulnerability details publicly  
❌ Wait to report (do it immediately)  

### Do

✅ Email security@project.org  
✅ Include full technical details  
✅ Give us reasonable time to fix  
✅ Follow this policy  

---

## Vulnerability Disclosure Process

### Step 1: Report (You)

**Email:** security@project.org

**Include:**
```
Subject: [SECURITY] Vulnerability Report - [Brief Title]

Body:
1. Type of vulnerability (RCE, auth bypass, data leak, etc.)
2. Affected component (deploy.sh, hook X, config Y, etc.)
3. Affected versions (v1.0, v2.0, all versions, etc.)
4. CVSS score estimate if possible
5. Proof of concept (steps to reproduce)
6. Impact assessment (who is affected, what can attacker do)
7. Recommended fix (if you have one)
8. Your contact information (for coordinated disclosure)
```

**Example:**

```
Subject: [SECURITY] Arbitrary File Write in deploy.sh

Body:
Type: Arbitrary File Write / Local Privilege Escalation
Component: deploy.sh (line 45)
Versions: All versions up to v2.0
CVSS Score: 7.8 (High)

Proof of Concept:
When deploy.sh backs up existing files, the backup path is 
constructed from user input without validation. By creating 
a symlink at /etc/windsurf, an attacker can write to any 
file writable by root.

Steps:
1. ln -s /etc/shadow /etc/windsurf
2. sudo ./deploy.sh
3. Deploy script backs up /etc/shadow to /etc/windsurf.backup.*
4. Attacker can modify /etc/shadow via symlink

Impact:
Local privilege escalation - attacker with sudo access can 
modify system files and gain root access.

Recommended Fix:
Use readlink -f to resolve symlinks before backing up.
Validate destination is regular file or directory, not symlink.

Contact: reporter@example.com (PGP key: [key])
Timeline: Immediate
```

### Step 2: Response (Us)

**Within 24 hours:**
- ✅ Acknowledge receipt of report
- ✅ Confirm we're investigating
- ✅ Provide security contact's name
- ✅ Initial severity assessment

**Within 48 hours:**
- ✅ Share preliminary findings
- ✅ Confirm we can reproduce (or ask for clarification)
- ✅ Provide timeline for fix

**Example response:**

```
Thank you for the security report. We take this seriously.

We have confirmed the vulnerability in deploy.sh line 45.
The symlink traversal issue could allow local escalation.

We are preparing a patch. Target timeline:
- Patch prepared: 2 days
- Security review: 1 day
- Release: 4 days
- Public disclosure: 7 days after release

We will keep you updated.
```

### Step 3: Coordinate Fix

**During fix development:**
- We fix the vulnerability
- We prepare tests to prevent regression
- We prepare security advisory
- We create patched release

**We may ask you:**
- ✅ To test the patch
- ✅ For additional clarification
- ✅ Permission to credit you publicly

### Step 4: Release & Disclosure

**What happens:**
1. Security patch released (not in normal release cycle)
2. Users encouraged to update immediately
3. Security advisory published
4. Vulnerability disclosed publicly (30+ days after patch release)

**Public disclosure includes:**
- Vulnerability description
- Affected versions
- Severity/CVSS score
- Impact
- Mitigation steps
- Credit to reporter (with permission)

**Example advisory:**

```
## Security Advisory: Symlink Traversal in deploy.sh

Severity: HIGH (CVSS 7.8)
Affects: windsurf-hooker versions < 2.0.1
Fixed: windsurf-hooker 2.0.1 released [date]

### Description
deploy.sh did not validate backup destinations, allowing 
symlink-based write attacks.

### Impact
Local attacker with sudo could write arbitrary files as root.

### Mitigation
Upgrade to 2.0.1 or later immediately.

### Credits
Thanks to [Reporter Name] for responsible disclosure.
```

---

## Response Timeline

| Severity | Acknowledgment | Fix Target | Public Disclosure |
|----------|----------------|------------|-------------------|
| Critical | 4 hours | 24-48 hours | 30 days after patch |
| High | 24 hours | 3-5 days | 30 days after patch |
| Medium | 48 hours | 1-2 weeks | 30 days after patch |
| Low | 1 week | 1-2 months | 30 days after patch |

**Our commitments:**
- ✅ We will respond to every report
- ✅ We will provide status updates at least weekly
- ✅ We will not publicly disclose before patch is released
- ✅ We will credit the reporter (if desired)
- ✅ We will prioritize critical vulnerabilities

---

## Security Practices

### Code Review

- All changes reviewed before merge
- Security-critical code reviewed by security-aware maintainer
- Third-party security audits (periodically)

### Dependency Management

- Minimal dependencies (keep it simple)
- Dependencies pinned to specific versions
- Automated security scanning (GitHub Dependabot)
- Regular updates and patches

### Access Control

```
Repository Access:
├─ Maintainers: Can merge to main
├─ Contributors: Can submit PRs
└─ Public: Can read and clone

Deployment Access:
├─ Root only: Can run deploy.sh
├─ Sudo: Via sudo (logged)
└─ Non-root: Cannot modify system directories
```

### Audit Trail

```
Every deployment logged:
├─ Git commits (immutable history)
├─ Sudo execution (syslog)
├─ Backup creation (timestamped)
├─ Deployment logs (script output)
└─ File ownership (chown logged)
```

### Secure Defaults

```
File Permissions:
├─ Directories: 755 (world-readable, root-writable)
├─ Config: 644 (world-readable)
├─ Scripts: 755 (executable)
└─ Ownership: root:root (root-only modification)

No Secrets in Repository:
├─ Private keys: ❌ Never committed
├─ Credentials: ❌ Never committed
├─ API keys: ❌ Never committed
└─ Passwords: ❌ Never committed
```

---

## Known Security Limitations

### By Design

**1. Root Access Required**
- Deployment requires sudo (by design)
- Prevents non-admin modifications
- Trade-off: Requires trust in administrative users

**2. System Directory Modification**
- Modifies /etc/ and /usr/local/
- Standard practice but requires admin access
- Can be mitigated with custom deployment paths

**3. Backup Disk Space**
- Backups accumulate without automatic cleanup
- Could fill disk if not managed
- Mitigation: Cron job to clean old backups

### Recommendations

**For Production Use:**

1. **Access Control**
   - Restrict sudo access to windsurf-deployer group
   - Monitor sudo usage: `sudo journalctl -u sudo`
   - Use SSH key-based authentication

2. **Network Isolation**
   - Restrict who can git push to main
   - Use GitHub branch protection rules
   - Require code review before deployment

3. **Monitoring**
   - Monitor /etc/windsurf for unauthorized changes
   - Set up file integrity monitoring (aide, tripwire)
   - Alert on unexpected deployments

4. **Backup Management**
   - Set up automated cleanup (30-day retention)
   - Backup backups to external storage
   - Test restore procedures regularly

5. **Incident Response**
   - Document escalation procedures
   - Train team on incident response
   - Test disaster recovery regularly

---

## Third-Party Security

### Dependencies

This project has minimal dependencies:

| Dependency | Purpose | Status |
|-----------|---------|--------|
| GNU bash | Shell scripting | Built-in OS |
| GNU coreutils | File operations (cp, chmod, etc.) | Built-in OS |
| Python 3 | Hook scripting (optional) | Standard OS |

**All are OS-standard components.**

### GitHub Security

- Repository is private (for enterprise) or public (for open-source)
- Branch protection requires code review
- Dependabot scans for vulnerable dependencies
- Secret scanning prevents credential leaks

---

## Compliance

### Standards Alignment

This project implements controls aligned with:

**SOC 2 Type II:**
- ✅ Change management (CC6.1)
- ✅ Access control (CC6.2)
- ✅ System monitoring (CC7.2)

**ISO 27001:**
- ✅ Access control (A.9)
- ✅ Change management (A.12.1.2)
- ✅ Incident management (A.16)

**GDPR:**
- ✅ Data minimization (no personal data stored)
- ✅ Integrity (backups and versioning)
- ✅ Confidentiality (access control)

---

## Security Contacts

**Report a vulnerability:**
- Email: security@project.org (preferred)
- GPG key: [Link to public key, if available]

**General security questions:**
- Email: security@project.org

**Non-security issues:**
- GitHub Issues: [link]

---

## Security Advisories

Subscribe to security advisories:
- GitHub: Watch "Releases" in this repository
- Mailing list: [Subscribe link]
- RSS: [Feed URL]

**Latest advisories:** [Link to GitHub Releases]

---

## Responsible Disclosure Philosophy

We believe in:

1. **Open Communication** — We tell users the truth about vulnerabilities
2. **Reasonable Timeline** — We give ourselves time to fix properly
3. **Credit & Appreciation** — We thank researchers who help
4. **Root Cause Prevention** — We fix not just the bug, but why it happened
5. **Transparency** — We explain what happened and how we prevent it

**We do NOT:**
- ❌ Minimize reported vulnerabilities
- ❌ Blame researchers for finding issues
- ❌ Delay disclosures unreasonably
- ❌ Retaliate against reporters
- ❌ Ignore legitimate security concerns

---

## Security Incident History

| Date | Vulnerability | Severity | Status |
|------|---|---|---|
| [None reported] | - | - | - |

*(No security incidents reported yet. This is a good sign!)*

---

## Security Roadmap

**Short term (Q1):**
- [ ] Security audit of deploy.sh
- [ ] Symlink validation in backup logic
- [ ] Secrets scanning in CI/CD

**Medium term (Q2):**
- [ ] Third-party security assessment
- [ ] Multi-system deployment hardening
- [ ] Automated compliance scanning

**Long term (Q3+):**
- [ ] Bug bounty program (if applicable)
- [ ] Enhanced monitoring integration
- [ ] Policy enforcement mechanisms

---

## Questions?

Email: security@project.org

Thank you for helping keep windsurf-hooker secure.
