#!/usr/bin/env python3
"""
pre_write_comprehensive_comments: Enforce Comprehensive, Meaningful Commentary

Core Invariant:
- Every function/class must have a docstring explaining purpose, parameters, return value
- Complex logic must have inline comments explaining WHY (not WHAT)
- Comments must be accurate and non-trivial
- No empty or one-liner docstrings for functions > 5 lines
- Code must be inherently debuggable through clear naming and documentation

This enforces that code is not just working, but DOCUMENTED and MAINTAINABLE.
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Tuple

def resolve_policy_path() -> Path:
    """Resolve policy path (deployed path first, repo-local fallback for testing)."""
    system_path = Path("/etc/windsurf/policy/policy.json")
    local_path = Path(__file__).resolve().parents[1] / "windsurf" / "policy" / "policy.json"
    return system_path if system_path.exists() else local_path


POLICY_PATH = resolve_policy_path()


def block(msg: str, details: List[str] = None):
    """Block code lacking comprehensive comments."""
    print("BLOCKED: pre_write_comprehensive_comments - Insufficient documentation", file=sys.stderr)
    print(msg, file=sys.stderr)
    if details:
        for detail in details:
            print(f"  - {detail}", file=sys.stderr)
    sys.exit(2)


def extract_functions(code: str, language: str) -> List[Dict]:
    """Extract function definitions and their metadata for all supported languages."""
    functions = []
    lines = code.split("\n")
    
    if language in ("python", "py"):
        # Python function pattern: def name(...): or async def name(...):
        pattern = r"^\s*(?:async\s+)?def\s+(\w+)\s*\([^)]*\)\s*(?:->\s*\w+)?\s*:"
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                func_name = match.group(1)
                func_line = i + 1
                indent_level = len(line) - len(line.lstrip())
                func_body_lines = []
                docstring = None
                
                for j in range(i + 1, min(i + 50, len(lines))):
                    next_line = lines[j]
                    next_indent = len(next_line) - len(next_line.lstrip())
                    if next_line.strip() and next_indent <= indent_level:
                        break
                    func_body_lines.append(next_line)
                    if j == i + 1:
                        stripped = next_line.strip()
                        if stripped.startswith('"""') or stripped.startswith("'''"):
                            docstring = stripped
                
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": len(func_body_lines),
                    "docstring": docstring, "language": "python",
                })
    
    elif language in ("javascript", "typescript", "js", "ts"):
        # JS/TS function patterns
        pattern = r"^\s*(?:async\s+)?function\s+(\w+)\s*\([^)]*\)\s*\{|^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{|^\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*=>"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1) or match.group(2) or match.group(3)
                func_line = i + 1
                docstring = None
                if i > 0 and "*/" in lines[i - 1]:
                    docstring = "JSDoc"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "javascript",
                })
    
    elif language == "java":
        # Java: public/private/static [return_type] methodName(...) {
        pattern = r"^\s*(public|private|protected|static|abstract)*\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match and not line.strip().startswith("//"):
                func_name = match.group(2)
                func_line = i + 1
                docstring = None
                if i > 0 and "*/" in lines[i - 1]:
                    docstring = "JavaDoc"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "java",
                })
    
    elif language in ("cpp", "c", "c++"):
        # C/C++: return_type funcName(...) {
        pattern = r"^\s*\w+[\s\*&]+(\w+)\s*\([^)]*\)\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match and not line.strip().startswith("//"):
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and "*/" in lines[i - 1]:
                    docstring = "Doxygen"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": language,
                })
    
    elif language == "go":
        # Go: func [receiver] FuncName(...) [return_type] {
        pattern = r"^\s*func\s+(?:\(\w+\s+[\w\*]+\)\s+)?([A-Z]\w+)\s*\([^)]*\)\s*\w*\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and lines[i - 1].strip().startswith("//"):
                    docstring = "Go-style"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "go",
                })
    
    elif language == "rust":
        # Rust: pub fn name(...) -> type { or fn name(...) {
        pattern = r"^\s*(?:pub\s+)?(?:async\s+)?fn\s+(\w+)\s*\([^)]*\)(?:\s*->\s*[\w:&<>\[\]]+)?\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and lines[i - 1].strip().startswith("///"):
                    docstring = "Doc-comment"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "rust",
                })
    
    elif language == "csharp":
        # C#: [modifiers] returnType MethodName(...) {
        pattern = r"^\s*(?:public|private|protected)*\s+\w+\s+(\w+)\s*\([^)]*\)\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match and not line.strip().startswith("//"):
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and lines[i - 1].strip().startswith("///"):
                    docstring = "XML-doc"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "csharp",
                })
    
    elif language == "ruby":
        # Ruby: def method_name(...) ... end
        pattern = r"^\s*def\s+(\w+)\s*\([^)]*\)?"
        for i, line in enumerate(lines):
            match = re.match(pattern, line)
            if match:
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and lines[i - 1].strip().startswith("#"):
                    docstring = "YARD"
                body_lines = 0
                for j in range(i + 1, min(i + 100, len(lines))):
                    body_lines += 1
                    if re.match(r"^\s*end\s*$", lines[j]):
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "ruby",
                })
    
    elif language == "php":
        # PHP: function name(...) { or public function name(...) {
        pattern = r"^\s*(?:public|private|protected)?\s*function\s+(\w+)\s*\([^)]*\)\s*\{?"
        for i, line in enumerate(lines):
            match = re.search(pattern, line)
            if match:
                func_name = match.group(1)
                func_line = i + 1
                docstring = None
                if i > 0 and lines[i - 1].strip().startswith("/**"):
                    docstring = "PHPDoc"
                brace_count = line.count("{") - line.count("}")
                body_lines = 1
                for j in range(i + 1, min(i + 100, len(lines))):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    body_lines += 1
                    if brace_count == 0:
                        break
                functions.append({
                    "name": func_name, "line": func_line, "body_lines": body_lines,
                    "docstring": docstring, "language": "php",
                })
    
    return functions


