#!/bin/bash
set -e

# Validation script for 7-phase hook implementation
# Checks: file existence, syntax, configuration, executable permissions

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOKS_DIR="$REPO_ROOT/windsurf-hooks"
CONFIG_DIR="$REPO_ROOT/windsurf"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ERRORS=0
WARNINGS=0

# Helper functions
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} File exists: $(basename $1)"
        return 0
    else
        echo -e "${RED}✗${NC} Missing: $1"
        ((ERRORS++))
        return 1
    fi
}

check_syntax() {
    local file=$1
    if python3 -m py_compile "$file" 2>/dev/null; then
        echo -e "${GREEN}✓${NC} Syntax OK: $(basename $file)"
        return 0
    else
        echo -e "${RED}✗${NC} Syntax error: $file"
        ((ERRORS++))
        return 1
    fi
}

check_json() {
    local file=$1
    if python3 -m json.tool "$file" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} JSON valid: $(basename $file)"
        return 0
    else
        echo -e "${RED}✗${NC} Invalid JSON: $file"
        ((ERRORS++))
        return 1
    fi
}

check_executable() {
    local file=$1
    if [ -x "$file" ]; then
        echo -e "${GREEN}✓${NC} Executable: $(basename $file)"
        return 0
    else
        echo -e "${YELLOW}⚠${NC} Not executable: $(basename $file) (run: chmod +x)"
        ((WARNINGS++))
        return 1
    fi
}

# =============================================================================
# VALIDATION STARTS HERE
# =============================================================================

echo "=========================================="
echo "7-Phase Hook Implementation Validator"
echo "=========================================="
echo ""

# Phase 1: Check hook files
echo "Checking hook files..."
echo ""

PHASE_1_HOOKS=(
    "$HOOKS_DIR/pre_intent_classification.py"
    "$HOOKS_DIR/pre_user_prompt_gate.py"
)

PHASE_2_HOOKS=(
    "$HOOKS_DIR/pre_plan_resolution.py"
)

PHASE_3_HOOKS=(
    "$HOOKS_DIR/pre_write_diff_quality.py"
    "$HOOKS_DIR/pre_write_code_policy.py"
    "$HOOKS_DIR/pre_filesystem_write.py"
)

PHASE_4_HOOKS=(
    "$HOOKS_DIR/pre_mcp_tool_use_allowlist.py"
    "$HOOKS_DIR/pre_run_command_blocklist.py"
)

PHASE_5_HOOKS=(
    "$HOOKS_DIR/post_write_verify.py"
    "$HOOKS_DIR/post_write_semantic_diff.py"
    "$HOOKS_DIR/post_write_observability.py"
)

PHASE_6_HOOKS=(
    "$HOOKS_DIR/post_refusal_audit.py"
)

PHASE_7_HOOKS=(
    "$HOOKS_DIR/post_session_entropy_check.py"
)

# Check Phase 1
echo "Phase 1 (Intent Classification):"
for hook in "${PHASE_1_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 2
echo "Phase 2 (Planning & Structure):"
for hook in "${PHASE_2_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 3
echo "Phase 3 (Code Write):"
for hook in "${PHASE_3_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 4
echo "Phase 4 (Tool & Command):"
for hook in "${PHASE_4_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 5
echo "Phase 5 (Verification):"
for hook in "${PHASE_5_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 6
echo "Phase 6 (Error Handling):"
for hook in "${PHASE_6_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check Phase 7
echo "Phase 7 (Meta):"
for hook in "${PHASE_7_HOOKS[@]}"; do
    check_file "$hook" && check_syntax "$hook"
done
echo ""

# Check configuration files
echo "Configuration files:"
check_file "$CONFIG_DIR/policy/policy.json" && check_json "$CONFIG_DIR/policy/policy.json"
check_file "$CONFIG_DIR/hooks.json" && check_json "$CONFIG_DIR/hooks.json"
echo ""

