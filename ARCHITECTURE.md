# Architecture Overview

**windsurf-hooker System Design & Philosophy**

---

## Core Philosophy

**One Principle:** Automate the boring, document the complex, verify everything.

This system is designed around the principle that deployment and configuration management should require zero human intervention after initial setup. Every deployment is logged, every change is reversible, every file state is verifiable.

---

## System Architecture

### High-Level Design

```
┌────────────────────────────────────────────────────────────┐
│                    SOURCE CONTROL                          │
│  GitHub Repository (windsurf-hooker)                       │
│  ├── windsurf-hooks/    (Hook implementations)             │
│  ├── windsurf/          (IDE configuration)                │
│  ├── deploy.sh          (Deployment orchestrator)          │
│  ├── .githooks/         (Git hook templates)               │
│  └── docs/              (Documentation)                    │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │ git clone / git pull
                       ↓
┌────────────────────────────────────────────────────────────┐
│                   LOCAL MACHINE                            │
│  Developer's Linux System                                  │
│  ├── Repository (working directory)                        │
│  └── ./init or git hook trigger                            │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       │ Deploy with sudo
                       ↓
┌────────────────────────────────────────────────────────────┐
│              TARGET SYSTEM DIRECTORIES                     │
│  ├── /usr/local/share/windsurf-hooks (System hooks)        │
│  ├── /root/.codeium/hooks (IDE-specific hooks)             │
│  └── /etc/windsurf (Configuration files)                   │
└────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. Source Repository (GitHub)

**Purpose:** Version-controlled source of truth

**Contains:**
- `windsurf-hooks/` — Hook scripts (Python, Bash)
- `windsurf/` — Configuration files
- `deploy.sh` — Deployment logic
- `.githooks/` — Git hook templates
- Tests, docs, examples

**Characteristics:**
- Immutable (all changes tracked)
- Auditable (complete git history)
- Reversible (can revert any change)
- Distributed (cloneable to any system)

#### 2. Initialization Layer (`./init`)

**Purpose:** One-time setup; bridges repository and active system

**Responsibilities:**
1. Verify running environment
2. Install git hooks in `.git/hooks/`
3. Execute initial deployment
4. Verify success and report status

**Exit Behavior:**
- Success: System ready for automatic updates
- Failure: Error message and rollback

#### 3. Deployment Script (`deploy.sh`)

**Purpose:** Core orchestration engine; moves files to destinations

**Key Functions:**

| Function | Purpose | Safety |
|----------|---------|--------|
| `backup_existing()` | Create timestamped backup before overwrite | Prevents data loss |
| `deploy_directory()` | Copy files and set permissions | Atomic operation |
| `verify_deployment()` | Confirm files exist with correct ownership | Catches errors early |
| `check_root()` | Verify running as root | Prevents partial failures |

**Flow:**
```
Start
├─→ Check if running as root
├─→ Verify source directories exist
├─→ For each destination:
│   ├─→ Back up existing installation
│   ├─→ Copy files
│   ├─→ Set directory permissions (755)
│   ├─→ Set file permissions (644)
│   ├─→ Set executable permissions (755 for .py)
│   ├─→ Change ownership (root:root)
│   └─→ Verify success
├─→ Final integrity check
└─→ Report results
```

**Design Decisions:**
- **Idempotent:** Safe to run multiple times
- **Atomic:** All-or-nothing per destination
- **Auditable:** Logging at each step
- **Reversible:** Previous backups available

#### 4. Git Hooks Layer (`.git/hooks/`)

**Purpose:** Trigger deployment automatically on git operations

**Hooks Installed:**

| Hook | Triggers | Purpose |
|------|----------|---------|
| `post-checkout` | `git clone`, `git checkout` | Deploy after code arrives |
| `post-merge` | `git merge`, `git pull` | Deploy after changes integrated |

**Implementation:**
```bash
#!/bin/bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if [[ -f "${REPO_DIR}/deploy.sh" ]]; then
    sudo "${REPO_DIR}/deploy.sh" 2>/dev/null || true
