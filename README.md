# windsurf-hooker

**Enterprise-grade automation for Windsurf IDE configuration deployment and security hook management**

[![Tests](https://img.shields.io/badge/tests-automated-brightgreen)](https://github.com)
[![Security](https://img.shields.io/badge/security-hardened-blue)](SECURITY.md)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Enterprise](https://img.shields.io/badge/enterprise-production%20ready-green)](README_ENTERPRISE.md)

---

## System Inventory Index

This repository implements a comprehensive security framework for Windsurf IDE with the following components:

| Name/Identifier | Type | File Path(s) | Entry Points/Triggers | Inputs | Outputs | Dependencies | Failure Modes | Security Impact | Observability | Config Knobs |
|---|---|---|---|---|---|---|---|---|---|---|
| **pre_intent_classification** | Hook | `windsurf-hooks/pre_intent_classification.py` | User prompt processing | Prompt text, context | Intent classification JSON | Python stdlib, regex patterns | Invalid classification, low confidence | Medium (access control basis) | Structured logs to stderr | Confidence threshold (0.80) |
| **pre_plan_resolution** | Hook | `windsurf-hooks/pre_plan_resolution.py` | After intent classification | Intent, workspace context | Plan resolution status | File system, policy.json | Missing plan files, permission errors | Low (workflow gating) | Plan search logs | Search paths list |
| **pre_user_prompt_gate** | Hook | `windsurf-hooks/pre_user_prompt_gate.py` | Before prompt processing | User prompt content | Prompt validation result | Policy patterns | Pattern matching failures | Medium (input filtering) | Validation logs | Blocked patterns |
| **pre_write_diff_quality** | Hook | `windsurf-hooks/pre_write_diff_quality.py` | Before code writes | Diff content, file list | Quality assessment | Text processing | Large diffs, complexity overflow | Low (code quality) | Quality metrics | Max lines per edit (100) |
| **pre_write_code_escape_detection** | Hook | `windsurf-hooks/pre_write_code_escape_detection.py` | Code write phase | Code content | Escape detection result | Regex patterns | Pattern evasion | High (RCE prevention) | Escape attempt logs | Escape patterns list |
| **pre_write_code_policy** | Hook | `windsurf-hooks/pre_write_code_policy.py` | Code write phase | Code content | Policy compliance | Policy.json | Policy violations | Medium (code standards) | Violation logs | Policy rules |
| **pre_filesystem_write_atlas_enforcement** | Hook | `windsurf-hooks/pre_filesystem_write_atlas_enforcement.py` | File write attempts | File paths, content | ATLAS gate validation | ATLAS framework | Gate bypass attempts | Critical (filesystem security) | Gate enforcement logs | Forbidden paths |
| **pre_filesystem_write** | Hook | `windsurf-hooks/pre_filesystem_write.py` | File write attempts | File operations | Safety validation | File system checks | Unsafe paths, permissions | Medium (file safety) | Safety check logs | Suspicious patterns |
| **pre_mcp_tool_use_atlas_gate** | Hook | `windsurf-hooks/pre_mcp_tool_use_atlas_gate.py` | MCP tool calls | Tool name, parameters | ATLAS gate authorization | ATLAS MCP server | Invalid tools, malformed payloads | Critical (MCP security) | Gate decision logs | Allowed tools list |
| **pre_mcp_tool_use_allowlist** | Hook | `windsurf-hooks/pre_mcp_tool_use_allowlist.py` | MCP tool calls (fallback) | Tool requests | Allowlist validation | Policy.json | Allowlist mismatches | Medium (MCP filtering) | Allowlist logs | Tool allowlist |
| **pre_run_command_kill_switch** | Hook | `windsurf-hooks/pre_run_command_kill_switch.py` | Command execution | Command strings | Kill switch validation | Kill switch config | Switch activation | High (execution control) | Kill switch logs | Kill switch state |
| **pre_run_command_blocklist** | Hook | `windsurf-hooks/pre_run_command_blocklist.py` | Command execution | Command strings | Blocklist validation | Blocklist patterns | Blocklist matches | Medium (command filtering) | Blocklist logs | Blocked patterns |
| **post_write_semantic_diff** | Hook | `windsurf-hooks/post_write_semantic_diff.py` | After code writes | File changes | Semantic analysis | Diff tools | Analysis failures | Low (change tracking) | Semantic logs | Analysis depth |
| **post_write_observability** | Hook | `windsurf-hooks/post_write_observability.py` | After code writes | Write operations | Observability metrics | Logging system | Metric collection failures | Low (monitoring) | Metrics logs | Logging thresholds |
| **post_write_verify** | Hook | `windsurf-hooks/post_write_verify.py` | After code writes | Written files | Verification results | File system | Verification failures | Medium (integrity) | Verification logs | Verification rules |
| **post_refusal_audit** | Hook | `windsurf-hooks/post_refusal_audit.py` | After operation refusals | Refusal context | Audit trail | Audit system | Audit failures | Medium (compliance) | Audit logs | Audit format |
| **post_session_entropy_check** | Hook | `windsurf-hooks/post_session_entropy_check.py` | Session end | Session history | Entropy analysis | Session state | Entropy threshold breach | Low (session health) | Entropy logs | Entropy threshold (0.7) |
| **00-kaiza-global-rules** | Rule | `windsurf/rules/00-kaiza-global-rules.md` | Always active | All operations | Governance constraints | Rule engine | Rule violations | High (system governance) | Rule enforcement logs | Rule parameters |
| **00-production-or-nothing** | Rule | `windsurf/rules/00-production-or-nothing.md` | Always active | Code generation | Production requirements | Quality checks | Production standard failures | High (code quality) | Quality logs | Production standards |
| **05-defects-block-work** | Rule | `windsurf/rules/05-defects-block-work.md` | Always active | All operations | Defect detection | Defect patterns | Defect detection failures | Medium (defect prevention) | Defect logs | Defect patterns |
| **05-no-existing-violations** | Rule | `windsurf/rules/05-no-existing-violations.md` | Always active | Code changes | Violation checking | Violation patterns | Violation misses | Medium (compliance) | Violation logs | Violation rules |
| **06-no-containment** | Rule | `windsurf/rules/06-no-containment.md` | Always active | System operations | Containment prevention | Security policies | Containment breaches | High (security) | Security logs | Containment rules |
| **10-debug-mode** | Rule | `windsurf/rules/10-debug-mode.md` | Always active | Debug operations | Debug validation | Debug policies | Debug violations | Low (debug safety) | Debug logs | Debug rules |
| **10-refusal-behavior** | Rule | `windsurf/rules/10-refusal-behavior.md` | Always active | Refusal events | Refusal validation | Refusal policies | Refusal policy violations | Low (behavior) | Refusal logs | Refusal rules |
| **20-definition-of-done** | Rule | `windsurf/rules/20-definition-of-done.md` | Always active | Task completion | Done validation | Done criteria | Done criteria failures | Medium (quality) | Done logs | Done criteria |
| **policy.json** | Policy | `windsurf/policy/policy.json` | System initialization | Policy requests | Policy configuration | JSON schema | Policy load failures | Critical (system policy) | Policy logs | Policy settings |
| **MANIFEST.json** | Skill Registry | `windsurf/skills/MANIFEST.json` | Skill discovery | Skill requests | Skill metadata | JSON schema | Manifest load failures | Medium (skill management) | Skill logs | Skill configurations |
| **no-placeholders-production-code** | Skill | `windsurf/skills/no-placeholders-production-code/` | Code generation tasks | Code context | Production-ready code | Pattern matching | Placeholder detection failures | Medium (code quality) | Quality logs | Placeholder patterns |
| **test-engineering-suite** | Skill | `windsurf/skills/test-engineering-suite/` | Testing tasks | Code context | Test implementations | Testing frameworks | Test generation failures | Medium (test coverage) | Test logs | Coverage targets |
| **audit-first-commentary** | Skill | `windsurf/skills/audit-first-commentary/` | Code documentation | Code context | Audit-ready comments | Documentation standards | Commentary generation failures | Low (documentation) | Documentation logs | Commentary standards |
| **debuggable-by-default** | Skill | `windsurf/skills/debuggable-by-default/` | Code implementation | Code context | Debuggable code | Debugging frameworks | Debug feature failures | Medium (debuggability) | Debug logs | Debug requirements |
| **secure-by-default** | Skill | `windsurf/skills/secure-by-default/` | Code implementation | Code context | Secure code | Security frameworks | Security implementation failures | High (security) | Security logs | Security standards |
| **refactor-with-safety** | Skill | `windsurf/skills/refactor-with-safety/` | Refactoring tasks | Code context | Safe refactors | Refactoring tools | Refactoring safety failures | Medium (code safety) | Refactor logs | Safety rules |
| **kaiza-mcp-ops** | Skill | `windsurf/skills/kaiza-mcp-ops/` | MCP operations | MCP context | Safe MCP operations | MCP framework | MCP operation failures | High (MCP security) | MCP logs | MCP rules |
| **repo-understanding** | Skill | `windsurf/skills/repo-understanding/` | Repository analysis | Repository context | Repository understanding | Analysis tools | Analysis failures | Low (understanding) | Analysis logs | Analysis depth |
| **release-readiness** | Skill | `windsurf/skills/release-readiness/` | Release tasks | Release context | Release validation | Release criteria | Release validation failures | Medium (release quality) | Release logs | Release criteria |
| **observability-pack-implementer** | Skill | `windsurf/skills/observability-pack-implementer/` | Observability tasks | Code context | Observability implementation | Observability frameworks | Implementation failures | Medium (observability) | Observability logs | Observability standards |
| **incident-triage-and-rca** | Skill | `windsurf/skills/incident-triage-and-rca/` | Incident response | Incident context | Incident analysis | Incident tools | Analysis failures | Medium (incident response) | Incident logs | Incident procedures |
| **df** | Workflow | `windsurf/global_workflows/df.md` | Slash command `/df` | File system context | File system analysis | File system tools | Analysis failures | Low (information) | Workflow logs | Analysis parameters |
| **fix-bug** | Workflow | `windsurf/global_workflows/fix-bug.md` | Slash command `/fix-bug` | Bug context | Bug fix process | Debug tools | Fix process failures | Medium (bug resolution) | Workflow logs | Fix procedures |
| **implement-feature** | Workflow | `windsurf/global_workflows/implement-feature.md` | Slash command `/implement-feature` | Feature context | Feature implementation | Development tools | Implementation failures | Medium (feature delivery) | Workflow logs | Implementation steps |
| **pre-pr-review** | Workflow | `windsurf/global_workflows/pre-pr-review.md` | Slash command `/pre-pr-review` | PR context | PR review process | Review tools | Review process failures | Low (code review) | Workflow logs | Review criteria |
| **refactor-module** | Workflow | `windsurf/global_workflows/refactor-module.md` | Slash command `/refactor-module` | Module context | Refactoring process | Refactoring tools | Refactoring failures | Medium (code quality) | Workflow logs | Refactoring steps |
| **release-candidate** | Workflow | `windsurf/global_workflows/release-candidate.md` | Slash command `/release-candidate` | Release context | Release process | Release tools | Release process failures | High (release safety) | Workflow logs | Release procedures |
| **security-hardening-sprint** | Workflow | `windsurf/global_workflows/security-hardening-sprint.md` | Slash command `/security-hardening-sprint` | Security context | Security hardening | Security tools | Hardening failures | High (security) | Workflow logs | Security procedures |
| **triage-prod-issue** | Workflow | `windsurf/global_workflows/triage-prod-issue.md` | Slash command `/triage-prod-issue` | Issue context | Issue triage | Triage tools | Triage failures | Medium (incident response) | Workflow logs | Triage procedures |
| **upgrade-deps** | Workflow | `windsurf/global_workflows/upgrade-deps.md` | Slash command `/upgrade-deps` | Dependency context | Dependency upgrade | Dependency tools | Upgrade failures | Medium (dependency management) | Workflow logs | Upgrade procedures |
| **tests.yml** | CI/CD | `.github/workflows/tests.yml` | Git push/PR | Repository state | Test results | GitHub Actions | Test failures | Medium (CI/CD) | CI logs | Test configuration |

---

## Deep Dive Analysis

### Hook Components

#### pre_intent_classification

**A. Purpose & Scope**
Classifies user intent with confidence scoring to separate WHAT (intent) from HOW (mode/approach). Emits structured intent classification for downstream hooks. Does NOT block operations - purely informational.

**B. Definition & Location**
- File: `windsurf-hooks/pre_intent_classification.py`
- Registered in: `windsurf/hooks.json` under `pre_intent_classification`
- Entry point: Python script executed via `python3 /usr/local/share/windsurf-hooks/pre_intent_classification.py`

**C. Triggering & Lifecycle**
- Trigger: User prompt processing before any operation
- Ordering: First hook in execution chain
- Synchronous: Blocks prompt processing until classification complete
- Precedence: Highest (sets context for all subsequent hooks)

**D. Inputs / Outputs / Side Effects**
- Inputs: Prompt text, session context
- Outputs: JSON with `primary_intent`, `confidence`, `secondary_intents`
- Side Effects: Writes classification to stderr for logging

**E. Contracts & Interfaces**
```python
def classify_intent(prompt: str) -> Dict[str, any]:
    Returns: {
        "primary_intent": "code_write|repair|audit|explore",
        "confidence": 0.0-1.0,
        "secondary_intents": [...]
    }
```

**F. Error Handling & Failure Containment**
- Fails open: If classification fails, defaults to "explore" with 0.5 confidence
- No retries: Classification is deterministic
- Blast radius: Limited to intent context only

**G. Security & Compliance Analysis**
- Trust boundary: User input processing
- Sensitive data: Prompt content may contain sensitive information
- Injection risk: Low (regex-based, no code execution)
- Guardrails: Pattern-based classification only

**H. Observability & Auditability**
- Logs: Structured JSON to stderr with intent classification
- Metrics: Confidence scores, intent distribution
- Audit trail: Intent classification recorded for each session

**I. Examples**
```bash
# Minimal invocation
echo "Implement a user authentication system" | python3 pre_intent_classification.py
# Output: {"primary_intent": "code_write", "confidence": 0.9}
```

#### pre_mcp_tool_use_atlas_gate

**A. Purpose & Scope**
ATLAS-GATE Primary Gate implementing hard security boundary for all MCP tool usage. Enforces that all capabilities must route through ATLAS-GATE MCP server. No fallback paths, no silent success.

**B. Definition & Location**
- File: `windsurf-hooks/pre_mcp_tool_use_atlas_gate.py`
- Registered in: `windsurf/hooks.json` under `pre_mcp_tool_use`
- Phase: `atlas_gate_primary_gate`

**C. Triggering & Lifecycle**
- Trigger: Any MCP tool use attempt
- Ordering: First MCP validation hook
- Synchronous: Blocks execution until validation complete
- Precedence: Critical security gate

**D. Inputs / Outputs / Side Effects**
- Inputs: Tool name, parameters, context
- Outputs: Allow/deny decision with reasoning
- Side Effects: Security decision logged, potentially blocks operation

**E. Contracts & Interfaces**
```python
ATLAS_GATE_OPS = {
    "atlas_gate.read": {"required": ["path"], "optional": ["encoding", "max_bytes"]},
    "atlas_gate.write": {"required": ["path", "content"], "optional": ["mode", "encoding"]},
    "atlas_gate.exec": {"required": ["command"], "optional": ["timeout", "env"]},
    "atlas_gate.stat": {"required": ["path"], "optional": []}
}
```

**F. Error Handling & Failure Containment**
- Fails closed: Any validation error blocks operation
- No retries: Security decisions are final
- Blast radius: System-wide security boundary

**G. Security & Compliance Analysis**
- Trust boundary: Critical security boundary
- Sensitive data: Tool parameters may contain sensitive information
- Injection risk: High (prevents code injection via tool parameters)
- Guardrails: Strict schema validation, allowlist enforcement

**H. Observability & Auditability**
- Logs: All security decisions with full context
- Metrics: Gate decisions, blocked attempts
- Audit trail: Complete record of all MCP tool usage attempts

**I. Examples**
```bash
# Allowed operation
python3 pre_mcp_tool_use_atlas_gate.py atlas_gate.read '{"path": "/etc/hosts"}'
# Output: {"allowed": true, "reason": "Valid ATLAS-GATE operation"}

# Blocked operation
python3 pre_mcp_tool_use_atlas_gate.py bash.run '{"command": "rm -rf /"}'
# Output: {"allowed": false, "reason": "Non-ATLAS-GATE tool not permitted"}
```

### Rule Components

#### 00-kaiza-global-rules

**A. Purpose & Scope**
Enforces global governance rules that apply to every Cascade session and workspace. Mandates production-grade code, auditability, debuggability, and security-by-default.

**B. Definition & Location**
- File: `windsurf/rules/00-kaiza-global-rules.md`
- Discovery: Always loaded by rule engine
- Registration: Automatic via filename convention (00-prefix)

**C. Triggering & Lifecycle**
- Trigger: All operations, always active
- Ordering: Highest precedence (00 prefix)
- Synchronous: Rules evaluated before any operation
- Precedence: Override all other rules

**D. Inputs / Outputs / Side Effects**
- Inputs: Operation context, code content, workspace state
- Outputs: Rule compliance status, violation reports
- Side Effects: May block operations that violate rules

**E. Contracts & Interfaces**
- Rule format: Markdown with structured sections
- Validation: Pattern-based and semantic analysis
- Enforcement: Hard blocking for critical violations

**F. Error Handling & Failure Containment**
- Fails closed: Rule violations block operations
- No retries: Rule evaluation is deterministic
- Blast radius: System-wide governance

**G. Security & Compliance Analysis**
- Trust boundary: System governance
- Sensitive data: Code and operation context
- Injection risk: Low (rule-based validation)
- Guardrails: Comprehensive security and quality requirements

**H. Observability & Auditability**
- Logs: Rule evaluations and violations
- Metrics: Compliance rates, violation types
- Audit trail: Complete rule enforcement record

**I. Examples**
```markdown
# Rule violation example
# Code contains placeholder "TODO"
# Rule: "Do not generate incomplete scaffolding"
# Action: Block operation with violation report
```

### Skill Components

#### no-placeholders-production-code

**A. Purpose & Scope**
Ensures all code output is production-ready with zero placeholders, stubs, mocks, or scaffolding. Validates code completeness, error handling, configuration, and tests.

**B. Definition & Location**
- Directory: `windsurf/skills/no-placeholders-production-code/`
- Manifest: `windsurf/skills/MANIFEST.json`
- Registration: Enabled in manifest

**C. Triggering & Lifecycle**
- Trigger: Code generation tasks
- Ordering: Applied during code writing phase
- Synchronous: Validates code before output
- Precedence: High (production quality)

**D. Inputs / Outputs / Side Effects**
- Inputs: Generated code, context
- Outputs: Production-ready code or rejection
- Side Effects: May require code revision

**E. Contracts & Interfaces**
- Placeholder patterns: TODO, FIXME, XXX, pass, unimplemented, stub
- Validation: Pattern scanning + semantic analysis
- Enforcement: Hard rejection of placeholder-containing code

**F. Error Handling & Failure Containment**
- Fails closed: Placeholders trigger rejection
- Retries: Suggests specific fixes
- Blast radius: Code quality only

**G. Security & Compliance Analysis**
- Trust boundary: Code quality enforcement
- Sensitive data: Generated code content
- Injection risk: Low (pattern matching)
- Guardrails: Comprehensive placeholder detection

**H. Observability & Auditability**
- Logs: Placeholder detections, rejections
- Metrics: Code quality scores
- Audit trail: Production readiness verification

**I. Examples**
```python
# Rejected code
def authenticate_user():
    # TODO: Implement authentication
    pass

# Accepted code
def authenticate_user(username: str, password: str) -> bool:
    """Authenticate user credentials.
    
    Args:
        username: User identifier
        password: Plain text password
        
    Returns:
        True if authentication successful, False otherwise
        
    Raises:
        AuthenticationError: For invalid credentials
        DatabaseError: For database connectivity issues
    """
    try:
        user = get_user_by_username(username)
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Failed authentication attempt for user: {username}")
            return False
        
        logger.info(f"Successful authentication for user: {username}")
        return True
    except DatabaseError as e:
        logger.error(f"Database error during authentication: {e}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during authentication: {e}")
        raise AuthenticationError("Authentication failed")
```

### Workflow Components

#### implement-feature

**A. Purpose & Scope**
Structured workflow for implementing a complete feature from requirement to production. Ensures all quality gates, testing, documentation, and release readiness criteria are met.

**B. Definition & Location**
- File: `windsurf/global_workflows/implement-feature.md`
- Registration: Slash command `/implement-feature`
- Discovery: Global workflow registry

**C. Triggering & Lifecycle**
- Trigger: Slash command invocation
- Ordering: Sequential step execution
- Synchronous: Blocks until completion
- Precedence: Standard workflow priority

**D. Inputs / Outputs / Side Effects**
- Inputs: Feature name, issue ID, description
- Outputs: Complete feature implementation
- Side Effects: Creates code, tests, documentation, PR

**E. Contracts & Interfaces**
- Steps: 7-phase implementation process
- Validation: Quality gates at each phase
- Artifacts: Code, tests, docs, deployment configs

**F. Error Handling & Failure Containment**
- Fails safe: Incomplete implementations blocked
- Rollback: Can revert to previous state
- Blast radius: Limited to feature branch

**G. Security & Compliance Analysis**
- Trust boundary: Feature development process
- Sensitive data: Feature requirements, code
- Injection risk: Low (structured workflow)
- Guardrails: Multiple quality and security gates

**H. Observability & Auditability**
- Logs: Step completion, quality gate results
- Metrics: Implementation time, quality scores
- Audit trail: Complete feature development record

**I. Examples**
```bash
# Workflow invocation
/implement-feature user-authentication issue-123 "Add OAuth2 authentication"

# Expected steps executed:
# 1. Understand Requirement & Design
# 2. Set Up Local Environment
# 3. Implement Core Logic
# 4. Add Tests
# 5. Documentation
# 6. Security Review
# 7. Release Preparation
```

---

## Global System Architecture

### System Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    Windsurf IDE                             │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   User Input    │    │     Hook Execution Pipeline      │ │
│  └─────────┬───────┘    └─────────────────┬───────────────┘ │
│            │                              │                 │
│  ┌─────────▼───────┐    ┌─────────────────▼───────────────┐ │
│  │ Intent Classify │───▶│ pre_* Hooks (Security Gates)    │ │
│  └─────────┬───────┘    └─────────────────┬───────────────┘ │
│            │                              │                 │
│  ┌─────────▼───────┐    ┌─────────────────▼───────────────┐ │
│  │  Plan Resolution│───▶│ Operation Execution (MCP/Files) │ │
│  └─────────┬───────┘    └─────────────────┬───────────────┘ │
│            │                              │                 │
│  ┌─────────▼───────┐    ┌─────────────────▼───────────────┐ │
│  │   Skills Apply  │◀───│ post_* Hooks (Audit/Observability)│ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Execution Model

```
1. USER INPUT
   ↓
2. pre_intent_classification (Intent Analysis)
   ↓
3. pre_plan_resolution (Plan Validation)
   ↓
4. pre_user_prompt_gate (Input Filtering)
   ↓
5. OPERATION TYPE DETERMINATION
   ├─ Code Write → pre_write_* hooks
   ├─ File System → pre_filesystem_write hooks  
   ├─ MCP Tool → pre_mcp_tool_use hooks
   └─ Command → pre_run_command hooks
   ↓
6. OPERATION EXECUTION
   ↓
7. post_* hooks (Verification, Audit, Observability)
   ↓
8. RESULT DELIVERY
```

### Configuration Reference

| Configuration | Location | Default | Impact | Security |
|---|---|---|---|---|
| Atlas Gate Enablement | `policy.json` | `true` | MCP security | Critical |
| Confidence Threshold | `policy.json` | `0.80` | Intent classification | Medium |
| Max Lines Per Edit | `policy.json` | `100` | Diff quality | Low |
| Forbidden Paths | `policy.json` | [`.ssh`, `.aws`, `/etc`] | File system security | High |
| Entropy Threshold | `policy.json` | `0.7` | Session health | Low |
| Kill Switch State | Runtime config | `false` | Command execution | High |
| Backup Retention | `deploy.sh` | 30 days | Recovery | Medium |

### Security Posture

#### Threat Model Summary

| Threat | Vector | Impact | Mitigation |
|---|---|---|---|
| Code Injection | User input, tool parameters | Critical | ATLAS Gate validation |
| Path Traversal | File operations | High | Forbidden path enforcement |
| Command Injection | Shell execution | Critical | Command blocklist/kill switch |
| Privilege Escalation | MCP tool misuse | Critical | Strict MCP allowlist |
| Data Exfiltration | File reads | Medium | Path restrictions, audit |
| Denial of Service | Resource exhaustion | Medium | Rate limiting, quotas |

#### Risk Register

| Risk | Probability | Impact | Mitigation Status |
|---|---|---|---|
| ATLAS Gate bypass | Low | Critical | Multiple validation layers |
| Policy misconfiguration | Medium | High | Policy validation, defaults |
| Hook failure | Medium | Medium | Fails-closed design |
| Audit trail loss | Low | Medium | Redundant logging |
| Unauthorized code execution | Low | Critical | Strict validation |

---

## Quick Answer: What Is This?

**For Enterprise Users:**

Production-grade system that ensures consistent, auditable, and reversible deployment of Windsurf IDE configurations and security enforcement mechanisms across enterprise environments.

**In Plain English:**

Imagine you keep a recipe book on your computer. Every time you update it, you want copies in three places: your kitchen, your office, and your backup drawer. This project automatically:

1. **Copies** your Windsurf configuration to three system locations
2. **Sets it up** automatically when you first clone this repository
3. **Keeps everything in sync** every time you pull updates
4. **Protects** the files with proper permissions so everything works correctly
5. **Enforces** security policies and compliance requirements

No manual copying, no forgotten updates, no permission errors, no security gaps.

**📋 For comprehensive enterprise documentation, see [README_ENTERPRISE.md](README_ENTERPRISE.md)**

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

**What it is:** Security enforcement and policy validation hooks that integrate with the Windsurf IDE runtime

**What it contains:** Python scripts that enforce enterprise security policies and validate operations

**Security Features:**
- Pre-execution validation of all operations
- Post-execution auditing and observability
- ATLAS Gate security framework integration
- Comprehensive policy enforcement
**Where it goes:**

- `/usr/local/share/windsurf-hooks` (system-wide access)
- `/root/.codeium/hooks` (Windsurf IDE access)

### Component 2: windsurf

**What it is:** Core configuration framework containing IDE settings, workflows, skills, and policy definitions

**What it contains:**
- Configuration files for IDE behavior and capabilities
- Workflow definitions and skill manifests
- Security policies and enforcement rules
- Global workflow templates and automation patterns
**Where it goes:** `/etc/windsurf` (system configuration)

**Security Impact:** Serves as authoritative configuration source for hook validation

### How They Work Together

```text
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
Security policies are enforced
         ↓
Everything is ready to use
```

**🔒 Security Architecture:**

- **windsurf/** defines what the system *should* do (configuration layer)
- **windsurf-hooks/** enforces what the system *can* do (security layer)
- All operations validated against enterprise policies
- Complete audit trail for compliance reporting

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
| Config files | 600 | `rw-------` - readable/writable by root only |
| Hook scripts | 700 | `rwx------` - executable by root only |

**Why these permissions?**
- Directories must be executable to enter them
- Config files must be readable by root only
- Hook scripts must be executable by root only
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
│  ├── pre_write_*          │ ├── global_workflows/  │
│  ├── post_write_*         │ ├── policy/            │
│  ├── pre_mcp_*            │ ├── rules/             │
│  ├── pre_run_*            │ ├── skills/            │
│  └── [security hooks]     │ └── [config files]     │
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

### Security Architecture

**Dual-Layer Security Model:**

- **Configuration Layer (windsurf/)**: Defines policies, workflows, and capabilities
- **Enforcement Layer (windsurf-hooks/)**: Validates and enforces security policies at runtime

**Key Security Features:**
- **Pre-execution validation**: All operations checked before execution
- **Post-execution auditing**: Complete audit trail for compliance
- **ATLAS Gate integration**: Advanced security framework
- **Policy enforcement**: Enterprise-grade security controls
- **Immutable audit trail**: Complete logging of all actions

**Trust Boundaries:**

- **Root-owned deployment**: Secure, controlled installation
- **Principle of least privilege**: Minimal required permissions
- **Comprehensive logging**: Full audit trail for security review
- **Automated backups**: Timestamped, reversible deployments

### Data Flow

```text
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
   ├─ Set ownership (root:root)
   └─ Verify success
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