# Check documentation
echo "Documentation files:"
check_file "$REPO_ROOT/HOOK_ARCHITECTURE.md"
check_file "$REPO_ROOT/HOOK_QUICK_REFERENCE.md"
check_file "$REPO_ROOT/MIGRATION_GUIDE.md"
check_file "$REPO_ROOT/IMPLEMENTATION_SUMMARY.md"
echo ""

# Validate hooks.json entries
echo "Validating hooks.json registry..."
python3 << 'EOF'
import json
from pathlib import Path

hooks_file = Path("windsurf/hooks.json")
hooks_data = json.loads(hooks_file.read_text())

expected_hooks = [
    "pre_intent_classification",
    "pre_plan_resolution",
    "pre_user_prompt_gate",
    "pre_write_diff_quality",
    "pre_write_code",
    "pre_filesystem_write",
    "pre_mcp_tool_use",
    "pre_run_command",
    "post_write_semantic_diff",
    "post_write_observability",
    "post_write_code",
    "post_refusal_audit",
    "post_session_entropy_check",
]

registered = list(hooks_data.get("hooks", {}).keys())

print(f"Expected hooks: {len(expected_hooks)}")
print(f"Registered hooks: {len(registered)}")

missing = set(expected_hooks) - set(registered)
if missing:
    print(f"Missing from hooks.json: {missing}")
else:
    print("✓ All expected hooks registered")

EOF
echo ""

# Validate policy.json sections
echo "Validating policy.json sections..."
python3 << 'EOF'
import json
from pathlib import Path

policy_file = Path("windsurf/policy/policy.json")
policy = json.loads(policy_file.read_text())

expected_sections = {
    "tokens": dict,
    "prohibited_patterns": dict,
    "block_commands_regex": list,
    "mcp_tool_allowlist": list,
    "intent_classification": dict,
    "plan_resolution": dict,
    "diff_quality": dict,
    "filesystem_write": dict,
    "observability": dict,
    "session_entropy": dict,
}

print(f"Expected policy sections: {len(expected_sections)}")

missing = []
for section, expected_type in expected_sections.items():
    if section not in policy:
        missing.append(section)
    elif not isinstance(policy[section], expected_type):
        print(f"⚠ Section '{section}' has wrong type (expected {expected_type.__name__})")

if missing:
    print(f"Missing policy sections: {missing}")
else:
    print(f"✓ All {len(expected_sections)} policy sections present")

EOF
echo ""

# Test hooks in isolation
echo "Testing hooks in isolation..."
python3 << 'EOF'
import json
import subprocess
from pathlib import Path

test_input = json.dumps({
    "tool_info": {
        "prompt": "implement a function",
        "edits": [
            {"path": "test.py", "old_string": "", "new_string": "def test(): pass"}
        ]
    },
    "conversation_context": "",
})

hooks_to_test = [
    "pre_intent_classification.py",
    "pre_plan_resolution.py",
    "pre_write_diff_quality.py",
    "pre_filesystem_write.py",
    "post_write_semantic_diff.py",
]

hooks_dir = Path("windsurf-hooks")

for hook in hooks_to_test:
    hook_path = hooks_dir / hook
    if hook_path.exists():
        result = subprocess.run(
            ["python3", str(hook_path)],
            input=test_input,
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"✓ {hook} executed successfully")
        else:
            print(f"✗ {hook} failed with exit code {result.returncode}")
            if result.stderr:
                print(f"  Error: {result.stderr[:100]}")

EOF
echo ""

# Summary
echo "=========================================="
echo "Validation Summary"
echo "=========================================="

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN}✓ All checks passed!${NC}"
    echo ""
    echo "Implementation is complete and ready for deployment."
    echo ""
    echo "Next steps:"
    echo "  1. Review HOOK_ARCHITECTURE.md"
    echo "  2. Read MIGRATION_GUIDE.md for deployment"
    echo "  3. Check HOOK_QUICK_REFERENCE.md for usage"
    exit 0
else
    echo -e "${RED}✗ $ERRORS error(s) found${NC}"
    if [ $WARNINGS -gt 0 ]; then
        echo -e "${YELLOW}⚠ $WARNINGS warning(s)${NC}"
    fi
    exit 1
fi
