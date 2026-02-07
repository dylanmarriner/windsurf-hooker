# Phase 2: Multi-Language Enforcement Quick Start

**TL;DR**: Java, C/C++, Go, and Rust are now fully supported with completeness and documentation enforcement.

## What's Supported

### Completeness Checks
All Phase 2 languages block:
- `TODO`, `FIXME`, `XXX`, `HACK`, `BUG`, `TEMP` comments
- Stub exceptions: `NotImplementedError`, `NotImplementedException`, `UnsupportedOperationException`
- Rust stubs: `unimplemented!()`, `todo!()`
- Go panics with "not implemented" or "TODO"
- C++ runtime_error throws
- Placeholder returns: `null`, `None`, `{}`, `[]`, `false`, `0`

### Documentation Checks
All Phase 2 languages require:
- Function/method docstrings with meaningful content (>30 chars)
- Complex functions (>5 lines) need comprehensive documentation
- Complex code blocks (>8 lines) need inline comments
- Meaningful variable names (no `x`, `temp`, `data`, `obj`, etc.)

## Running Tests

```bash
cd windsurf-hooker
bash tests/test-phase2-languages.sh
```

Expected output:
```
=== Phase 2 Language Support Tests ===
Total: 13 | Passed: 13 | Failed: 0
```

## Example: Java Code

### ❌ BLOCKED - Missing Docstring
```java
public class DataProcessor {
    public void process() {
        System.out.println("incomplete");
    }
}
```
**Error**: Function 'process' is missing a docstring

### ✅ ALLOWED - Complete with Documentation
```java
/**
 * Processes the incoming data stream.
 * Validates input and applies transformations.
 */
public void process() {
    System.out.println("complete");
}
```

## Example: C++ Code

### ❌ BLOCKED - Runtime Error Stub
```cpp
#include <stdexcept>

void processData() {
    throw std::runtime_error("not implemented yet");
}
```
**Error**: Stub or incomplete marker: throw std::runtime_error

### ✅ ALLOWED - Complete with Documentation
```cpp
/**
 * Processes the incoming data stream.
 * Validates input and applies transformations.
 */
void processData() {
    std::cout << "Processing data" << std::endl;
}
```

## Example: Go Code

### ❌ BLOCKED - TODO Panic
```go
func ProcessData() {
    panic("TODO: implement data processing")
}
```
**Error**: Code contains incomplete markers

### ✅ ALLOWED - Complete with Comments
```go
// ProcessData handles the incoming data stream.
// It validates input and applies transformations.
func ProcessData() {
    println("Processing data")
}
```

## Example: Rust Code

### ❌ BLOCKED - Unimplemented!
```rust
fn process_data() {
    unimplemented!()
}
```
**Error**: Stub or incomplete marker: unimplemented!

### ✅ ALLOWED - Complete with Doc Comments
```rust
/// Processes the incoming data stream.
/// 
/// Validates input and applies transformations.
fn process_data() {
    println!("Processing data");
}
```

## Architecture

```
Windsurf IDE
    ↓
[pre_write_completeness.py]
    - Detects TODOs, stubs, placeholders
    - Language-specific patterns
    - Exit 2 if violations found
    ↓ (Pass)
[pre_write_comprehensive_comments.py]
    - Extracts functions by language
    - Validates docstrings
    - Checks inline comment density
    - Exit 2 if violations found
    ↓ (Pass)
File Write Allowed
```

## Supported Comment Styles by Language

| Language | Comment Style | Example |
|----------|---------------|---------|
| Java | JavaDoc | `/** ... */` |
| C/C++ | Doxygen | `/** ... */` |
| Go | Go-style | `// Comment on preceding line` |
| Rust | Doc comments | `/// ...` or `//! ...` |

## File Extensions Recognized

```
Java:    .java
C/C++:   .c, .cpp, .cc, .cxx, .c++
Go:      .go
Rust:    .rs
```

## Known Limitations

- **Java**: Simple regex-based method detection (not full AST parsing)
- **C/C++**: Cannot distinguish between declarations and definitions
- **Go**: Only detects exported functions (PascalCase)
- **Rust**: Comment placement detection is heuristic-based

## Troubleshooting

### "Function 'X' is missing a docstring"
Add a docstring/comment block above the function:

**Java**:
```java
/**
 * Brief description of what the function does.
 */
public void myFunction() { }
```

**C++**:
```cpp
/**
 * Brief description of what the function does.
 */
void myFunction() { }
```

**Go**:
```go
// MyFunction does something important.
func MyFunction() { }
```

**Rust**:
```rust
/// Does something important.
fn my_function() { }
```

### "Code contains incomplete markers or stub implementations"
Remove or replace TODO comments and stub code:

- ❌ `// TODO: implement this` → ✅ `// Implementation complete`
- ❌ `throw new NotImplementedError();` → ✅ Actual implementation
- ❌ `panic("unimplemented")` → ✅ Working code
- ❌ `unimplemented!()` → ✅ Implementation

### "Complex code block (N lines) lacks inline comments"
Add inline comments explaining the logic:

```cpp
void complexLogic() {
    // Initialize the data structure for processing
    std::vector<int> data = {1, 2, 3};
    
    // Apply transformation to each element
    for (int i = 0; i < data.size(); i++) {
        data[i] *= 2;
    }
    
    // Output the results
    for (int val : data) {
        std::cout << val << " ";
    }
}
```

## Next Steps

- **Phase 3**: C#, PHP, Swift, Kotlin, Ruby (coming soon)
- **Phase 4**: R, MATLAB (specialized languages)
- See `PHASE_2_IMPLEMENTATION.md` for detailed documentation
