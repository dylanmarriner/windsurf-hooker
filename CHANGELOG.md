# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- Planned feature placeholder

### Changed
- Documentation system reorganized

### Deprecated
- Nothing

### Removed
- Nothing

### Fixed
- Nothing

### Security
- Nothing

---

## [2.0.0] - 2025-02-01

### Added
- **Automatic Git Hook Installation** (`./init` script)
  - One-command setup process
  - Installs post-checkout and post-merge hooks automatically
  - Runs initial deployment on setup completion
  
- **Automatic Deployment on Git Operations**
  - post-checkout hook: Triggers on `git clone` and `git checkout`
  - post-merge hook: Triggers on `git pull` and `git merge`
  - No manual deployment commands needed after setup
  
- **Enhanced Error Handling**
  - Better error messages with context
  - Graceful failure modes
  - Detailed logging of each operation
  
- **Comprehensive Documentation**
  - README.md with multiple audience levels
  - ARCHITECTURE.md explaining system design
  - CONTRIBUTING.md with contribution guidelines
  - CODE_OF_CONDUCT.md establishing community standards
  - SECURITY.md with vulnerability disclosure policy
  - docs/ folder structure for role-based documentation
  
- **Deployment Verification**
  - verify_deployment() function checks success
  - File ownership and permission verification
  - Automatic error detection and reporting
  
- **Git Hook Templates**
  - .githooks/ directory for hook source files
  - Hooks copied to .git/hooks/ during init
  - Centralized hook management

### Changed
- **Breaking: Script Structure**
  - Major refactor of deploy.sh for clarity
  - Better function organization
  - More robust error handling
  - ⚠️ Scripts now require bash 4.0+ (was 3.2+)
  
- **Breaking: Configuration**
  - Moved to root-relative path detection
  - Works from any directory via git rev-parse
  - Removed absolute path assumptions
  
- **Improved Backup System**
  - Backup timestamps more granular (seconds precision)
  - Backup creation happens before every deployment
  - Clear backup location: same directory as original

### Deprecated
- ⚠️ Direct execution of deploy.sh (use ./init instead)
  - Note: Direct execution still works for advanced users
  - Will be removed in v3.0.0
  - Use ./init for recommended setup

### Removed
- Nothing (backward compatible except noted breaking changes)

### Fixed
- **Permission Issues on CentOS/RHEL**
  - Fixed hardcoded /usr/bin/bash (now uses #!/bin/bash)
  - Improved permission setting on strict systems
  - Added explicit chmod after all cp operations
  
- **Error Handling**
  - Better detection of failed deployments
  - Clear error messages instead of silent failures
  - Automatic backup restoration on errors (future version)

### Security
- Added SECURITY.md with vulnerability disclosure policy
- Implemented root-only execution checks
- Added backup permission verification
- Documented threat model and mitigations

---

## [1.0.0] - 2024-12-15

### Added
- Initial release
- Basic deployment script (deploy.sh)
  - Copies windsurf-hooks to /usr/local/share/windsurf-hooks
  - Copies windsurf-hooks to /root/.codeium/hooks
  - Copies windsurf config to /etc/windsurf
  - Sets permissions (755 for dirs, 644 for files)
  - Creates timestamped backups
  
- Basic README with usage instructions
- LICENSE file (Apache 2.0)
- .gitignore with common exclusions

### Security
- Initial security considerations documented
- Backup mechanism implemented

---

## Migration Guides

### Upgrading from 1.0.0 to 2.0.0

**What changed:**
- Automatic deployment on git operations (NEW)
- Better error handling and logging (IMPROVED)
- Comprehensive documentation (NEW)

**How to upgrade:**

```bash
# 1. Pull latest code
git pull origin main

# 2. Run initialization (installs git hooks)
./init

# 3. Verify hooks installed
ls -la .git/hooks/post-checkout
ls -la .git/hooks/post-merge

# 4. All set! Future git operations auto-deploy
```

**Important notes:**
- You only need to run `./init` once
- Old deployments (from 1.0.0) still work fine
- No breaking changes to deployment destinations
- Backups from 1.0.0 remain intact

**Rollback (if needed):**
```bash
# Git hooks are in .git/ (not tracked in repo)
# To remove hooks:
rm .git/hooks/post-checkout
rm .git/hooks/post-merge

# Then use old deploy method:
sudo /path/to/deploy.sh
```

---

## Version History Summary

| Version | Release Date | Key Feature | Status |
|---------|--------------|------------|--------|
| 2.0.0 | 2025-02-01 | Automatic git hooks | Current |
| 1.0.0 | 2024-12-15 | Initial release | Supported |

---

## Semantic Versioning Explanation

**Format:** MAJOR.MINOR.PATCH

- **MAJOR (2.0.0):** Breaking changes (require action to upgrade)
- **MINOR (2.1.0):** New features (backward compatible)
- **PATCH (2.0.1):** Bug fixes (fully compatible)

**Examples:**
- 2.0.0 → 2.1.0: Safe upgrade (new features)
- 2.0.0 → 2.0.1: Safe upgrade (bug fixes only)
- 1.0.0 → 2.0.0: Requires review (breaking changes)

---

## Release Process

### For End Users

**New version released when:**
- Critical bug fixed (patch release)
- New features added (minor release)
- Breaking changes made (major release)

**How to update:**
```bash
git pull origin main
./init  # Re-runs, safe to run multiple times
```

### For Maintainers

**Release checklist:**
- [ ] All tests passing
- [ ] Code reviewed and approved
- [ ] CHANGELOG.md updated
- [ ] Version number updated (version.txt)
- [ ] Tagged on GitHub (v2.0.0)
- [ ] Release notes published
- [ ] Announcement sent to subscribers

---

## Planned Features (Roadmap)

### Version 2.1.0 (Q2 2025)
- [ ] Ansible playbook for multi-system deployment
- [ ] Docker container example
- [ ] GitHub Actions workflow template

### Version 2.2.0 (Q3 2025)
- [ ] Kubernetes manifest examples
- [ ] Monitoring integration (Prometheus)
- [ ] Health check endpoint

### Version 3.0.0 (Q4 2025)
- [ ] Remove direct deploy.sh execution (init only)
- [ ] Add policy-based deployment
- [ ] Support custom deployment destinations
- [ ] Remove 1.x backward compatibility

---

## Support Timeline

| Version | Release | End of Support | Status |
|---------|---------|----------------|--------|
| 2.0.0 | 2025-02-01 | 2026-02-01 | Current |
| 1.0.0 | 2024-12-15 | 2025-06-15 | Maintenance |

- **Current:** Receives features, bug fixes, security patches
- **Maintenance:** Security patches only
- **End of Life:** No support

---

## Known Issues

### Version 2.0.0

| Issue | Severity | Workaround | Fixed In |
|-------|----------|-----------|----------|
| None reported | - | - | - |

---

## Credits

### Contributors

- **Initial development:** Engineering team
- **Documentation:** Technical writing team
- **Community feedback:** All contributors and users

### Acknowledgments

Thank you to everyone who has:
- Reported bugs
- Suggested improvements
- Tested releases
- Contributed code or documentation
- Helped make this project better

---

## Questions About Versions?

- **Confused about a version?** See [GLOSSARY.md](docs/GLOSSARY.md)
- **Want a specific feature?** Open a feature request on GitHub
- **Found a bug?** See [SECURITY.md](SECURITY.md) or open an issue
- **Upgrading?** See migration guide above or [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last updated:** 2025-02-01  
**Maintained by:** Engineering Team  
**Format:** Keep a Changelog v1.1.0
