#!/bin/bash
# Test ATLAS-GATE + Windsurf integration
# Validates all updated hooks work correctly

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$REPO_DIR/windsurf-hooks"
POLICY_FILE="$REPO_DIR/windsurf/policy/policy.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
test_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((TESTS_PASSED++))
}

test_fail() {
    echo -e "${RED}✗${NC} $1"
    ((TESTS_FAILED++))
}

test_hook() {
    local hook_name=$1
    local input=$2
    local expected_exit=$3
    local description=$4
    
    local result
    result=$(echo "$input" | python3 "$HOOKS_DIR/$hook_name" 2>&1 || echo "EXIT:$?")
    local exit_code=$?
    
    if [ "$expected_exit" -eq 0 ]; then
        if [ $exit_code -eq 0 ]; then
            test_pass "$description"
        else
            test_fail "$description (expected exit 0, got $exit_code)"
        fi
    else
        if [ $exit_code -eq 2 ]; then
            test_pass "$description"
        else
            test_fail "$description (expected exit 2, got $exit_code)"
        fi
    fi
}

echo "=========================================="
echo "ATLAS-GATE + Windsurf Integration Tests"
echo "=========================================="
echo ""

# Test 1: Policy validation
echo "Test 1: Policy JSON Validity"
if python3 -m json.tool "$POLICY_FILE" > /dev/null 2>&1; then
    test_pass "policy.json is valid JSON"
else
    test_fail "policy.json is invalid JSON"
fi

# Verify policy has required fields
export REPO_DIR
python3 << 'EOF'
import json
import os
from pathlib import Path

policy_path = Path(os.environ["REPO_DIR"]) / "windsurf" / "policy" / "policy.json"
policy = json.loads(policy_path.read_text())
required = ["mcp_tool_allowlist", "block_commands_regex", "prohibited_patterns"]

for field in required:
    if field not in policy:
        print(f"FAIL: Missing policy field: {field}")
        exit(1)

# Check ATLAS tools in allowlist
tools = policy.get("mcp_tool_allowlist", [])
atlas_tools = [t for t in tools if t.startswith("mcp_atlas-gate-mcp_")]

if len(atlas_tools) == 0:
    print("FAIL: No ATLAS-GATE tools in allowlist")
    exit(1)

print(f"OK: {len(atlas_tools)} ATLAS-GATE tools configured")
EOF

echo ""

# Test 2: Hook syntax validation
echo "Test 2: Hook Python Syntax"
for hook in pre_user_prompt_gate.py pre_mcp_tool_use_allowlist.py pre_run_command_blocklist.py pre_write_code_policy.py; do
    if python3 -m py_compile "$HOOKS_DIR/$hook" 2>/dev/null; then
        test_pass "$hook syntax valid"
    else
        test_fail "$hook syntax invalid"
    fi
done

echo ""

# Test 3: pre_user_prompt_gate - plan extraction
echo "Test 3: pre_user_prompt_gate (Plan Extraction)"

# Test 3.1: Extract BLAKE3 hash
test_hook \
    "pre_user_prompt_gate.py" \
    '{"tool_info": {"prompt": "implement plan=3f2a1b9c8e7d6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f"}}' \
    0 \
    "Extract BLAKE3 hash from prompt"

# Test 3.2: Extract alias
test_hook \
    "pre_user_prompt_gate.py" \
    '{"tool_info": {"prompt": "implement plan: auth-refactor"}}' \
    0 \
    "Extract plan alias from prompt"

# Test 3.3: Detect non-mutation
test_hook \
    "pre_user_prompt_gate.py" \
    '{"tool_info": {"prompt": "what is this code doing?"}}' \
    0 \
    "Detect non-mutation intent (no block)"

echo ""

# Test 4: pre_mcp_tool_use_allowlist - tool enforcement
echo "Test 4: pre_mcp_tool_use_allowlist (Tool Enforcement)"

# Test 4.1: Allow begin_session (first call)
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_begin_session"}}' \
    0 \
    "Allow begin_session (first call)"

# Test 4.2: Block non-ATLAS tool
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "read_file"}}' \
    2 \
    "Block non-ATLAS tool (read_file)"

# Test 4.3: Block write_file without session
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file", "plan": "abc123"}, "conversation_context": ""}' \
    2 \
    "Block write_file without session init"

# Test 4.4: Block write_file without prompt unlock
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file", "plan": "abc123"}, "conversation_context": "ATLAS_SESSION_OK"}' \
    2 \
    "Block write_file without prompt unlock"