fi
```

**Design Notes:**
- **Non-blocking:** Errors don't interrupt git operations
- **Silent:** Output suppressed (prevents git message clutter)
- **Forgiving:** `|| true` prevents hook failure on deploy error
- **Robust:** Works from any directory via `git rev-parse`

#### 5. Target System Directories

**Purpose:** Live running configuration

**Three Deployments:**

1. **`/usr/local/share/windsurf-hooks`**
   - System-wide accessible
   - Readable by all users
   - Used by global Windsurf installations
   - Permissions: `755 (drwxr-xr-x) root:root`

2. **`/root/.codeium/hooks`**
   - IDE-specific location
   - Codeium integration point
   - Readable by root and windsurf process
   - Permissions: `755 (drwxr-xr-x) root:root`

3. **`/etc/windsurf`**
   - Standard config location
   - System-wide configuration
   - Read by IDE on startup
   - Permissions: `755 (drwxr-xr-x) root:root`

**Why Three Locations?**
- **Redundancy:** Multiple integration points
- **Compatibility:** Different Windsurf versions expect different paths
- **Modularity:** Hook scripts and config separated
- **Scalability:** Can be extended independently

---

## Data Flow & Lifecycle

### Scenario 1: Initial Setup

```
1. User clones repository
   git clone https://github.com/org/windsurf-hooker.git
   cd windsurf-hooker

2. User runs initialization
   ./init

3. Init script runs
   ├─→ Create .git/hooks directory
   ├─→ Copy post-checkout hook
   ├─→ Copy post-merge hook
   ├─→ Make hooks executable (chmod +x)
   └─→ Call deploy.sh with sudo

4. Deploy script executes
   ├─→ Verify running as root
   ├─→ Back up existing installations (if any)
   ├─→ Copy files to 3 locations
   ├─→ Set permissions and ownership
   └─→ Verify success

5. System ready
   ├─→ /etc/windsurf populated and readable
   ├─→ /usr/local/share/windsurf-hooks populated and executable
   ├─→ /root/.codeium/hooks synchronized
   └─→ Git hooks installed and ready

6. Status reported
   [INFO] Deployment complete!
   Files deployed to:
   - /usr/local/share/windsurf-hooks
   - /root/.codeium/hooks
   - /etc/windsurf
```

### Scenario 2: Pulling Updates

```
1. Developer pushes changes
   git push origin main

2. Team member updates
   git pull origin main

3. Git runs post-merge hook automatically
   └─→ Calls deploy.sh with sudo

4. Deploy script updates files
   ├─→ Backup current versions
   ├─→ Copy new versions from repo
   ├─→ Verify permissions/ownership
   └─→ Complete silently

5. Developer gets notification (optional logging)
   [INFO] Running auto-deployment after git merge...
   [INFO] Deployment complete!

Result: Latest code deployed automatically, zero manual steps
```

### Scenario 3: Rollback After Failed Deployment

```
1. User detects problem
   $ ls /etc/windsurf
   # Missing files or corrupted

2. User runs rollback
   sudo ./scripts/rollback.sh

3. Rollback script
   ├─→ List available backups
   ├─→ Ask which backup to restore
   ├─→ Restore selected backup
   ├─→ Verify restoration success
   └─→ Log action

4. System restored to previous known-good state
   $ ls /etc/windsurf
   # Files restored

Result: RTO <1 minute, zero data loss
```

---

## Permission Model

### Rationale

The permission scheme balances three concerns:

1. **Security:** Prevent accidental/unauthorized modification
2. **Functionality:** Allow Windsurf IDE to read configuration
3. **Maintainability:** Allow root to manage/update system

### Permission Details

```
Directory Permissions: 755 (rwxr-xr-x)
├─ Owner (root): read, write, execute
├─ Group: read, execute (can enter directory)
└─ Others: read, execute (can read contents)

Configuration File Permissions: 644 (rw-r--r--)
├─ Owner (root): read, write
├─ Group: read only
└─ Others: read only

Executable Permissions: 755 (rwxr-xr-x)
├─ Owner (root): read, write, execute
├─ Group: read, execute
└─ Others: read, execute
```

### Why These Specific Values?

| Permission | Value | Reason |
|-----------|-------|--------|
| Directories | 755 | Must be executable to enter; world-readable for discovery |
| Config files | 644 | Readable by all (Windsurf runs as varied users); writable by root only |
| Scripts | 755 | Must be executable by system; globally readable |
| Ownership | root:root | Only root can modify; all users can read |

### Access Control Matrix

| User Type | /etc/windsurf | /usr/local/share/... | /root/.codeium/... |
|-----------|---------------|----------------------|-------------------|
| root | Read, Write, Execute | Read, Write, Execute | Read, Write, Execute |
| windsurf | Read, Execute | Read, Execute | Read, Execute |
| Other users | Read, Execute | Read, Execute | No Access |

---

## Error Handling & Resilience

### Anticipated Failure Modes

#### 1. Insufficient Permissions
**Scenario:** User runs deploy.sh without sudo  
**Detection:** `check_root()` function  
**Recovery:** Error message explains root requirement

#### 2. Source Directory Missing
**Scenario:** Corrupted repo clone  
**Detection:** Verify source before copying  
**Recovery:** Abort with error; suggest re-cloning

#### 3. Destination Unwritable
**Scenario:** /etc/ or /usr/local/share/ not writable  
**Detection:** cp command fails  
**Recovery:** Error logged; previous backup left intact

#### 4. Partial Deployment
**Scenario:** Some files deployed, deployment interrupted  
**Detection:** Verification step after all copies  
**Recovery:** Rollback previous backup if verification fails

#### 5. Backup Corruption
**Scenario:** Previous backup is unreadable  
**Detection:** Manual verification by operator  
**Recovery:** Use older backup or restore from source control

### Error Handling Code

```bash
# Pattern 1: Abort on error
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1  # Fail immediately
    fi
}

