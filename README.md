# depgraph

Analyze dependencies in a Python project.

At the moment, depgraph performs three main tasks:

1. Analyze the (nested) scopes in a Python file.
2. Analyze certain variable assignments in a Python file.
3. Crawl the dependency graph of a Python file.

## Usage

Basic usage:
```bash
python -m depgraph <file_path>
```

Example:
```bash
python -m depgraph ./src/depgraph/processors/process_file.py
```

### Options

- `file_path`: Path to the Python file to analyze
- `--depth`: Depth of the analysis (default: 4)
- `--log-level`: Set logging level (DEBUG, INFO) (default: INFO)
- `--log-file`: Path to log file (if not specified, logs to stderr only)
- `--scope-filter`: Filter output to a specific scope (e.g., '<module>.outer.Inner.method')
- `--output-file`: Write results to specified file
- `--output-format`: Format for output file (JSON) (default: JSON)

Example with all options:
```bash
python -m depgraph ./src/depgraph/processors/process_file.py \
  --depth 6 \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --scope-filter "<module>.my_function"
```


### Output File

When using `--output-file`, the analysis results will be written to the specified file in JSON format, which includes:

- Scope analysis
- Assignment information
- Dependency graph information
- Import relationships

Example with output file:

```bash
python -m depgraph ./src/depgraph/processors/process_file.py \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --output-file ./depgraph.json
```