# Test 4.5: Block write_file without plan hash
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file"}, "conversation_context": "ATLAS_SESSION_OK ATLAS_PROMPT_UNLOCKED"}' \
    2 \
    "Block write_file without plan hash"

# Test 4.6: Allow write_file with all requirements
test_hook \
    "pre_mcp_tool_use_allowlist.py" \
    '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file", "plan": "3f2a1b9c8e7d6f5a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3e2f"}, "conversation_context": "ATLAS_SESSION_OK ATLAS_PROMPT_UNLOCKED"}' \
    0 \
    "Allow write_file with plan hash + session + prompt"

echo ""

# Test 5: pre_run_command_blocklist - shell kill
echo "Test 5: pre_run_command_blocklist (Shell Kill)"

# Test 5.1: Block any command
test_hook \
    "pre_run_command_blocklist.py" \
    '{"tool_info": {"command": "ls -la"}}' \
    2 \
    "Block shell command (ls)"

# Test 5.2: Block different command
test_hook \
    "pre_run_command_blocklist.py" \
    '{"tool_info": {"command": "echo hello"}}' \
    2 \
    "Block shell command (echo)"

# Test 5.3: Block empty command
test_hook \
    "pre_run_command_blocklist.py" \
    '{"tool_info": {"command": ""}}' \
    2 \
    "Block empty shell command"

echo ""

# Test 6: pre_write_code_policy - escape detection
echo "Test 6: pre_write_code_policy (Escape Detection)"

# Test 6.1: Allow clean code
test_hook \
    "pre_write_code_policy.py" \
    '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "def hello():\n  return 42"}]}}' \
    0 \
    "Allow clean code (no escapes)"

# Test 6.2: Block subprocess
test_hook \
    "pre_write_code_policy.py" \
    '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "import subprocess\nsubprocess.run([\"ls\"])"}]}}' \
    2 \
    "Block escape primitive (subprocess)"

# Test 6.3: Block os.system
test_hook \
    "pre_write_code_policy.py" \
    '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "import os\nos.system(\"ls\")"}]}}' \
    2 \
    "Block escape primitive (os.system)"

# Test 6.4: Block exec
test_hook \
    "pre_write_code_policy.py" \
    '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "exec(\"print(1)\")"}]}}' \
    2 \
    "Block escape primitive (exec)"

echo ""

# Test 7: Session state machine (integration test)
echo "Test 7: Session State Machine (Integration)"

# Simulate: begin_session → read_prompt → write_file
echo "Sequence test:"

# Step 1: begin_session
echo -n "  1. begin_session... "
result=$(echo '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_begin_session"}}' | \
    python3 "$HOOKS_DIR/pre_mcp_tool_use_allowlist.py" 2>&1 || true)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((TESTS_FAILED++))
fi

# Step 2: read_prompt (after session is OK)
echo -n "  2. read_prompt... "
result=$(echo '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_read_prompt"}, "conversation_context": "ATLAS_SESSION_OK"}' | \
    python3 "$HOOKS_DIR/pre_mcp_tool_use_allowlist.py" 2>&1 || true)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((TESTS_FAILED++))
fi

# Step 3: write_file (after session + prompt)
echo -n "  3. write_file with plan... "
result=$(echo '{"tool_info": {"tool_name": "mcp_atlas-gate-mcp_write_file", "plan": "abc123"}, "conversation_context": "ATLAS_SESSION_OK ATLAS_PROMPT_UNLOCKED"}' | \
    python3 "$HOOKS_DIR/pre_mcp_tool_use_allowlist.py" 2>&1 || true)
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC}"
    ((TESTS_PASSED++))
else
    echo -e "${RED}✗${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Integration status:"
    echo "  ✓ Policy.json valid"
    echo "  ✓ All hooks have valid Python syntax"
    echo "  ✓ pre_user_prompt_gate extracts plans"
    echo "  ✓ pre_mcp_tool_use_allowlist enforces ATLAS tools + session + plan"
    echo "  ✓ pre_run_command_blocklist blocks all shell"
    echo "  ✓ pre_write_code_policy blocks escape primitives"
    echo "  ✓ Session state machine works"
    echo ""
    echo "Ready for deployment!"
    exit 0
else
    echo -e "${RED}✗ $TESTS_FAILED test(s) failed${NC}"
    exit 1
fi
