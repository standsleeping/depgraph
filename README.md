# depgraph

Analyze dependencies in a Python project.

This project performs four main tasks:

1. Analyze the (nested) scopes in a Python file.
2. Analyze certain variable assignments in a Python file.
3. Crawl the dependency graph of a Python file.
4. Build call trees showing which functions call a target function.

## Usage

Basic usage:
```bash
python -m depgraph <file_path>
```

Examples:
```bash
# Analyze dependencies (default)
python -m depgraph ./src/depgraph/processors/process_file.py

# Analyze call tree for a function across entire project
python -m depgraph src --action call-tree --target-function parse_file
```

### Options

- `file_path`: Path to the Python file or directory to analyze
- `--action`: Type of analysis to perform: `dependencies` (default) or `call-tree`
- `--target-function`: Target function name for call tree analysis (required with `--action call-tree`)
- `--depth`: Depth of the analysis (default: 4)
- `--log-level`: Set logging level (DEBUG, INFO) (default: INFO)
- `--scope-filter`: Filter output to a specific scope (e.g., '<module>.outer.Inner.method')
- `--output-file`: Write results to specified file
- `--output-format`: Format for output file (JSON) (default: JSON)

Examples with options:
```bash
# Dependency analysis with options
python -m depgraph ./src/depgraph/processors/process_file.py \
  --depth 6 \
  --log-level DEBUG \
  --scope-filter "<module>.my_function"

# Call tree analysis with output file
python -m depgraph src \
  --action call-tree \
  --target-function parse_file \
  --output-file ./call_tree.json \
  --log-level INFO
```


### Output File

When using `--output-file`, the analysis results will be written to the specified file in JSON format. For dependency analysis, this includes:

- Scope analysis
- Assignment information  
- Dependency graph information
- Import relationships

For call tree analysis, this includes:
- Target function name
- Direct callers with call sites and arguments
- Recursive caller relationships

Example with output file:

```bash
python -m depgraph ./src/depgraph/processors/process_file.py \
  --log-level DEBUG \
  --output-file ./depgraph.json
```

## Programmatic API

### Call Tree Analysis

Build call trees to understand which functions call a target function, both directly and indirectly:

```python
from depgraph import analyze_call_tree, analyze_project_call_tree

# Analyze a single file
source_code = '''
def calculate_score(value, multiplier=1.0):
    return value * multiplier * 100

def process_data(data):
    score = calculate_score(len(data), 1.5)
    return score
'''

result = analyze_call_tree(source_code, "calculate_score")
print(result["direct_callers"])  # Shows process_data calls calculate_score

# Analyze an entire project
result = analyze_project_call_tree("/path/to/project", "target_function")
```

The call tree analysis handles:
- Cross-file function calls
- Import aliases (`from utils import func as renamed_func`)
- Module.function calls (`utils.func()`)
- Recursive caller relationships (who calls the callers)