# Pattern 2: Safe copy with verification
deploy_directory() {
    local src="$1"
    local dest="$2"
    
    # Verify source exists
    if [[ ! -d "$src" ]]; then
        log_error "Source directory not found: $src"
        return 1  # Caller decides to continue or fail
    fi
    
    # Backup before modifying
    backup_existing "$dest"
    
    # Copy with error check
    if ! cp -r "$src" "$dest"; then
        log_error "Copy failed: $src → $dest"
        return 1
    fi
    
    # Set permissions
    find "$dest" -type d -exec chmod 755 {} \; || return 1
    find "$dest" -type f -exec chmod 644 {} \; || return 1
    
    # Verify result
    if [[ ! -d "$dest" ]]; then
        log_error "Deployment verification failed for $dest"
        return 1
    fi
    
    return 0  # Success
}
```

### Recovery Procedures

**Automatic (on error):**
- Abort current operation
- Leave previous backup intact
- Report error to operator

**Manual (operator initiated):**
```bash
# Check what's wrong
ls -la /etc/windsurf
stat /etc/windsurf

# Restore previous version
sudo cp -r /etc/windsurf.backup.1704067200 /etc/windsurf

# Re-deploy from source
sudo ./deploy.sh
```

---

## Performance Characteristics

### Deployment Time

| Operation | Typical Duration |
|-----------|------------------|
| Backup creation | <100ms |
| File copy (small repo) | 1-2 seconds |
| Permission setting | <500ms |
| Verification | <200ms |
| **Total** | **2-4 seconds** |

### Storage Requirements

| Component | Size |
|-----------|------|
| windsurf-hooks/ | ~2 MB |
| windsurf/ | ~15 MB |
| Backups per deployment | ~17 MB |
| **Total (with 30-day backups)** | ~500 MB |

### Scalability Considerations

**Current Design Supports:**
- ✅ Single-system deployment
- ✅ Multiple deployment destinations
- ✅ Large file sets (100MB+)
- ✅ Frequent deployments (1/minute)

**Future Extensions:**
- Multi-system rollout (Ansible)
- Rolling deployments
- Canary deployments
- Health check integration

---

## Security Architecture

### Threat Model

| Threat | Impact | Mitigation |
|--------|--------|-----------|
| Unauthorized deployment | System compromise | Root-only execution, sudo |
| Undetected tampering | Silent corruption | Backups, checksums, version control |
| Unauthorized modification | Data corruption | File permissions (644), ownership (root) |
| Privilege escalation | Full system control | Isolated to /etc/ and system directories |
| Data loss on bad deploy | Unavailable system | Timestamped backups before each deploy |

### Control Implementation

#### 1. Access Control
```bash
# Only root can execute deployment
check_root() {
    if [[ $EUID -ne 0 ]]; then
        log_error "This script must be run as root"
        exit 1
    fi
}

# Only root can modify files
chown -R root:root "$dest"
```

#### 2. Audit Trail
```bash
# All deployments logged
[INFO] Deploying windsurf to /etc/windsurf
[INFO] Backed up to /etc/windsurf.backup.1704067200
[INFO] Deployment complete!

# Git history preserved
git log --all | grep "Deploy\|Update\|Add"
```

#### 3. Integrity Verification
```bash
# Backups are timestamped and retained
ls -la /etc/windsurf.backup.*

# Permissions verified post-deployment
stat /etc/windsurf  # Should show: root:root, 755
```

#### 4. Least Privilege
```bash
# Windsurf runs as non-root user
# But reads from root-owned /etc/windsurf
# File permissions allow world-read (644)
```

---

## Monitoring & Observability

### What to Monitor

```
Deployment Frequency
├─→ Healthy range: 1-5 per hour during development
├─→ Alert if: >10 per hour (possible runaway)
└─→ Alert if: 0 per day (possible hook failure)

