# Contributing to windsurf-hooker

Thank you for your interest in improving this project. This document explains how to contribute effectively, whether you're fixing bugs, adding features, improving documentation, or anything else.

---

## Table of Contents

- [Types of Contributions](#types-of-contributions)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Code Standards](#code-standards)
- [Pull Request Process](#pull-request-process)
- [Code Review Guidelines](#code-review-guidelines)
- [Questions & Support](#questions--support)

---

## Types of Contributions

### Bug Reports
Found something broken? Help us fix it.

**What makes a good bug report:**
- Clear description of what's broken
- Steps to reproduce the issue
- What you expected to happen vs. what actually happened
- Your environment (OS, shell version, Windsurf version)
- Error messages (paste exactly)

**Example:**
```
Title: deploy.sh fails on Ubuntu with permission error

Description:
When I run ./init on Ubuntu 22.04, the deployment fails.

Steps to reproduce:
1. Clone repository
2. Run ./init
3. See error: "Permission denied: cannot create /etc/windsurf"

Expected: Files deployed to /etc/windsurf
Actual: Error and no files deployed

Environment:
- OS: Ubuntu 22.04
- Shell: bash 5.1
- User: non-root (tried with sudo)
- Error: "[ERROR] Cannot create directory /etc/windsurf"
```

### Feature Requests
Have an idea for improvement? We'd love to hear it.

**What makes a good feature request:**
- Clear problem statement (what problem does this solve?)
- Proposed solution (how should it work?)
- Alternative approaches you considered
- Real-world use cases

**Example:**
```
Title: Support custom deployment paths

Description:
Currently, deployment paths are hardcoded. In enterprise 
environments, /etc might be read-only. Support for custom paths 
would enable deployment to /opt/windsurf instead.

Use case:
Company has read-only /etc on managed systems. Need to deploy 
to /opt/windsurf and set environment variable WINDSURF_CONFIG_PATH.

Proposed solution:
- Add .env file for deployment paths
- Use environment variables at deployment time
- Document custom path configuration

This would enable [enterprise use case].
```

### Documentation Improvements
Found confusing instructions? Want to add examples? Help us improve.

**Types of documentation contributions:**
- Clarifying existing docs
- Adding examples or use cases
- Fixing typos or grammar
- Adding missing sections
- Improving organization

### Code Improvements
See inefficiencies or bugs in the code? Fix them.

**Types of code contributions:**
- Bug fixes (non-breaking)
- Performance optimizations
- Refactoring for clarity
- Adding error handling
- Shell script improvements

### Integration Examples
Have you deployed this in a unique way? Share it.

**Share your knowledge:**
- CI/CD integration examples
- Ansible playbook
- Docker container
- Kubernetes manifest
- Monitoring integration

---

## Getting Started

### Prerequisites

- Linux machine (Ubuntu, CentOS, Debian, etc.)
- Git installed and configured
- Bash shell
- Text editor (VS Code, vim, nano, etc.)
- GitHub account (to open issues and PRs)

### First Time Contributor?

1. **Find an issue to work on**
   - Look for issues labeled `good-first-issue` or `help-wanted`
   - These are specifically chosen to be approachable
   - Read the issue to understand what's needed

2. **Claim the issue** (optional)
   - Comment: "I'd like to work on this"
   - Maintainers will assign it to you
   - Prevents duplicate effort

3. **Follow the development setup** (below)

4. **Make your changes** with clear commit messages

5. **Open a pull request** describing your work

---

## Development Setup

### Clone the Repository

```bash
# Clone to your local machine
git clone https://github.com/your-org/windsurf-hooker.git
cd windsurf-hooker

# Verify you're in the right place
pwd     # Should end with: windsurf-hooker
ls -la  # Should show: README.md, deploy.sh, init, etc.
```

### Initialize Development Environment

```bash
# Run the init script (sets up git hooks for your local copy)
./init

# This installs git hooks and runs initial deployment
# (Safe to run multiple times)
```

### Create a Feature Branch

```bash
# Update main branch
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/your-feature-name

# Use descriptive names:
# - feature/add-email-notifications
# - fix/permission-error-on-ubuntu
# - docs/clarify-deployment-steps
# - test/add-rollback-tests
```

### Development Tools (Optional)

```bash
# Install ShellCheck (for bash linting)
sudo apt-get install shellcheck

# Install shfmt (for bash formatting)
sudo apt-get install shfmt

# Run linter on your changes
shellcheck deploy.sh

# Format your bash code
shfmt -i 2 -w deploy.sh
```

---

## Making Changes

### Code Style Guidelines

#### Bash Scripts

**Variable Naming:**
```bash
# Good - descriptive and UPPERCASE for constants
WINDSURF_HOOKS_SRC="${REPO_DIR}/windsurf-hooks"
DESTINATION_PATH="/etc/windsurf"
BACKUP_RETENTION_DAYS=30

# Bad - unclear abbreviations
WH_SRC="/path"
DEST="/etc/windsurf"
RET=30
```

**Function Naming:**
```bash
# Good - verb_noun format, descriptive
backup_existing_installation() { }
verify_deployment_success() { }
check_root_privileges() { }

# Bad - unclear what it does
do_stuff() { }
run_deploy() { }
verify() { }
```

**Comments:**
```bash
# Good - explains WHY, not WHAT
# Create backup before overwriting (safety: allow recovery)
backup_existing "$dest"

# Bad - obvious comment
# Create a backup
mkdir -p "$backup_dir"

# Good - document assumptions
# Assumes /etc/windsurf is writable by root (standard Linux)
# Will fail gracefully if directory is read-only
```

**Error Handling:**
```bash
# Good - explicit error handling
if ! cp -r "$src" "$dest"; then
    log_error "Failed to copy: $src → $dest"
    return 1
fi

# Good - verify results
if [[ ! -d "$dest" ]]; then
    log_error "Destination directory missing: $dest"
    return 1
fi

# Bad - silent failure
cp -r "$src" "$dest"  # What if this fails?
```

**Function Structure:**
```bash
my_function() {
    # 1. Input validation
    local param="$1"
    if [[ -z "$param" ]]; then
        log_error "Parameter required"
        return 1
    fi
    
    # 2. Logging
    log_info "Starting operation..."
    
    # 3. Main logic
    # (clear, step-by-step)
    
    # 4. Verification
    if [[ ! -f "$result_file" ]]; then
        log_error "Operation did not produce expected result"
        return 1
    fi
    
    # 5. Logging success
    log_info "Operation completed successfully"
    return 0
}
```

#### Python Scripts

```python
# Good - docstring explains purpose and parameters
def validate_hook_permissions(hook_path: str) -> bool:
    """
    Validate that hook has correct execute permissions.
    
    Args:
        hook_path: Full path to hook file
        
    Returns:
        True if permissions are correct, False otherwise
    """
    pass

# Good - type hints
def deploy_configuration(src: str, dest: str, owner: str = "root") -> bool:
    """Deploy configuration files with proper ownership."""
    pass

# Bad - unclear
def check(f):
    """Check file."""
    pass
```

### Commit Messages

**Format:**
```
[Type] Brief description (50 chars max)

Longer explanation if needed (wrap at 72 chars).
Explain WHAT changed and WHY, not just HOW.

References: #123 (issue number)
```

**Types:**
- `[fix]` - Bug fix
- `[feature]` - New capability
- `[docs]` - Documentation
- `[refactor]` - Code improvement
- `[test]` - Testing

**Examples:**

```
[fix] Resolve permission errors on CentOS

On CentOS, /etc/windsurf defaults to 0700. This prevented
Windsurf from reading configuration. Changed permission 
logic to explicitly set 0755 on all directories.

Fixes: #42
```

```
[docs] Add troubleshooting section to README

Added common errors and solutions to help users self-serve
before opening issues.
```

```
[test] Add rollback integration test

New test verifies rollback from corrupted deployment restores
previous known-good state.
```

---

## Testing

### Run Existing Tests

```bash
# Run all unit tests
for test in tests/unit/*.sh; do
    bash "$test" || echo "Failed: $test"
done

# Run all integration tests
./tests/integration/deployment.integration.sh

# Run full test suite
./tests/run-all.sh
```

### Create Tests for Your Changes

#### Unit Test Example

```bash
# File: tests/unit/test-custom-feature.sh
#!/bin/bash

# Test: Feature works in normal case
test_custom_feature_success() {
    # Setup
    local temp_dir=$(mktemp -d)
    
    # Execute
    my_custom_function "$temp_dir"
    
    # Verify
    if [[ -f "$temp_dir/expected_file" ]]; then
        echo "PASS: File created"
        rm -rf "$temp_dir"
        return 0
    else
        echo "FAIL: File not created"
        rm -rf "$temp_dir"
        return 1
    fi
}

test_custom_feature_error_handling() {
    # Setup with bad input
    
    # Execute
    my_custom_function "/nonexistent/path"
    
    # Verify it failed gracefully
    if [[ $? -ne 0 ]]; then
        echo "PASS: Error handled correctly"
        return 0
    else
        echo "FAIL: Should have failed"
        return 1
    fi
}

# Run tests
test_custom_feature_success || exit 1
test_custom_feature_error_handling || exit 1
```

#### Integration Test Example

```bash
# File: tests/integration/test-custom-feature.integration.sh
#!/bin/bash

# Full deployment flow with new feature
test_deployment_with_feature() {
    # Setup temporary environment
    TEMP_ROOT=$(mktemp -d)
    export WINDSURF_DEST="$TEMP_ROOT/etc/windsurf"
    
    # Deploy
    ./deploy.sh
    
    # Verify new feature worked
    if [[ -f "$WINDSURF_DEST/new_config" ]]; then
        echo "PASS: Feature deployed correctly"
    else
        echo "FAIL: Feature not deployed"
        return 1
    fi
    
    # Cleanup
    rm -rf "$TEMP_ROOT"
}

test_deployment_with_feature || exit 1
```

### Testing Checklist

Before opening a pull request, verify:

- [ ] Feature/fix works as intended
- [ ] Existing tests still pass
- [ ] New functionality has tests
- [ ] Error cases handled (bad input, missing files, etc.)
- [ ] Tested on your system
- [ ] Code follows style guidelines
- [ ] Commit messages are clear
- [ ] No unrelated changes included

---

## Submitting Changes

### Before Opening a Pull Request

1. **Update your branch with latest main:**
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. **Run tests:**
   ```bash
   ./tests/run-all.sh
   ```

3. **Lint your code (if Bash):**
   ```bash
   shellcheck deploy.sh
   ```

4. **Review your own changes:**
   ```bash
   git diff origin/main
   ```

5. **Push your branch:**
   ```bash
   git push origin feature/your-feature-name
   ```

### Open a Pull Request

GitHub will suggest opening a PR. Click "Create Pull Request."

**Fill in the PR template:**

```markdown
## Description
Brief summary of what this PR does.

## Problem It Solves
What issue does this fix? What capability does it add?

## Changes Made
- Change 1
- Change 2
- Change 3

## How to Test
Step-by-step instructions for reviewers to verify:
1. Check out this branch
2. Run tests: `./tests/run-all.sh`
3. Verify deployment works: `sudo ./deploy.sh`
4. Check files exist: `ls /etc/windsurf`

## Type of Change
- [ ] Bug fix (non-breaking change)
- [ ] New feature (non-breaking change)
- [ ] Breaking change
- [ ] Documentation update

## Related Issues
Fixes #123 or Relates to #456

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] No unrelated changes
- [ ] Commit messages are clear
```

---

## Code Review Guidelines

### What Happens Next

1. **Automated Checks Run**
   - Tests execute automatically
   - Linters check code style
   - Security scanners run
   - All must pass to proceed

2. **Maintainer Reviews**
   - Code review for quality
   - Architecture review for design
   - Security review for vulnerabilities
   - Documentation review for clarity

3. **Feedback & Iteration**
   - Reviewer requests changes (if needed)
   - You update your PR
   - Reviewer re-checks
   - Repeat until approved

4. **Merge**
   - PR approved by reviewers
   - All checks passing
   - Squashed and merged to main
   - Branch deleted

### Responding to Review Feedback

**When you receive feedback:**

1. **Assume good intent** — Reviewer wants to help
2. **Ask questions** if feedback is unclear
3. **Explain your approach** if you disagree
4. **Make changes** if feedback is valid
5. **Push updates** to your branch
6. **Mention** reviewer: "Done, ready for re-review"

**Example feedback interaction:**

```
Reviewer: "This error message is unclear. What does 'invalid config' mean?"

You: "Good point. Changed to: 'Config file missing required field: 
description'. Should be clearer now."

[You push changes]

You: "@reviewer1 Updated error message. Ready for re-review."

Reviewer: "Great, looks good! Approving."
```

### Approval Requirements

| Change Type | Approvals Needed | Typical Timeline |
|-------------|-----------------|-----------------|
| Bug fix | 1 reviewer | 48 hours |
| Feature | 2 reviewers | 1 week |
| Architecture change | 2 + maintainer | 2 weeks |
| Security update | Security reviewer | 24 hours |

---

## Questions & Support

### Where to Ask Questions

**Development Questions:**
- GitHub Discussions: [link]
- Open an issue: [link]
- Slack/Discord: [link]

**PR Review Questions:**
- Comment on the PR
- Mention reviewer: `@reviewer-name`
- Ask in Discussions

**Security Questions:**
- Email: security@project.org
- Do NOT open public issues
- See [SECURITY.md](SECURITY.md)

### Getting Help

**Stuck on something?**
1. Check [docs/contributor-guide/](docs/contributor-guide/)
2. Read existing issues for similar problems
3. Ask in Discussions (others may have same question)
4. Email maintainers: maintainers@project.org

**Need a maintainer's attention?**
- Mention them in a PR: `@maintainer-name`
- Email (if urgent): maintainers@project.org
- Expected response: 48 hours

---

## Code of Conduct

By contributing, you agree to our [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

In short:
- Be respectful and inclusive
- No harassment or discrimination
- Welcome people of all backgrounds
- Focus on the work, not the person
- If you see a problem, report it

---

## Attribution

Contributors will be recognized in:
- [CHANGELOG.md](CHANGELOG.md) (by PR)
- GitHub contributors graph
- Project website (if applicable)

Thank you for making windsurf-hooker better!

---

**Questions?** Open an issue or reach out to maintainers@project.org
