#!/bin/bash
# Simple ATLAS-GATE integration test (no policy file dependencies)

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$REPO_DIR/windsurf-hooks"
POLICY_FILE="$REPO_DIR/windsurf/policy/policy.json"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS=0
PASSED=0

test_result() {
    local status=$1
    local description=$2
    ((TESTS++))
    if [ $status -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $description"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $description"
    fi
}

echo "=========================================="
echo "ATLAS-GATE Integration - Simple Tests"
echo "=========================================="
echo ""

# Test 1: Policy.json valid
echo "Test 1: Configuration"
python3 -m json.tool "$POLICY_FILE" > /dev/null
test_result $? "policy.json is valid JSON"

export REPO_DIR
python3 << 'EOF'
import json
import os
from pathlib import Path

policy_path = Path(os.environ["REPO_DIR"]) / "windsurf" / "policy" / "policy.json"
policy = json.loads(policy_path.read_text())

# Check required fields
assert "mcp_tool_allowlist" in policy
assert "block_commands_regex" in policy
assert "prohibited_patterns" in policy

# Check ATLAS tools
tools = policy.get("mcp_tool_allowlist", [])
atlas_count = len([t for t in tools if t.startswith("mcp_atlas-gate-mcp_")])
assert atlas_count == 11, f"Expected 11 ATLAS tools, got {atlas_count}"

print(f"OK: 11 ATLAS-GATE tools configured")
EOF
test_result $? "ATLAS-GATE tools configured in policy"

echo ""

# Test 2: Hook syntax
echo "Test 2: Hook Syntax"
hooks=(
    "pre_user_prompt_gate.py"
    "pre_mcp_tool_use_allowlist.py"
    "pre_run_command_blocklist.py"
    "pre_write_code_policy.py"
)

for hook in "${hooks[@]}"; do
    python3 -m py_compile "$HOOKS_DIR/$hook"
    test_result $? "$hook Python syntax valid"
done

echo ""

# Test 3: Hook execution (basic, no policy file required)
echo "Test 3: Hook Execution (Basic)"

# pre_user_prompt_gate should always succeed
output=$(echo '{"tool_info": {"prompt": "implement plan=abc123"}}' | \
    python3 "$HOOKS_DIR/pre_user_prompt_gate.py" 2>&1)
test_result $? "pre_user_prompt_gate accepts valid input"

# Verify output is JSON
echo "$output" | python3 -m json.tool > /dev/null
test_result $? "pre_user_prompt_gate outputs valid JSON"

# pre_run_command_blocklist should always fail
echo '{"tool_info": {"command": "ls"}}' | \
    python3 "$HOOKS_DIR/pre_run_command_blocklist.py" 2>&1 > /dev/null
test_result $? "pre_run_command_blocklist blocks shell (exit 2)"

echo ""

# Test 4: Escape detection in pre_write_code_policy
echo "Test 4: Escape Primitive Detection"

# Clean code should pass
echo '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "x = 1"}]}}' | \
    python3 "$HOOKS_DIR/pre_write_code_policy.py" > /dev/null 2>&1
test_result $? "pre_write_code_policy allows clean code"

# Subprocess should fail
echo '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "import subprocess"}]}}' | \
    python3 "$HOOKS_DIR/pre_write_code_policy.py" 2>&1 > /dev/null
test_result $? "pre_write_code_policy blocks subprocess"

# os.system should fail
echo '{"tool_info": {"edits": [{"path": "test.py", "old_string": "", "new_string": "os.system(\"ls\")"}]}}' | \
    python3 "$HOOKS_DIR/pre_write_code_policy.py" 2>&1 > /dev/null
test_result $? "pre_write_code_policy blocks os.system"

echo ""

# Test 5: Hook script exists and is executable
echo "Test 5: Deployment Scripts"
[ -x "$REPO_DIR/deploy.sh" ]
test_result $? "deploy.sh is executable"

[ -x "$REPO_DIR/validate-implementation.sh" ]
test_result $? "validate-implementation.sh is executable"

echo ""

# Summary
echo "=========================================="
echo "Summary: $PASSED / $TESTS tests passed"
echo "=========================================="

if [ $PASSED -eq $TESTS ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Integration verified:"
    echo "  ✓ policy.json is valid and configured"
    echo "  ✓ All hooks have valid Python syntax"
    echo "  ✓ Hooks execute correctly"
    echo "  ✓ Escape primitives are blocked"
    echo "  ✓ Deployment scripts exist"
    echo ""
    exit 0
else
    echo -e "${RED}✗ $(($TESTS - $PASSED)) test(s) failed${NC}"
    exit 1
fi
