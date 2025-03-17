# Import Crawler

A Python module dependency analyzer that builds a graph of import relationships between Python files.

## Usage

Basic usage:

```bash
python -m depgraph.import_crawler --path <path-to-python-file-or-directory>
```

Example:

```bash
python -m depgraph.import_crawler --path ./depgraph/analyze_file.py
```


### Options

- `file_path`: Path to the Python file to analyze
- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) (default: INFO)
- `--log-file`: Path to log file (if not specified, logs to stderr only)
- `--display`: Display format(s) for console output (simple, tree, JSON, all) (default: simple)
- `--output-file`: Write analysis results to specified file
- `--output-format`: Format for output file (JSON) (default: JSON)

### Display Formats

- `simple`: Basic text output showing direct dependencies
- `tree`: Tree-like visualization of the dependency hierarchy
- `json`: Detailed JSON format showing imports and imported-by relationships
- `all`: Show all display formats

### Output File

When using `--output-file`, the analysis results will be written to the specified file. Currently, only JSON format is supported, which includes:

- Full dependency graph
- Import relationships (both directions)
- File paths and module information

Example with all options:

```bash
python -m depgraph.import_crawler ./depgraph/analyze_file.py \
  --log-level DEBUG \
  --log-file ./depgraph.log \
  --display all --output-file ./depgraph.json --output-format json
```
