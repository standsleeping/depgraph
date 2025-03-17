# depgraph

Analyze dependencies in a Python project.

## Usage

Basic usage:
```bash
python -m depgraph <file_path>
```

Example:
```bash
python -m depgraph ./depgraph/process_file.py
```

### Options

- `file_path`: Path to the Python file to analyze
- `--depth`: Depth of the analysis (default: 4)
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)
- `--log-file`: Path to log file (if not specified, logs to stderr only)
- `--scope`: Analyze dependencies for a specific scope (e.g., a function name or "<module>" for module level) (default: "<module>")

Example with all options:
```bash
python -m depgraph ./depgraph/process_file.py \
  --depth 6 \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --scope "my_function"
```
