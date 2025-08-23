# Call Tree Analysis Documentation

## Overview

The call tree analysis module provides functionality to analyze Python codebases and build comprehensive call trees showing which functions call a target function, both directly and indirectly. It handles complex scenarios including cross-file calls, import aliases, and recursive relationships.

## Architecture

The module consists of two main components:

1. **Single-file analysis** (`analyze_call_tree.py`) - Handles all import patterns and call types
2. **Project-wide analysis** (`analyze_project_call_tree.py`) - Orchestrates multi-file analysis

## Component Breakdown

### 1. Call Tree Analysis

The foundation is `analyze_call_tree()`, which analyzes a single source file to find direct callers of a target function. It handles import aliases, module.function calls, and direct function calls.

```python
def analyze_call_tree(source_code: str, target_function_name: str) -> dict[str, Any]:
    """
    Analyze Python source code to find all calls to a target function.
    """
    tree = ast.parse(source_code)
    
    # Build a map of function definitions
    functions = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions[node.name] = node
        elif isinstance(node, ast.ClassDef):
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    functions[f"{node.name}.{item.name}"] = item
```

#### Function Discovery

The algorithm first discovers all function definitions in the file:
- Standalone functions: `def foo():`
- Class methods: `class Bar: def baz(self):`

Methods are stored with qualified names like `"GameEngine.evaluate_player"`.

#### Call Site Detection

For each function, we walk its AST to find calls to the target:

```python
for func_name, func_node in functions.items():
    call_sites = []
    
    for node in ast.walk(func_node):
        if isinstance(node, ast.Call):
            func_expr = node.func
            called_func_name = None
            
            if isinstance(func_expr, ast.Name):
                # Direct function call: func()
                called_func_name = func_expr.id
            elif isinstance(func_expr, ast.Attribute):
                # Module.function call: module.func()
                called_func_name = func_expr.attr
            
            if called_func_name == target_function_name:
                # Found a call to our target!
```

#### Argument Extraction

When a call is found, we extract its arguments:

```python
# Extract positional arguments
positional = []
for arg in node.args:
    positional.append(ast.unparse(arg))

# Extract keyword arguments
keyword = {}
for kw in node.keywords:
    if kw.arg:  # Skip **kwargs
        keyword[kw.arg] = ast.unparse(kw.value)
```

This preserves the exact expressions used, like `"player['points']"` or `"len(data)"`.

### 2. Import Resolution

The function extracts import aliases to resolve function calls correctly:

```python
def extract_import_aliases(tree: ast.AST) -> dict[str, str]:
    """Extract import aliases from the AST."""
    import_aliases = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            # Track 'from module import name' statements
            for alias in node.names:
                imported_name = alias.name
                local_name = alias.asname if alias.asname else imported_name
                import_aliases[local_name] = imported_name
    
    return import_aliases
```

#### Handling Import Patterns

The function handles various import styles:

```python
# from utils import target_func
# → import_aliases["target_func"] = "target_func"

# from utils import target_func as renamed_target  
# → import_aliases["renamed_target"] = "target_func"

# import utils
# → import_aliases["utils"] = "utils"
```

#### Resolving Aliased Calls

When analyzing calls, we check if they're aliased imports:

```python
if isinstance(func_expr, ast.Name):
    local_name = func_expr.id
    
    # Check if this is an aliased import
    if local_name in import_tracker.import_aliases:
        actual_name = import_tracker.import_aliases[local_name]
        if actual_name == target_function_name:
            # Found a call via import alias!
            called_func_name = target_function_name
```

This allows us to detect that `renamed_target(2)` is actually calling `target_func`.

### 3. Project-Wide Analysis

The project analyzer orchestrates multi-file analysis with recursive caller discovery.

#### File Discovery

First, we discover all Python files in the project:

```python
def discover_python_files(project_path: Path) -> list[Path]:
    """Discover all Python files in a project directory."""
    python_files = []
    for file_path in project_path.rglob("*.py"):
        # Skip __pycache__ directories
        if "__pycache__" not in str(file_path):
            python_files.append(file_path)
    return python_files
```

