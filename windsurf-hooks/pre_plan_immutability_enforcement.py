#!/usr/bin/env python3
"""
Hook: pre_plan_immutability_enforcement

Enforces plan immutability. Plan must not be modified between execution steps.

Workflow:
  1. Before execution: Hash entire plan
  2. Store hash in session context
  3. Before each step: Verify hash unchanged
  4. Reject if modified

Plan hash is the source of truth for what Windsurf should execute.
"""

import sys
import json
import hashlib
import os
from datetime import datetime

PLAN_HASH_FILE = "/tmp/windsurf_plan_hash"
PLAN_CONTEXT_FILE = "/tmp/windsurf_plan_context"

def compute_plan_hash(plan_content):
    """Compute SHA256 hash of plan"""
    if isinstance(plan_content, dict):
        plan_content = json.dumps(plan_content, sort_keys=True)
    elif isinstance(plan_content, str):
        pass
    else:
        plan_content = str(plan_content)
    
    return hashlib.sha256(plan_content.encode()).hexdigest()

def get_stored_plan_hash():
    """Get previously stored plan hash"""
    if os.path.exists(PLAN_HASH_FILE):
        try:
            with open(PLAN_HASH_FILE, "r") as f:
                return f.read().strip()
        except:
            return None
    return None

def store_plan_hash(plan_hash, plan_content):
    """Store plan hash and context"""
    try:
        with open(PLAN_HASH_FILE, "w") as f:
            f.write(plan_hash)
        with open(PLAN_CONTEXT_FILE, "w") as f:
            f.write(json.dumps({"hash": plan_hash, "stored_at": datetime.now().isoformat()}))
    except Exception as e:
        audit_log_error(f"Failed to store plan hash: {e}")

def audit_log_error(message):
    """Log to audit trail"""
    try:
        with open("/tmp/windsurf_plan_audit.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] {message}\n")
    except:
        pass

def main():
    """
    Hook invocation.
    Receives: plan, step_index, intent
    """
    
    try:
        input_data = json.loads(sys.stdin.read()) if sys.stdin.isatty() == False else {}
    except:
        input_data = {}
    
    plan = input_data.get("plan")
    step_index = input_data.get("step_index", 0)
    action = input_data.get("action", "verify")  # "init" or "verify"
    
    if not plan:
        print(json.dumps({"status": "error", "reason": "No plan provided"}))
        sys.exit(1)
    
    current_plan_hash = compute_plan_hash(plan)
    
    if action == "init":
        # First execution: store hash
        stored_hash = get_stored_plan_hash()
        if stored_hash:
            audit_log_error(f"Plan hash already exists. Overwriting. Old: {stored_hash}, New: {current_plan_hash}")
        
        store_plan_hash(current_plan_hash, plan)
        print(json.dumps({
            "status": "allowed",
            "action": "plan_hash_initialized",
            "plan_hash": current_plan_hash,
            "step": step_index
        }))
        sys.exit(0)
    
    elif action == "verify":
        # Mid-execution: verify hash unchanged
        stored_hash = get_stored_plan_hash()
        
        if not stored_hash:
            audit_log_error(f"No stored plan hash found. Initialize plan first.")
            print(json.dumps({
                "status": "rejected",
                "reason": "Plan not initialized. Call with action=init first.",
                "step": step_index
            }))
            sys.exit(1)
        
        if current_plan_hash != stored_hash:
            audit_log_error(
                f"Plan hash mismatch at step {step_index}. "
                f"Expected: {stored_hash}, Got: {current_plan_hash}. REJECTING."
            )
            print(json.dumps({
                "status": "rejected",
                "reason": "Plan has been modified since execution started",
                "expected_hash": stored_hash,
                "current_hash": current_plan_hash,
                "step": step_index
            }))
            sys.exit(1)
        
        print(json.dumps({
            "status": "allowed",
            "plan_hash_verified": current_plan_hash,
            "step": step_index
        }))
        sys.exit(0)
    
    else:
        print(json.dumps({"status": "error", "reason": f"Unknown action: {action}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
