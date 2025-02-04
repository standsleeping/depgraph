import ast
import os
import sysconfig
from importlib.util import find_spec
from typing import Optional


class ImportCrawler:
    def __init__(self, root_file: str) -> None:
        self.root_file = os.path.abspath(root_file)
        self.project_root = os.path.dirname(self.root_file)
        self.visited: set[str] = set()
        self.graph: dict[str, set[str]] = {}
        paths = sysconfig.get_paths().values()
        self.stdlib_paths = set([os.path.abspath(p) for p in paths])

    def build_graph(self, file_path: str) -> None:
        """Recursively builds the import graph."""
        file_path = os.path.abspath(file_path)
        if file_path in self.visited or not file_path.endswith(".py"):
            return

        self.visited.add(file_path)

        tree = self.parse_file(file_path)
        if tree is None:
            return

        module_dir = os.path.dirname(file_path)
        self.process_imports(tree, file_path, module_dir)

    def parse_file(self, file_path: str) -> Optional[ast.AST]:
        """
        Parses a Python file and returns its AST.
        Returns None if the file cannot be parsed or found.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=file_path)
        except (SyntaxError, FileNotFoundError):
            return None

    def process_imports(self, tree: ast.AST, file_path: str, module_dir: str) -> None:
        """Process import statements in the AST and add them to the graph."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module_name = alias.name
                    self.resolve_import(module_name, file_path, module_dir)
            elif isinstance(node, ast.ImportFrom):
                if isinstance(node.module, str):
                    module_name = node.module
                    if module_name:
                        self.resolve_import(module_name, file_path, module_dir)

    def resolve_import(
        self, module_name: str, current_file: str, search_dir: str
    ) -> None:
        """Resolves the module path and updates the graph."""
        module_path = self.find_module(module_name, search_dir)
        if module_path:
            self.graph.setdefault(current_file, set()).add(module_path)
            self.build_graph(module_path)

    def find_module(self, module_name: str, search_dir: str) -> Optional[str]:
        """
        Attempts to find the module file given its name by:
        1. Checking relative to the current directory
        2. Searching through sys.path
        """
        # First try relative to current directory
        local_module = self.find_local_module(module_name, search_dir)
        if local_module:
            return local_module

        # If not found locally, try finding through sys.path
        module_path = self.find_module_in_syspath(module_name)
        if module_path:
            return module_path

        return None

    def find_module_in_syspath(self, module_name: str) -> Optional[str]:
        """
        Attempts to find the module through sys.path.
        Returns the path if found and is a local module, None otherwise.
        """
        try:
            spec = find_spec(module_name)
            if spec and spec.origin:
                # Filter out compiled modules and non-local modules
                if spec.origin.endswith(".py") and self.is_local_module(spec.origin):
                    return spec.origin
        except (ImportError, AttributeError):
            pass
        return None

    def find_local_module(self, module_name: str, search_dir: str) -> Optional[str]:
        """
        Attempts to find a module relative to the current directory.
        Returns the path if found and is a local module, None otherwise.
        """
        parts = module_name.split(".")
        potential_paths = [
            os.path.join(search_dir, *parts) + ".py",
            os.path.join(search_dir, *parts, "__init__.py"),
        ]
        for path in potential_paths:
            if os.path.exists(path) and self.is_local_module(path):
                return path
        return None

    def is_local_module(self, module_path: str) -> bool:
        """
        Determines if a module is local to the project by checking:
        1. Not in standard library paths
        2. Within project directory
        """
        module_path = os.path.abspath(module_path)

        # Check if module is in standard library
        for stdlib_path in self.stdlib_paths:
            if module_path.startswith(stdlib_path):
                return False

        # Check if module is within project directory
        if not module_path.startswith(self.project_root):
            return False

        return True