def check_function_documentation(functions: List[Dict], code: str, path: str) -> List[Dict]:
    """Validate that functions have adequate documentation."""
    violations = []
    
    for func in functions:
        name = func["name"]
        line = func["line"]
        body_lines = func["body_lines"]
        has_docstring = func["docstring"] is not None
        
        # Rules:
        # 1. All functions need docstrings
        if not has_docstring:
            violations.append({
                "type": "missing_docstring",
                "line": line,
                "file": path,
                "function": name,
                "reason": f"Function '{name}' is missing a docstring",
            })
            continue
        
        # 2. Docstring must be meaningful (not just a stub)
        if func["docstring"] in ('"""', "'''", '"""docstring"""'):
            violations.append({
                "type": "empty_docstring",
                "line": line,
                "file": path,
                "function": name,
                "reason": f"Docstring for '{name}' is empty or trivial",
            })
        
        # 3. Functions > 5 lines need more than one-liner
        if body_lines > 5 and func["docstring"] and len(func["docstring"]) < 30:
            violations.append({
                "type": "insufficient_docstring",
                "line": line,
                "file": path,
                "function": name,
                "reason": f"Docstring for '{name}' is too brief for a {body_lines}-line function",
            })
    
    return violations


def check_inline_comments_density(code: str, path: str, language: str) -> List[Dict]:
    """Validate that complex code has adequate inline comments."""
    violations = []
    lines = code.split("\n")
    
    # Find "complex" code blocks (>8 consecutive lines of non-comment, non-brace code)
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip comments, empty lines, docstrings, pure braces
        if not line or line in ["{", "}", "};", "{;"] or line.startswith("#") or line.startswith("//"):
            i += 1
            continue
        
        # Skip function/class definitions (they're allowed without inline comments)
        if re.match(r"^\s*(def|function|async\s+function|fn|pub\s+fn|func|public\s+\w+\s+\w+|class\s+|interface\s+)", lines[i]):
            i += 1
            continue
        
        # Count consecutive non-comment lines (excluding braces and definitions)
        code_lines = 0
        comment_lines = 0
        start_line = i
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Skip definition lines
            if re.match(r"^\s*(def|function|async\s+function|fn|pub\s+fn|func|public\s+\w+\s+\w+|class\s+|interface\s+)", lines[i]):
                break
            
            if line and not line in ["{", "}", "};", "{;"] and not line.startswith("#") and not line.startswith("//"):
                code_lines += 1
            elif line.startswith("#") or line.startswith("//"):
                comment_lines += 1
            i += 1
            
            # Stop at function/class definition or EOF
            if i >= len(lines) or re.match(r"^\s*(def|function|fn|pub\s+fn|func|class\s+)", lines[i]):
                break
        
        # Only flag if we have >8 lines of actual logic code without comments
        if code_lines > 8 and comment_lines == 0:
            violations.append({
                "type": "insufficient_inline_comments",
                "line": start_line + 1,
                "file": path,
                "code_lines": code_lines,
                "comment_lines": comment_lines,
                "reason": f"Complex code block ({code_lines} lines) lacks inline comments explaining logic",
            })
    
    return violations


