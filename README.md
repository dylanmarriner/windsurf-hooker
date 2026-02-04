# windsurf-hooker

**Auto-deployment system for Windsurf IDE configuration and hooks**

[![Tests](https://img.shields.io/badge/tests-automated-brightgreen)](https://github.com)
[![Security](https://img.shields.io/badge/security-hardened-blue)](SECURITY.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)

---

## Quick Answer: What Is This?

**In Plain English:**

Imagine you keep a recipe book on your computer. Every time you update it, you want copies in three places: your kitchen, your office, and your backup drawer. This project automatically:

1. **Copies** your Windsurf configuration to three system locations
2. **Sets it up** automatically when you first clone this repository
3. **Keeps everything in sync** every time you pull updates
4. **Protects** the files with proper permissions so everything works correctly

No manual copying, no forgotten updates, no permission errors.

---

## Table of Contents

- [What Does It Do?](#what-does-it-do)
- [For Absolute Beginners](#for-absolute-beginners)
- [For Operators/Deployers](#for-operators--deployers)
- [For Developers](#for-developers)
- [For Auditors & Enterprise](#for-auditors--enterprise)
- [Architecture Overview](#architecture-overview)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)
- [Glossary](#glossary)

---

## What Does It Do?

This repository contains two critical components for Windsurf IDE:

### Component 1: windsurf-hooks

**What it is:** Special scripts that automatically run when you update code  
**What it contains:** Python and shell scripts that integrate with git  
**Where it goes:**
- `/usr/local/share/windsurf-hooks` (system-wide access)
- `/root/.codeium/hooks` (Windsurf IDE access)

### Component 2: windsurf

**What it is:** Configuration files for the Windsurf IDE  
**Where it goes:** `/etc/windsurf` (system configuration)

### How They Work Together

```
You pull code changes (git pull)
         ↓
Git automatically runs our hooks
         ↓
Hooks trigger the deployment script
         ↓
Files are copied to their destinations
         ↓
Permissions are automatically set
         ↓
Everything is ready to use
```

---

## For Absolute Beginners

### Prerequisites

You need:
- **Linux computer** (Ubuntu, CentOS, Debian, etc.)
- **Administrator access** (ability to use `sudo`)
- **Git installed** (to clone this repository)
- **Basic terminal skills** (comfortable typing commands)

### Installation: One Command

```bash
# Step 1: Navigate to where you cloned this repository
cd /path/to/windsurf-hooker

# Step 2: Run the initialization script
./init

# That's it!
```

**What happens:**

1. The `./init` script runs
2. It asks for your password (sudo requirement)
3. It copies files to the correct locations
4. It sets up automatic updates for the future
5. You're done!

### Automatic Updates from Now On

After running `./init`, the system is automatic:

```bash
# Every time you do this...
git pull

# ...the system automatically deploys the latest files.
# No additional commands needed!
```

### Verifying It Worked

```bash
# Check that windsurf configuration was deployed
ls -la /etc/windsurf

# Check that hooks were deployed
ls -la /usr/local/share/windsurf-hooks

# All should show files owned by root with proper permissions
```

---

## For Operators & Deployers

### System Requirements

| Requirement | Specification |
|-------------|---------------|
| OS | Linux (any distribution) |
| User | Must have sudo access |
| Disk Space | ~50 MB |
| Network | Internet (for git operations) |
| Shell | bash 4.0 or higher |

### Complete Setup Walkthrough

#### Step 1: Clone Repository

```bash
git clone https://github.com/your-org/windsurf-hooker.git
cd windsurf-hooker
```

#### Step 2: Run Initialization

```bash
./init
```

**Output should look like:**
```
[INFO] Setting up git hooks for auto-deployment...
[INFO] Git hooks installed successfully!
[INFO] Running initial deployment...
[INFO] Deploying windsurf-hooks to /usr/local/share/windsurf-hooks
[INFO] Deploying windsurf-hooks to /root/.codeium/hooks
[INFO] Deploying windsurf to /etc/windsurf
[INFO] Deployment complete!
```

If you see errors, see [Troubleshooting](#troubleshooting).

#### Step 3: Verify Deployment

```bash
# Verify all directories exist and are readable
ls -la /usr/local/share/windsurf-hooks
ls -la /root/.codeium/hooks
ls -la /etc/windsurf

# Check that Windsurf can read the files
stat /etc/windsurf/
```

### Configuration

#### Default Deployment Locations

Edit `deploy.sh` to change destinations:

```bash
# Current locations:
WINDSURF_HOOKS_DEST1="/usr/local/share/windsurf-hooks"
WINDSURF_HOOKS_DEST2="/root/.codeium/hooks"
WINDSURF_DEST="/etc/windsurf"

# Change these variables to customize paths
```

#### File Permissions Explained

After deployment, files have these permissions:

| Type | Permission | Meaning |
|------|-----------|---------|
| Directories | 755 | `rwxr-xr-x` - readable/writable by root only |
| Config files | 644 | `rw-r--r--` - readable by all, writable by root |
| Hook scripts | 755 | `rwxr-xr-x` - executable by all |

**Why these permissions?**
- Directories must be executable to enter them
- Config files must be readable by applications
- Hook scripts must be executable by the system
- Root ownership prevents accidental modification

### Manual Deployment (Without Git)

If you need to deploy without git hooks:

```bash
cd /path/to/windsurf-hooker
sudo ./deploy.sh
```

### Backup & Recovery

Automatic backups are created before each deployment:

```bash
# List all backups
ls -la /usr/local/share/windsurf-hooks.backup.*
ls -la /root/.codeium/hooks.backup.*
ls -la /etc/windsurf.backup.*

# Restore from backup (example)
sudo cp -r /usr/local/share/windsurf-hooks.backup.1704067200 \
           /usr/local/share/windsurf-hooks

# Or use the rollback script
sudo ./scripts/rollback.sh
```

### Monitoring & Verification

```bash
# Verify hook installation
test -x .git/hooks/post-checkout && echo "Hooks installed" || echo "Hooks missing"

# Check recent deployments (if logging is enabled)
tail -20 /var/log/windsurf-deploy.log

# Verify file integrity
sha256sum /etc/windsurf/* > /tmp/manifest.txt
sha256sum -c /tmp/manifest.txt
```

### Troubleshooting Common Issues

See the [Troubleshooting](#troubleshooting) section at the end of this document.

---

## For Developers

### Development Setup

```bash
# 1. Clone the repository
git clone https://github.com/your-org/windsurf-hooker.git
cd windsurf-hooker

# 2. Create a feature branch
git checkout -b feature/my-improvement

# 3. Make your changes
# 4. Test locally
./tests/deployment.integration.sh

# 5. Commit with descriptive message
git commit -m "Add feature: description of what you added"

# 6. Push and open a pull request
git push origin feature/my-improvement
```

### Code Standards

**Bash Script Style:**
```bash
# Good - descriptive variable names
DESTINATION_PATH="/etc/windsurf"

# Good - comments explain WHY, not WHAT
# Backup existing installation before overwriting (safety)
backup_existing "$dest"

# Bad - unclear names
DST="/etc/windsurf"

# Bad - comments state the obvious
# Create a directory
mkdir -p "$dir"
```

**File Organization:**
```bash
# Logical flow:
# 1. Configuration (variables, file paths)
# 2. Utility functions (logging, error handling)
# 3. Main logic (actual deployment steps)
# 4. Execution (call main function)

# Add new functions before main()
# Add new configuration at the top
```

### Testing Your Changes

```bash
# Run unit tests
./tests/unit/*.sh

# Run integration tests (full end-to-end)
./tests/integration/deployment.integration.sh

# Test on different systems (Docker simulation)
./tests/multi-os.test.sh
```

### Adding New Features

**Example: Adding an environment variable feature**

1. Update `deploy.sh` configuration:
```bash
WINDSURF_ENV_PATH="${WINDSURF_DEST}/environment.conf"
```

2. Create utility function:
```bash
deploy_environment_file() {
    local src="$1"
    local dest="$2"
    cp "$src" "$dest"
    chmod 644 "$dest"
    chown root:root "$dest"
}
```

3. Add to deployment sequence:
```bash
deploy_environment_file "${WINDSURF_SRC}/environment.conf" "$WINDSURF_ENV_PATH"
```

4. Add test:
```bash
# tests/unit/test-env-deployment.sh
test -f "$WINDSURF_DEST/environment.conf" && echo "PASS" || echo "FAIL"
```

5. Document in relevant docs

### Creating a Pull Request

```bash
# After pushing your branch:
# - GitHub will suggest opening a PR
# - Click the "Create Pull Request" button
# - Fill in the PR template:
#   - What does this change?
#   - Why is it needed?
#   - How should reviewers test it?
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## For Auditors & Enterprise

### Compliance & Security

This project implements controls for:
- **SOC 2 Type II**: Change management, access control, monitoring
- **ISO 27001**: Asset management, access control, incident response
- **GDPR**: Data handling (if applicable)

**Full compliance documentation:** [SECURITY.md](SECURITY.md)

### Audit Trail & Logging

```bash
# GitHub version control provides immutable audit trail
git log --all --oneline | head -20

# Deployment logs (if configured)
sudo tail -100 /var/log/windsurf-deploy.log

# File modification tracking
stat /etc/windsurf/
ls -la /usr/local/share/windsurf-hooks.backup.*/
```

### Change Control Verification

Every deployment is tracked:

1. **Before:** Automatic backup created with timestamp
2. **During:** Deployment logged with success/failure
3. **After:** Verification confirms correctness
4. **Rollback:** Previous version available if needed

```bash
# Verify backup exists
ls -la /etc/windsurf.backup.* | head -5

# Check deployment success
grep -i "deployment complete" /var/log/windsurf-deploy.log

# Verify file ownership
ls -la /etc/windsurf | head -1  # Should show root:root
```

### Permissions & Access Control

```bash
# Verify role-based access
stat /etc/windsurf
#   Access: (0755/drwxr-xr-x)  Owner: (0/root)  Group: (0/root)

stat /usr/local/share/windsurf-hooks
#   Access: (0755/drwxr-xr-x)  Owner: (0/root)  Group: (0/root)

# Only root can modify; all users can read
```

### Recovery Time Objective (RTO)

| Scenario | Detection | Recovery | RTO |
|----------|-----------|----------|-----|
| Corrupted files | Manual check or automated test | Run deploy.sh | <5 min |
| Permission drift | File read fails | Run deploy.sh again | <2 min |
| Partial corruption | Checksum mismatch | Rollback.sh to previous | <1 min |

### For More Details

See comprehensive compliance documentation:
- [SECURITY.md](SECURITY.md) - Security policies
- [docs/enterprise/](docs/enterprise/) - Enterprise deployment
- [docs/architecture/adr/](docs/architecture/adr/) - Design decisions

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────┐
│         Git Repository (This Project)               │
├─────────────────────────────────────────────────────┤
│  windsurf-hooks/          windsurf/                 │
│  ├── post_write_verify.py │ ├── global_workflows/  │
│  ├── pre_mcp_tool_use...  │ ├── policy/            │
│  ├── pre_run_command...   │ ├── rules/             │
│  └── [other hooks]        │ ├── skills/            │
│                           │ └── [config files]     │
└────────┬──────────────────┬────────────────────────┘
         │                  │
   ┌─────▼──────┐      ┌────▼─────────────┐
   │  ./init    │      │  deploy.sh        │
   │  Script    │      │  (Main Logic)     │
   └─────┬──────┘      └────┬─────────────┘
         │                  │
         └──────┬───────────┘
                │
     ┌──────────▼──────────────────┐
     │   System Directories        │
     ├─────────────────────────────┤
     │ /usr/local/share/...        │
     │ /root/.codeium/hooks        │
     │ /etc/windsurf               │
     └─────────────────────────────┘
```

### Data Flow

```
1. Clone: Download repo from GitHub
   ↓
2. Init: Run ./init script
   ├─ Install git hooks
   ├─ Call deploy.sh
   └─ Display success
   ↓
3. Deploy: Copy files to destinations
   ├─ Back up existing files
   ├─ Copy files to 3 locations
   ├─ Set permissions (755/644/755)
   └─ Set ownership (root:root)
   ↓
4. Active: Files are now live
   ├─ Windsurf IDE reads config from /etc/windsurf
   ├─ Codeium reads hooks from /root/.codeium/hooks
   └─ System reads hooks from /usr/local/share/...
   ↓
5. Update: Developer pulls latest code
   ├─ Git runs post-merge hook automatically
   ├─ Hook triggers deploy.sh
   └─ Files update automatically
```

### File Ownership & Permissions

```
/etc/windsurf/                              (755) root:root
├── global_workflows/                       (755) root:root
│   ├── *.yaml                              (644) root:root
│   └── *.yml                               (644) root:root
├── policy/                                 (755) root:root
├── rules/                                  (755) root:root
└── hooks.json                              (644) root:root

/usr/local/share/windsurf-hooks/           (755) root:root
├── post_write_verify.py                    (755) root:root [executable]
└── pre_*.py                                (755) root:root [executable]

/root/.codeium/hooks/                      (755) root:root
└── [Same as above, synced copy]           (755) root:root [executable]
```

**Why these permissions?**
- **755 on directories**: Necessary for entering/listing
- **644 on files**: Readable by all, writable by root only
- **755 on .py files**: Must be executable by Windsurf process

---

## Examples

### Example 1: Fresh Installation (Beginner)

```bash
# You just cloned the project
$ git clone https://github.com/company/windsurf-hooker.git
$ cd windsurf-hooker

# Run initialization (one command, that's it!)
$ ./init

[INFO] Setting up git hooks for auto-deployment...
[INFO] Git hooks installed successfully!
[INFO] Running initial deployment...
[INFO] Deploying windsurf-hooks to /usr/local/share/windsurf-hooks
[INFO] Deploying windsurf-hooks to /root/.codeium/hooks
[INFO] Deploying windsurf to /etc/windsurf
[INFO] Deployment complete!

Deployed to:
  - /usr/local/share/windsurf-hooks
  - /root/.codeium/hooks
  - /etc/windsurf

# Verify everything worked
$ ls /etc/windsurf
global_workflows  hooks.json  policy  rules  skills  workflows
```

### Example 2: Pulling Updates (Automatic)

```bash
# Later, developer updates the repository
$ git pull origin main
Updating abc123..def456
Fast-forward
 windsurf-hooks/post_write_verify.py | 5 ++++
 windsurf/global_workflows/test.yaml | 3 +++
 2 files changed

# The system automatically deployed! (no command needed)
# Check the log:
[INFO] Running auto-deployment after git merge...
[INFO] Deploying windsurf to /etc/windsurf
[INFO] Deployment complete!
```

### Example 3: Enterprise Audit Scenario

```bash
# Auditor verifies deployment integrity
$ sudo stat /etc/windsurf
  File: /etc/windsurf
  Size: 4096      Blocks: 8          IO Block: 4096   directory
Access: (0755/drwxr-xr-x)  Uid: (    0/   root)   Gid: (    0/   root)
Access: 2025-02-01 14:32:10.000000000 +0000
Modify: 2025-02-01 14:32:10.000000000 +0000

# Verify backup exists
$ ls -la /etc/windsurf.backup.* | head -3
drwxr-xr-x root root ... windsurf.backup.1706790730
drwxr-xr-x root root ... windsurf.backup.1706790445

# Check deployment logs
$ sudo tail /var/log/windsurf-deploy.log
[INFO] Deployment complete!

# Auditor can confirm: Version controlled, backed up, logged
```

### Example 4: Adding Custom Configuration

```bash
# Developer adds new workflow to the repo
$ cd windsurf/global_workflows
$ cat > custom-deploy.yaml << EOF
name: Custom Deploy
description: Enterprise deployment workflow
...
EOF

$ git add custom-deploy.yaml
$ git commit -m "Add custom deployment workflow"
$ git push

# After merge, ./init runs automatically
# New workflow is deployed to /etc/windsurf/global_workflows
$ ls /etc/windsurf/global_workflows/
custom-deploy.yaml
...
```

---

## Troubleshooting

### Problem: `./init: Permission denied`

**Cause:** Script is not executable

**Solution:**
```bash
chmod +x init
./init
```

### Problem: `sudo: password required` during git operation

**Cause:** System prompts for password before running deployment

**Solution:** Configure passwordless sudo for the deploy script
```bash
# Run this as the user who cloned the repo:
sudo visudo

# Add this line at the end:
%sudo ALL=(ALL) NOPASSWD: /path/to/windsurf-hooker/deploy.sh

# Save and exit (Ctrl+X, then Y, then Enter in nano)
```

### Problem: `Permission denied` when accessing /etc/windsurf

**Cause:** Windsurf process doesn't have read permissions

**Solution:**
```bash
# Re-run deployment to fix permissions
sudo ./deploy.sh

# Verify permissions
ls -la /etc/windsurf
# Should show: drwxr-xr-x root:root
```

### Problem: Files not updating after `git pull`

**Cause:** Git hooks not installed properly

**Solution:**
```bash
# Verify hooks exist
ls -la .git/hooks/post-checkout
ls -la .git/hooks/post-merge

# If missing, reinstall:
./init
```

### Problem: `deploy.sh: No such file or directory`

**Cause:** Not in the correct directory

**Solution:**
```bash
# Navigate to repository root
cd windsurf-hooker

# Check you're in the right place
pwd  # Should end with windsurf-hooker
ls deploy.sh  # Should list the file

# Now run
./init
```

### Problem: `Cannot create directory /etc/windsurf: Permission denied`

**Cause:** Attempting to run without sudo

**Solution:**
```bash
# The init script calls deploy.sh with sudo automatically
# But if running deploy.sh directly:
sudo ./deploy.sh

# Or use init (which handles sudo):
./init
```

### Problem: Backup directory filling up disk space

**Cause:** Many backups accumulating (each timestamped)

**Solution:**
```bash
# Clean old backups (keep last 10)
ls -t /etc/windsurf.backup.* | tail -n +11 | xargs rm -rf

# Or set up automatic cleanup
cat >> /etc/cron.monthly/windsurf-cleanup << 'EOF'
#!/bin/bash
find /etc/windsurf.backup.* -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
find /usr/local/share/windsurf-hooks.backup.* -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
find /root/.codeium/hooks.backup.* -mtime +30 -exec rm -rf {} \; 2>/dev/null || true
EOF

chmod +x /etc/cron.monthly/windsurf-cleanup
```

### Getting Help

If you're still stuck:

1. **Check the logs:** `tail /var/log/windsurf-deploy.log`
2. **Check the docs:** [docs/user-guide/troubleshooting.md](docs/user-guide/troubleshooting.md)
3. **Open an issue:** [GitHub Issues](https://github.com) with error message
4. **Email maintainers:** maintainers@project.org

---

## Glossary

**Terms explained in plain language for non-technical readers:**

| Term | What It Means | Real-World Analogy |
|------|---------------|-------------------|
| **Repository** | A folder that tracks file changes | A filing cabinet with history of every document change |
| **Clone** | Download a copy of the repository | Photocopying the entire filing cabinet |
| **Git** | Software that tracks changes | A change-tracking system (like "Track Changes" in Word) |
| **Hook** | An automatic action triggered by an event | A mousetrap that springs when triggered |
| **Deploy** | Install files on a system | Copying a recipe from your phone to your kitchen |
| **Sudo** | Administrative command (run as root) | Master key that unlocks system-level access |
| **Root** | System administrator with full access | The person with the master key |
| **Permission** | Rule about who can read/write files | Lock settings (readable by all, writable by some) |
| **chmod** | Change file permissions | Changing lock settings |
| **chown** | Change who owns a file | Changing who the key belongs to |
| **Bash** | Shell scripting language | Instructions written in system language |
| **Python** | Programming language | Another way to write system instructions |
| **Environment** | Settings for how something works | Configuration like temperature for a machine |
| **SSH** | Secure connection to another computer | Encrypted phone call to another computer |
| **Backup** | Copy of important files | Duplicate copy for emergency recovery |
| **Rollback** | Restore to previous version | Undo to "undo all recent changes" |
| **Idempotent** | Safe to run multiple times | Hitting save repeatedly doesn't break anything |
| **Timestamp** | Date and time stamp | Date-stamped backup like "2025-02-01-14:32" |

---

## Support & Community

### Getting Help

- **Bug reports:** [GitHub Issues](https://github.com)
- **Discussions:** [GitHub Discussions](https://github.com)
- **Security concerns:** [SECURITY.md](SECURITY.md)

### Contributing

Want to improve this project? See [CONTRIBUTING.md](CONTRIBUTING.md)

### License

Apache License 2.0 - See [LICENSE](LICENSE)

---

## Status & Roadmap

**Current Version:** 2.0.0  
**Status:** Production Ready  

**Recent Changes:**
- ✅ Auto-deployment on git operations
- ✅ Timestamped backups
- ✅ Automated initialization
- ✅ Multi-location deployment

**Planned:**
- Multi-OS testing pipeline
- Ansible playbook support
- Docker container examples
- Monitoring integration

See [CHANGELOG.md](CHANGELOG.md) for detailed version history.

---

## Architecture & Design

For detailed architecture documentation, see:
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [docs/architecture/](docs/architecture/) - Technical details
- [docs/architecture/adr/](docs/architecture/adr/) - Design decisions

For security and compliance:
- [SECURITY.md](SECURITY.md) - Security policies
- [docs/enterprise/](docs/enterprise/) - Enterprise deployment

---

**Last Updated:** February 2026  
**Maintained By:** Engineering Team  
**Repository:** https://github.com/your-org/windsurf-hooker
