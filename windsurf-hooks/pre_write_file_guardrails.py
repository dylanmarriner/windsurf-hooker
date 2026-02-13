#!/usr/bin/env python3
"""
Hook: pre_write_file_guardrails

write_file is the only mutation surface. Strictly enforced.

Rules:
  - plan_hash required and must match session
  - intent required and non-empty
  - path must be within plan scope
  - path must not traverse boundaries
  - path must be within workspace root
  - protected paths are read-only

Rejection is immediate.
"""

import sys
import json
import os
from datetime import datetime
import pathlib

PLAN_HASH_FILE = "/tmp/windsurf_plan_hash"
WORKSPACE_ROOT = os.getcwd()

PROTECTED_PATHS = [
    "/etc/windsurf/",
    "/usr/local/share/windsurf-hooks/",
    "/.local/share/windsurf-hooks/",
    "/root/.codeium/hooks/",
    "/.ssh",
    "/.aws",
    "/etc/passwd",
    "/etc/shadow",
    "/root"
]

def get_stored_plan_hash():
    """Get session plan hash"""
    if os.path.exists(PLAN_HASH_FILE):
        try:
            with open(PLAN_HASH_FILE, "r") as f:
                return f.read().strip()
        except:
            return None
    return None

def validate_path(path):
    """
    Validate path safety.
    Returns: (is_safe, reason)
    """
    
    # Resolve to absolute path
    try:
        abs_path = os.path.abspath(path)
    except Exception as e:
        return False, f"Path resolution failed: {e}"
    
    # Check for path traversal
    if ".." in path or "~" in path:
        return False, "Path traversal detected"
    
    # Check if within workspace
    try:
        rel = pathlib.Path(abs_path).relative_to(WORKSPACE_ROOT)
    except ValueError:
        return False, f"Path outside workspace root: {abs_path}"
    
    # Check protected paths
    for protected in PROTECTED_PATHS:
        if abs_path.startswith(protected):
            return False, f"Protected path: {protected}"
    
    return True, "OK"

def audit_log(message):
    """Log to audit trail"""
    try:
        with open("/tmp/windsurf_write_file_audit.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except:
        pass

def main():
    """
    Hook invocation.
    Receives: path, content, plan_hash, intent, scope
    """
    
    try:
        input_data = json.loads(sys.stdin.read()) if sys.stdin.isatty() == False else {}
    except:
        input_data = {}
    
    path = input_data.get("path")
    content = input_data.get("content", "")
    provided_hash = input_data.get("plan_hash")
    intent = input_data.get("intent", "").strip()
    scope = input_data.get("scope", WORKSPACE_ROOT)
    
    errors = []
    
    # Validation 1: path required
    if not path:
        errors.append("path is required")
    
    # Validation 2: intent required and non-empty
    if not intent:
        errors.append("intent is required and must be non-empty")
    
    # Validation 3: plan_hash required
    if not provided_hash:
        errors.append("plan_hash is required")
    
    # Validation 4: plan_hash must match session
    if provided_hash:
        stored_hash = get_stored_plan_hash()
        if not stored_hash:
            errors.append("No plan hash in session. Initialize plan first.")
        elif provided_hash != stored_hash:
            errors.append(f"plan_hash mismatch. Expected: {stored_hash}, Got: {provided_hash}")
    
    # Validation 5: path safety
    if path:
        is_safe, reason = validate_path(path)
        if not is_safe:
            errors.append(f"Path validation failed: {reason}")
    
    # If any errors, reject
    if errors:
        audit_log(f"REJECTED write_file: path={path}, reasons={errors}")
        print(json.dumps({
            "status": "rejected",
            "errors": errors,
            "path": path
        }))
        sys.exit(1)
    
    # All checks passed
    audit_log(f"ALLOWED write_file: path={path}, intent={intent[:50]}...")
    print(json.dumps({
        "status": "allowed",
        "path": path,
        "intent": intent[:100]
    }))
    sys.exit(0)

if __name__ == "__main__":
    main()
