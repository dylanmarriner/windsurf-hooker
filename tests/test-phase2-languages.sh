#!/bin/bash
# Test suite for Phase 2 multi-language support (Java, C/C++, Go, Rust)

set -e

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../windsurf-hooks" && pwd)"
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

test_count=0
pass_count=0
fail_count=0

test_hook() {
    local hook_name="$1"
    local language="$2"
    local code_file="$3"
    local should_block="$4"
    
    test_count=$((test_count + 1))
    
    local hook_path="${HOOKS_DIR}/${hook_name}.py"
    if [[ ! -f "$hook_path" ]]; then
        echo -e "${RED}✗${NC} Test $test_count: Hook not found at $hook_path"
        fail_count=$((fail_count + 1))
        return 1
    fi
    
    # Create payload with Python (safer JSON encoding)
    local payload=$(python3 << PYSCRIPT
import json
code = open('$code_file', 'r').read()
payload = {
    'tool_info': {
        'edits': [
            {
                'path': 'code.$language',
                'new_string': code
            }
        ]
    }
}
print(json.dumps(payload))
PYSCRIPT
)
    
    # Run hook
    local result=0
    echo "$payload" | python3 "$hook_path" 2>/dev/null || result=$?
    
    # Check result
    if [[ "$should_block" == "true" ]]; then
        if [[ $result -eq 2 ]]; then
            echo -e "${GREEN}✓${NC} Test $test_count: $hook_name correctly blocked $language code"
            pass_count=$((pass_count + 1))
            return 0
        else
            echo -e "${RED}✗${NC} Test $test_count: $hook_name should have blocked $language code (got exit $result)"
            fail_count=$((fail_count + 1))
            return 1
        fi
    else
        if [[ $result -eq 0 ]]; then
            echo -e "${GREEN}✓${NC} Test $test_count: $hook_name correctly allowed $language code"
            pass_count=$((pass_count + 1))
            return 0
        else
            echo -e "${RED}✗${NC} Test $test_count: $hook_name should have allowed $language code (got exit $result)"
            fail_count=$((fail_count + 1))
            return 1
        fi
    fi
}

# Create test files

# Java - bad (TODO comment)
cat > /tmp/java_todo.java <<'EOF'
public class MyClass {
    // TODO: implement this properly
    public void doSomething() {
        System.out.println("incomplete");
    }
}
EOF

# Java - good
cat > /tmp/java_good.java <<'EOF'
public class MyClass {
    /**
     * Performs an operation on the system.
     * This method handles the core business logic.
     */
    public void doSomething() {
        System.out.println("complete");
    }
}
EOF

# Java - bad (missing docstring)
cat > /tmp/java_nodoc.java <<'EOF'
public class MyClass {
    public void doSomething() {
        System.out.println("missing docstring");
        String result = processData();
        return result;
    }
}
EOF

# C++ - bad (NotImplementedError)
cat > /tmp/cpp_stub.cpp <<'EOF'
#include <stdexcept>

void processData() {
    throw std::runtime_error("not implemented yet");
}
EOF

# C++ - good
cat > /tmp/cpp_good.cpp <<'EOF'
#include <iostream>

/**
 * Processes the incoming data stream.
 * Validates input and applies transformations.
 */
void processData() {
    std::cout << "Processing data" << std::endl;
}
EOF

# Go - bad (panic with TODO)
cat > /tmp/go_panic.go <<'EOF'
package main

func ProcessData() {
    panic("TODO: implement data processing")
}
EOF

# Go - good
cat > /tmp/go_good.go <<'EOF'
package main

// ProcessData handles the incoming data stream.
// It validates input and applies transformations according to spec.
func ProcessData() {
    println("Processing data")
}
EOF

# Rust - bad (unimplemented!)
cat > /tmp/rust_stub.rs <<'EOF'
fn process_data() {
    unimplemented!()
}
EOF

# Rust - good
cat > /tmp/rust_good.rs <<'EOF'
/// Processes the incoming data stream.
/// 
/// This function validates input and applies transformations
/// according to the specification.
fn process_data() {
    println!("Processing data");
}
EOF

echo "=== Phase 2 Language Support Tests ==="
echo ""

echo "--- Completeness Hook Tests (pre_write_completeness.py) ---"
test_hook "pre_write_completeness" "java" "/tmp/java_todo.java" "true"
test_hook "pre_write_completeness" "java" "/tmp/java_good.java" "false"
test_hook "pre_write_completeness" "cpp" "/tmp/cpp_stub.cpp" "true"
test_hook "pre_write_completeness" "cpp" "/tmp/cpp_good.cpp" "false"
test_hook "pre_write_completeness" "go" "/tmp/go_panic.go" "true"
test_hook "pre_write_completeness" "go" "/tmp/go_good.go" "false"
test_hook "pre_write_completeness" "rs" "/tmp/rust_stub.rs" "true"
test_hook "pre_write_completeness" "rs" "/tmp/rust_good.rs" "false"

echo ""
echo "--- Comprehensive Comments Hook Tests (pre_write_comprehensive_comments.py) ---"
test_hook "pre_write_comprehensive_comments" "java" "/tmp/java_nodoc.java" "true"
test_hook "pre_write_comprehensive_comments" "java" "/tmp/java_good.java" "false"
test_hook "pre_write_comprehensive_comments" "cpp" "/tmp/cpp_good.cpp" "false"
test_hook "pre_write_comprehensive_comments" "go" "/tmp/go_good.go" "false"
test_hook "pre_write_comprehensive_comments" "rs" "/tmp/rust_good.rs" "false"

echo ""
echo "=== Test Summary ==="
echo -e "Total: $test_count | ${GREEN}Passed: $pass_count${NC} | ${RED}Failed: $fail_count${NC}"

if [[ $fail_count -eq 0 ]]; then
    exit 0
else
    exit 1
fi
