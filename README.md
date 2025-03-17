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
- `--display`: Display format(s) for crawler output (simple, tree, JSON, all) (default: simple)
- `--scope`: Analyze dependencies for a specific scope (e.g., a function name or "<module>" for module level) (default: "<module>")
- `--output-file`: Write crawler analysis results to specified file
- `--output-format`: Format for crawler output file (JSON) (default: JSON)

Example with all options:
```bash
python -m depgraph ./src/depgraph/processors/process_file.py \
  --depth 6 \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --scope "my_function"
```

### Display Formats (Crawler)

- `simple`: Basic text output showing direct dependencies
- `tree`: Tree-like visualization of the dependency hierarchy
- `json`: Detailed JSON format showing imports and imported-by relationships
- `all`: Show all display formats

### Output File (Crawler)

When using `--output-file`, the analysis results will be written to the specified file. Currently, only JSON format is supported, which includes:

- Full dependency graph
- Import relationships (both directions)
- File paths and module information

Example with all options:

```bash
python -m depgraph.import_crawler ./depgraph/process_file.py \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --display all --output-file ./depgraph.json --output-format json
```