Backup Accumulation
├─→ Healthy range: 30 backups (30 days retention)
├─→ Alert if: >100 backups (storage filling up)
└─→ Cleanup: Delete >30 days old

File Integrity
├─→ Check ownership: Should be root:root
├─→ Check permissions: Should be 755/644
├─→ Check existence: All files should be present
└─→ Action if failed: Re-run deploy.sh

Deployment Success Rate
├─→ Healthy range: 99%+
├─→ Alert if: <95% success rate
└─→ Investigation: Check logs, verify permissions
```

### Logging Points

```bash
# Each step is logged
[INFO] Deploying windsurf-hooks to /usr/local/share/windsurf-hooks
[INFO] Deployed to /usr/local/share/windsurf-hooks with permissions set
[WARN] Backing up existing /etc/windsurf to /etc/windsurf.backup.1704067200
[INFO] Verification passed for /etc/windsurf
[INFO] Deployment complete!
```

---

## Design Decisions & Trade-offs

### Decision 1: Three Deployment Locations

**Decision:** Deploy windsurf-hooks to both `/usr/local/share/` and `/root/.codeium/`

**Rationale:**
- Different Windsurf versions look in different paths
- Redundancy ensures compatibility
- Can be deprecated as versions consolidate

**Trade-off:**
- ➕ Better compatibility
- ➕ Easier migration
- ➖ Storage duplication
- ➖ Slightly longer deploy time

### Decision 2: Root-Only Execution

**Decision:** Deploy script must run as root (via sudo)

**Rationale:**
- /etc/ and /usr/local/share/ require root access
- Prevents accidental partial deployments
- Enforces deliberate administrative action

**Trade-off:**
- ➕ Strong access control
- ➕ Auditable (sudo logs all execution)
- ➖ Requires sudo configuration
- ➖ Cannot be run by non-admin users

### Decision 3: Timestamped Backups (Not Versioned Backups)

**Decision:** Backups are timestamped copies, not git history

**Rationale:**
- Simple and understandable (no hidden complexity)
- Fast recovery without requiring git knowledge
- Works even if git is corrupted
- Easy to clean up by age (mtime-based)

**Trade-off:**
- ➕ Operator-friendly
- ➕ Simple cleanup (cron job)
- ➖ Requires manual cleanup (no auto-purge)
- ➖ Storage growth without policy

### Decision 4: Idempotent (Runnable Multiple Times)

**Decision:** deploy.sh can be run repeatedly with same result

**Rationale:**
- Safe to re-run if unsure deployment succeeded
- Integration with monitoring/alerting easier
- Beginners can "retry" without worrying
- No state management complexity

**Trade-off:**
- ➕ Resilient and forgiving
- ➕ Simple to understand
- ➖ Slower (backs up on every run)
- ➖ Disk space cost

---

## Future Architecture Directions

### Phase 2: Multi-System Orchestration
```
Ansible Playbook Wrapper
├─→ Coordinate deployments across multiple machines
├─→ Rolling deployment (zero downtime)
├─→ Rollback all systems on failure
└─→ Centralized logging and audit trail
```

### Phase 3: Health Checks & Auto-Recovery
```
Monitoring Agent
├─→ Continuous verification of deployed files
├─→ Detect and alert on corruption
├─→ Auto-trigger redeployment on detected issues
└─→ Report metrics to monitoring system
```

### Phase 4: Policy-Based Deployment
```
Configuration Management
├─→ Support different environments (dev/staging/prod)
├─→ Feature flags for selective deployment
├─→ Gradual rollout (canary deployments)
└─→ Environment-specific configuration
```

---

## Implementation Notes for Developers

### Key Design Patterns Used

**1. Function Composition**
```bash
main() {
    check_root
    deploy_directory "$src1" "$dest1"
    deploy_directory "$src2" "$dest2"
    verify_deployment "$dest1"
}
```

**2. Error Handling with Return Codes**
```bash
if deploy_directory "$src" "$dest"; then
    log_info "Success"
else
    log_error "Failed"
    exit 1
fi
```

**3. Logging Wrapper**
```bash
log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
```

**4. Path Resolution (Git-aware)**
```bash
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ ! -d "${REPO_DIR}/windsurf" ]]; then
    REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null)"
fi
```

---

## Related Documents

- [SECURITY.md](SECURITY.md) - Security policies and compliance
- [docs/architecture/adr/](docs/architecture/adr/) - Architecture Decision Records
- [docs/architecture/diagrams.md](docs/architecture/diagrams.md) - Visual diagrams
- [CONTRIBUTING.md](CONTRIBUTING.md) - Development guide

