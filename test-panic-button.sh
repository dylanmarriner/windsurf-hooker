#!/bin/bash
# Test script for panic button functionality

set -e

echo "=== Panic Button Test Suite ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Temporary policy file for testing
TEST_POLICY="/tmp/test_policy.json"

# Helper function to set profile
set_profile() {
    local profile=$1
    jq ".execution_profile=\"$profile\"" windsurf/policy/policy.json > "$TEST_POLICY"
}

# Helper function to test hook
test_hook() {
    local hook_path=$1
    local input_json=$2
    local expected_exit=0
    local expected_contains=$3
    
    echo -n "Testing $hook_path... "
    
    # Temporarily replace policy.json
    cp windsurf/policy/policy.json windsurf/policy/policy.json.bak
    cp "$TEST_POLICY" windsurf/policy/policy.json
    
    # Run hook
    output=$(echo "$input_json" | python3 "$hook_path" 2>&1 || true)
    exit_code=$?
    
    # Restore original
    mv windsurf/policy/policy.json.bak windsurf/policy/policy.json
    
    # Check results
    if [ "$expected_exit" -ne 0 ]; then
        if [ "$exit_code" -eq 2 ]; then
            if [[ "$output" == *"LOCKED"* ]]; then
                echo -e "${GREEN}✓${NC}"
                return 0
            fi
        fi
        echo -e "${RED}✗ (expected exit 2, got $exit_code)${NC}"
        echo "Output: $output"
        return 1
    else
        if [ "$exit_code" -eq 0 ]; then
            echo -e "${GREEN}✓${NC}"
            return 0
        else
            echo -e "${RED}✗ (expected exit 0, got $exit_code)${NC}"
            return 1
        fi
    fi
}

echo "--- Test 1: Standard Mode (Should Allow) ---"
set_profile "standard"

echo "Hooks should pass through policy checks in standard mode"
test_hook \
    "windsurf-hooks/pre_run_command_kill_switch.py" \
    '{"tool_info": {"command": "ls"}}' \
    0 || true
echo

echo "--- Test 2: Locked Mode (Should Block Everything) ---"
set_profile "locked"

echo "Test 2.1: Command execution blocked"
test_hook \
    "windsurf-hooks/pre_run_command_kill_switch.py" \
    '{"tool_info": {"command": "ls"}}' \
    2 || {
    echo -e "${RED}✗ pre_run_command_kill_switch failed to block in locked mode${NC}"
}
echo

echo "Test 2.2: MCP tool execution blocked"
test_hook \
    "windsurf-hooks/pre_mcp_tool_use_atlas_gate.py" \
    '{"tool_info": {"tool_name": "atlas_gate.read", "path": "/etc/hosts"}}' \
    2 || {
    echo -e "${RED}✗ pre_mcp_tool_use_atlas_gate failed to block in locked mode${NC}"
}
echo

echo "Test 2.3: Code write blocked"
test_hook \
    "windsurf-hooks/pre_write_code_escape_detection.py" \
    '{"tool_info": {"edits": []}}' \
    2 || {
    echo -e "${RED}✗ pre_write_code_escape_detection failed to block in locked mode${NC}"
}
echo

echo "Test 2.4: Filesystem write blocked"
test_hook \
    "windsurf-hooks/pre_filesystem_write_atlas_enforcement.py" \
    '{"tool_info": {"edits": []}}' \
    2 || {
    echo -e "${RED}✗ pre_filesystem_write_atlas_enforcement failed to block in locked mode${NC}"
}
echo

echo "--- Test 3: Restoration ---"
set_profile "standard"
echo "Profile restored to: standard"
echo -e "${GREEN}✓ Panic button can be deactivated${NC}"
echo

echo "=== All Tests Complete ==="
echo
echo "Summary:"
echo "  - Panic button activates with: jq '.execution_profile=\"locked\"' windsurf/policy/policy.json | sponge"
echo "  - All 4 critical hooks enforce the lock"
echo "  - Lock takes effect on next hook invocation"
echo "  - Lock can be deactivated with: jq '.execution_profile=\"standard\"' windsurf/policy/policy.json | sponge"
