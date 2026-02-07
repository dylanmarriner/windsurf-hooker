# /df - File System Analysis Workflow

**Triggered by:** `/df [path]`  
**Purpose:** Rapid file system context gathering and analysis  
**Safety Level:** Read-only (no mutations)

## Workflow Steps

### 1. Gather File System Context
- List directory structure with depth analysis
- Identify key configuration files
- Map project layout and organization

### 2. Analyze File Properties
- Get file sizes, modification times
- Identify file types and distributions
- Detect unused or orphaned files

### 3. Generate System Overview
- Total project size
- File count by type
- Directory hierarchy visualization
- Storage distribution

### 4. Identify Problem Areas
- Large files (>1MB)
- Deep nesting (>5 levels)
- Duplicate files
- Dead code or unused modules

## Output Format

```
Project: [name]
Location: [path]
Total Size: [human-readable]
File Count: [total]

Structure:
[tree visualization]

Analysis:
- Configuration files: [count]
- Source code files: [count]
- Test files: [count]
- Documentation: [count]
- Build/config artifacts: [count]

Concerns:
[list of identified issues]
```

## Usage Examples

```bash
# Full project analysis
/df

# Specific directory
/df src/

# With depth limit
/df --depth=2

# Show only code files
/df --filter=code
```

## Safety Guarantees

- ✓ Read-only filesystem access only
- ✓ No execution or modification
- ✓ No sensitive data exposure
- ✓ Respects .gitignore patterns
- ✓ Memory-safe for large trees