def check_meaningful_names(code: str, path: str) -> List[Dict]:
    """Check for non-meaningful variable names."""
    violations = []
    
    # Bad variable name patterns
    bad_patterns = [
        (r"\b(x|y|z|temp|tmp|val|data|obj|item|result|stuff|thing)\s*=", "generic single-letter or placeholder name"),
        (r"\bvar\s+(x|y|z|temp|tmp)\b", "var with generic name"),
    ]
    
    for pattern, reason in bad_patterns:
        for match in re.finditer(pattern, code):
            line_num = code[:match.start()].count("\n") + 1
            violations.append({
                "type": "unclear_naming",
                "line": line_num,
                "file": path,
                "name": match.group(1),
                "reason": f"Variable '{match.group(1)}' is {reason}. Use meaningful names.",
            })
    
    # Only report first few to avoid noise
    return violations[:5]


def detect_language(path: str) -> str:
    """Detect programming language from file extension (Phase 2+ support)."""
    # Phase 2: Java, C/C++, Go, Rust
    if path.endswith((".py",)):
        return "python"
    elif path.endswith((".js", ".ts", ".jsx", ".tsx")):
        return "javascript"
    elif path.endswith((".java",)):
        return "java"
    elif path.endswith((".cpp", ".cc", ".cxx", ".c++")):
        return "cpp"
    elif path.endswith((".c",)):
        return "c"
    elif path.endswith((".go",)):
        return "go"
    elif path.endswith((".rs",)):
        return "rust"
    # Phase 3: C#, PHP, Swift, Kotlin, Ruby
    elif path.endswith((".cs",)):
        return "csharp"
    elif path.endswith((".php", ".php3", ".php4", ".php5", ".php7", ".php8")):
        return "php"
    elif path.endswith((".swift",)):
        return "swift"
    elif path.endswith((".kt", ".kts")):
        return "kotlin"
    elif path.endswith((".rb",)):
        return "ruby"
    # Phase 4: R, MATLAB
    elif path.endswith((".r", ".R")):
        return "r"
    elif path.endswith((".m",)):
        return "matlab"
    else:
        return "unknown"


def main():
    """Check code for comprehensive comment coverage."""
    try:
        payload = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON input", file=sys.stderr)
        sys.exit(1)
    
    # Check execution profile
    text = POLICY_PATH.read_text().strip() if POLICY_PATH.exists() else ""
    policy = json.loads(text) if text else {}
    
    execution_profile = policy.get("execution_profile", "standard")
    
    # In locked mode: ALL code writes blocked
    if execution_profile == "locked":
        block(
            "System is in LOCKED mode (panic button activated).",
            ["All code writes are revoked.", "Contact administrator to unlock."],
        )
    
    edits = (payload.get("tool_info", {}) or {}).get("edits", [])
    
    all_violations = []
    
    for edit in edits:
        new_code = edit.get("new_string", "") or ""
        path = edit.get("path", "unknown")
        
        # Skip test files, config files, and markdown
        if any(x in path.lower() for x in ["test", "spec", "mock", ".json", ".md", ".yaml"]):
            continue
        
        language = detect_language(path)
        
        # Only validate supported languages
        if language == "unknown":
            continue
        
        # Check function documentation (Phase 2+: all C-family, Go, Rust, Ruby, PHP)
        supported_doc_check = {
            "python", "javascript", "java", "cpp", "c", "go", "rust", "csharp", "php", "ruby"
        }
        if language in supported_doc_check:
            functions = extract_functions(new_code, language)
            all_violations.extend(check_function_documentation(functions, new_code, path))
        
        # Check inline comment density (all supported languages)
        all_violations.extend(check_inline_comments_density(new_code, path, language))
        
        # Check meaningful names (all supported languages)
        all_violations.extend(check_meaningful_names(new_code, path))
    
    if all_violations:
        details = []
        seen = set()
        
        for v in all_violations:
            line_info = f"{v['file']}:{v['line']}"
            if line_info not in seen:  # Deduplicate
                details.append(f"{line_info} - {v['reason']}")
                seen.add(line_info)
        
        block(
            "Code lacks comprehensive documentation. Every function must have a docstring, "
            "and complex logic must have comments explaining WHY. Names must be meaningful.",
            details[:10],  # Limit to first 10 violations
        )
    
    sys.exit(0)


if __name__ == "__main__":
    main()
