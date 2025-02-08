import ast
import os
import logging
import sysconfig
from importlib.util import find_spec
from typing import Optional
from .module_info import ModuleInfo
from ..logger import setup_logger
from .package_finder import find_outermost_package_root
from .package_searcher import find_module_in_package_hierarchy
from .dependency_graph import DependencyGraph


class ImportCrawler:
    def __init__(self, root_file: str, logger: logging.Logger | None = None) -> None:
        self.root_file = os.path.abspath(root_file)
        self.project_root = os.path.dirname(self.root_file)
        self.visited: set[str] = set()
        self.graph = DependencyGraph()
        self.unresolved_imports: set[str] = set()
        paths = sysconfig.get_paths().values()
        self.stdlib_paths = set([os.path.abspath(p) for p in paths])

        if logger is None:
            logger = setup_logger()
        self.logger = logger
        self.logger.debug(f"Initialized with root: {os.path.basename(self.root_file)}")

    def build_graph(self, file_path: str) -> None:
        """Recursively builds the import graph."""
        file_path = os.path.abspath(file_path)
        if file_path in self.visited or not file_path.endswith(".py"):
            self.logger.debug(f"Skipping file: {os.path.basename(file_path)}")
            return

        self.logger.info(f"Building graph for {os.path.basename(file_path)}")
        self.visited.add(file_path)

        tree = self.parse_file(file_path)
        if tree is None:
            self.logger.warning(f"Failed to parse {os.path.basename(file_path)}")
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
        self.logger.debug(f"Resolving import {module_name} from {current_file}")
        module_path = self.find_module(module_name, search_dir)
        if module_path:
            current = ModuleInfo(current_file)
            module = ModuleInfo(module_path)
            self.graph.add_dependency(current, module)
            self.build_graph(module_path)
        else:
            self.unresolved_imports.add(module_name)
            self.logger.debug(f"Could not resolve {module_name}")

    def find_module(self, module_name: str, search_dir: str) -> Optional[str]:
        """
        Attempts to find the module file given its name by:
        1. Searching through the package hierarchy from current directory
        2. If not found, try finding through sys.path
        """
        # First try searching through package hierarchy
        outer_root = find_outermost_package_root(search_dir, self.logger)
        module_path = find_module_in_package_hierarchy(
            module_name, search_dir, outer_root, self.logger
        )
        if module_path:
            return module_path

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
                if spec.origin.endswith(".py"):
                    module_path = os.path.abspath(spec.origin)
                    # Check if module is in standard library
                    for stdlib_path in self.stdlib_paths:
                        if module_path.startswith(stdlib_path):
                            return None
                    # Check if module is within project directory
                    if module_path.startswith(self.project_root):
                        return module_path
        except (ImportError, AttributeError):
            pass
        return None

    def print_graph(self) -> None:
        """Prints the graph in a human-readable format."""
        for source, targets in self.graph.dependencies.items():
            printed_set = ", ".join([str(module) for module in targets])
            print(f"{source} -> [{printed_set}]")

    def print_unresolved_imports(self) -> None:
        """Prints the set of unresolved imports."""
        if self.unresolved_imports:
            print("-" * 80)
            print("Unresolved imports:")
            for import_name in self.unresolved_imports:
                print(f"  {import_name}")