The `rglob("*.py")` recursively finds all Python files in nested directories.

#### Cross-File Analysis

We analyze each file for direct calls to the target:

```python
all_direct_callers = []

for file_path in python_files:
    tree = parse_file(file_path)
    if tree is None:
        continue
        
    source_code = file_path.read_text()
    
    # Analyze with import support
    file_result = analyze_call_tree_with_imports(source_code, target_function_name)
    
    # Add file information to each caller
    for caller in file_result["direct_callers"]:
        caller["file"] = str(file_path.relative_to(project_root))
        all_direct_callers.append(caller)
```

#### Recursive Caller Discovery

The key innovation is recursive caller tracking. For each direct caller, we find who calls it:

```python
def find_callers_recursive(func_name: str, visited: set = None) -> list:
    """Recursively find all callers of a function."""
    if visited is None:
        visited = set()
    
    if func_name in visited:
        return []  # Prevent infinite recursion
    
    visited.add(func_name)
    
    callers = []
    for file_path in python_files:
        source_code = file_path.read_text()
        result = analyze_call_tree_with_imports(source_code, func_name)
        
        for caller in result["direct_callers"]:
            caller["file"] = str(file_path.relative_to(project_root))
            # Recursively find who calls this caller
            caller["callers"] = find_callers_recursive(
                caller["name"], visited.copy()
            )
            callers.append(caller)
    
    return callers
```

The `visited` set prevents infinite recursion in circular call chains.

## Example Usage

### Single File Analysis

```python
source_code = '''
def calculate_score(value, multiplier=1.0):
    return value * multiplier * 100

def process_data(data):
    score = calculate_score(len(data), 1.5)
    return score
'''

result = analyze_call_tree(source_code, "calculate_score")
# Returns:
# {
#     "target_function": "calculate_score",
#     "direct_callers": [{
#         "name": "process_data",
#         "file": "example.py",
#         "call_sites": [{
#             "line": 6,
#             "arguments": {
#                 "positional": ["len(data)", "1.5"],
#                 "keyword": {},
#                 "context": "direct"
#             }
#         }],
#         "callers": []
#     }]
# }
```

### Multi-File Project Analysis

Given a project structure:
```
project/
├── main.py
├── utils.py
└── processors.py
```

Where:
- `utils.py` defines `calculate_score()`
- `processors.py` imports and calls `calculate_score()`
- `main.py` calls functions from `processors.py`

```python
result = analyze_project_call_tree("project/", "calculate_score")
```

Returns a nested structure showing:
- `process_user_data` calls `calculate_score`
- `main` calls `process_user_data`

## Algorithm Complexity

### Time Complexity
- **File discovery**: O(n) where n is the number of files
- **AST parsing**: O(m) where m is total lines of code
- **Call detection**: O(f × c) where f is functions and c is average calls per function
- **Recursive caller discovery**: O(d × f) where d is call depth

### Space Complexity
- **AST storage**: O(m) for parsed trees
- **Call tree**: O(f × c) for the result structure
- **Visited set**: O(f) to prevent cycles

## Handling Edge Cases

### 1. Circular Dependencies
The `visited` set in `find_callers_recursive()` prevents infinite loops when functions call each other cyclically.

### 2. Missing Files
The `parse_file()` function returns `None` for unparseable files, which we gracefully skip:
```python
tree = parse_file(file_path)
if tree is None:
    continue
```

### 3. Import Variations
The `ImportTracker` handles:
- Direct imports: `from module import func`
- Renamed imports: `from module import func as alias`
- Module imports: `import module` (for `module.func()` calls)

### 4. Nested Functions
Currently, nested functions are not tracked separately. They're analyzed as part of their parent function's body.

### 5. Dynamic Calls
Dynamic calls like `getattr(obj, "method")()` or calls via variables are not detected, as they require runtime analysis.

