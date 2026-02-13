#!/usr/bin/env python3
"""
Hook: pre_session_state_enforcement

Enforces session state machine. No tool invocation allowed before begin_session.

States:
  INIT   → allow begin_session only
  ACTIVE → allow execution tools
  CLOSED → block all

Rejection is immediate and final.
"""

import sys
import json
import os
from datetime import datetime

STATE_FILE = "/tmp/windsurf_session_state"

def get_session_state():
    """Get current session state. Default: INIT"""
    if not os.path.exists(STATE_FILE):
        return "INIT"
    try:
        with open(STATE_FILE, "r") as f:
            return f.read().strip()
    except:
        return "INIT"

def set_session_state(state):
    """Persist session state"""
    try:
        with open(STATE_FILE, "w") as f:
            f.write(state)
    except Exception as e:
        audit_log_error(f"Failed to persist session state: {e}")

def audit_log_error(message):
    """Log error to audit trail"""
    try:
        with open("/tmp/windsurf_session_audit.log", "a") as f:
            f.write(f"[{datetime.now().isoformat()}] ERROR: {message}\n")
    except:
        pass

def main():
    """
    Hook invocation point.
    Receives: plan context, intent, tool name
    """
    
    try:
        # Parse input from stdin (hook invocation)
        input_data = json.loads(sys.stdin.read()) if sys.stdin.isatty() == False else {}
    except:
        input_data = {}
    
    tool_name = input_data.get("tool_name", "unknown")
    state = get_session_state()
    
    # State machine enforcement
    if state == "INIT":
        # Only begin_session allowed
        if tool_name != "begin_session":
            audit_log_error(f"Tool invocation in INIT state: {tool_name}. REJECTED.")
            print(json.dumps({
                "status": "rejected",
                "reason": "Session not initialized. Call begin_session first.",
                "state": state,
                "requested_tool": tool_name
            }))
            sys.exit(1)
        else:
            # Transition to ACTIVE
            set_session_state("ACTIVE")
            print(json.dumps({"status": "allowed", "new_state": "ACTIVE"}))
            sys.exit(0)
    
    elif state == "ACTIVE":
        # Execution tools allowed
        allowed_tools = {
            "begin_session", "end_session",
            "list_plans", "read_plan", "lint_plan", "bootstrap_create_foundation_plan",
            "read_prompt", "read_file", "write_file", "read_audit_log",
            "replay_execution", "verify_workspace_integrity",
            "generate_attestation_bundle", "verify_attestation_bundle",
            "export_attestation_bundle"
        }
        
        if tool_name == "end_session":
            set_session_state("CLOSED")
            print(json.dumps({"status": "allowed", "new_state": "CLOSED"}))
            sys.exit(0)
        elif tool_name in allowed_tools:
            print(json.dumps({"status": "allowed"}))
            sys.exit(0)
        else:
            audit_log_error(f"Disallowed tool in ACTIVE state: {tool_name}")
            print(json.dumps({
                "status": "rejected",
                "reason": f"Tool not in execution whitelist: {tool_name}",
                "state": state
            }))
            sys.exit(1)
    
    elif state == "CLOSED":
        # No tools allowed
        audit_log_error(f"Tool invocation in CLOSED state: {tool_name}. REJECTED.")
        print(json.dumps({
            "status": "rejected",
            "reason": "Session closed. No further operations allowed.",
            "state": state
        }))
        sys.exit(1)
    
    else:
        audit_log_error(f"Unknown session state: {state}")
        print(json.dumps({
            "status": "error",
            "reason": f"Unknown session state: {state}"
        }))
        sys.exit(1)

if __name__ == "__main__":
    main()
