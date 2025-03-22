import ast
import os
import sys
import logging
import sysconfig
from pathlib import Path
from importlib.util import find_spec
from typing import Optional, Dict, List
from .module_info import ModuleInfo
from depgraph.logger.setup_logger import setup_logger
from .package_finder import find_outermost_package_root
from .package_searcher import find_module_in_package_hierarchy
from .new_package_searcher import new_find_module_in_package_hierarchy
from .dependency_graph import DependencyGraph
from .site_packages import find_project_site_packages
from .import_categorizer import ImportCategorizer


class ImportCrawler:
    """
    Crawls the import graph for the given entry file.

    Args:
        abs_file_path: The absolute path to the file to crawl
        logger: The logger to use

    NOTES:
    - self.root_file (str) is deprecated. Replace with self.root_file_path (Path).
    - self.parent_path_str (str) is deprecated. The Path-appropriate version is self.parent_path (Path).
    - (More deprecated items to come)
    """

    def __init__(
        self, abs_file_path: Path, logger: logging.Logger | None = None
    ) -> None:
        self.root_file = str(abs_file_path)
        self.root_file_path = abs_file_path
        self.parent_path_str = os.path.dirname(self.root_file)
        self.parent_path = abs_file_path.parent
        self.visited: set[str] = set()
        self.visited_paths: set[Path] = set()
        self.graph = DependencyGraph()

        if logger is None:
            logger = setup_logger()
        self.logger = logger

        # Old str-based version:
        # self.logger.debug(f"Initialized with root: {os.path.basename(self.root_file)}")

        # New path-based version:
        self.logger.debug(f"Initialized with root: {self.root_file_path.name}")

        # Get standard library paths
        paths: Dict[str, str] = sysconfig.get_paths()

        # We use strings here because this data is always used with importlib.util.find_spec.
        self.stdlib_path_strs = set([p for p in paths.values()])

        # Get site-packages paths for the project being analyzed
        self.site_packages_paths: set[Path] = find_project_site_packages(
            self.parent_path_str,
            self.logger,
        )

        # Initialize the import categorizer
        self.import_categorizer = ImportCategorizer(
            self.stdlib_path_strs,
            self.site_packages_paths,
            self.logger,
        )

    @property
    def unresolved_local_imports(self) -> set[str]:
        return self.import_categorizer.local_imports

    @property
    def unresolved_system_imports(self) -> set[str]:
        return self.import_categorizer.system_imports

    @property
    def unresolved_third_party_imports(self) -> set[str]:
        return self.import_categorizer.third_party_imports

    def build_graph(
        self, file_path: Optional[Path] = None, old_file_path_str: Optional[str] = None
    ) -> DependencyGraph:
        """
        Recursively builds the import graph.
        If no file path is provided, uses the root file.
        Returns the dependency graph for convenience.

        Args:
            file_path: The absolute path to the file to crawl
            old_file_path_str: The old file path string (for backwards compatibility)

        Returns:
            The dependency graph
        """

        if old_file_path_str is not None:
            file_path = Path(old_file_path_str)
        elif file_path is None:
            file_path = self.root_file_path
        else:
            raise ValueError("file_path and old_file_path_str cannot both be None")

        if file_path in self.visited_paths or not file_path.suffix == ".py":
            self.logger.debug(f"Skipping file: {file_path.name}")
            return self.graph

        self.logger.info(f"Building graph for {file_path.name}")

        self.visited_paths.add(file_path)
        self.visited.add(str(file_path))  # TODO: Remove this

        tree = self.parse_file(file_path)

        if tree is None:
            self.logger.warning(f"Failed to parse {file_path.name}")
            return self.graph

        module_dir = file_path.parent

        self.process_imports(tree, file_path, module_dir)

        return self.graph

    def parse_file(self, file_path: Path) -> Optional[ast.AST]:
        """
        Parses a Python file and returns its AST.
        Returns None if the file cannot be parsed or found.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return ast.parse(f.read(), filename=file_path)
        except (SyntaxError, FileNotFoundError):
            return None

    def process_imports(self, tree: ast.AST, file_path: Path, module_dir: Path) -> None:
        """Process import statements in the AST and add them to the graph."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    alias_name: str = alias.name
                    self.resolve_import(
                        alias_name,
                        str(file_path),
                        module_dir,
                    )
            elif isinstance(node, ast.ImportFrom):
                if isinstance(node.module, str):
                    module_name: str = node.module
                    if module_name:
                        self.resolve_import(
                            module_name,
                            str(file_path),
                            module_dir,
                        )

    def resolve_import(
        self, module_name_str: str, current_file_str: str, search_dir: Path
    ) -> None:
        """Resolves the module path and updates the graph."""
        self.logger.debug(f"Resolving import {module_name_str} from {current_file_str}")

        module_path = self.find_module(module_name_str, search_dir)  # TODO: FRAME 0

        if module_path:
            current = ModuleInfo(current_file_str)
            module = ModuleInfo(module_path)
            self.graph.add_dependency(current, module)
            self.build_graph(None, module_path)
        else:
            self.categorize_unresolved_import(module_name_str)
            self.logger.debug(f"Could not resolve {module_name_str}")

    def categorize_unresolved_import(self, module_name: str) -> None:
        """Categorize an unresolved import using the ImportCategorizer."""
        self.import_categorizer.categorize_import(module_name)

    def find_module(self, module_name: str, search_dir: Path) -> Optional[Path]:
        """
        Attempts to find the module file given its name by:
        1. Searching through the package hierarchy from current directory
        2. If we're in a src-layout project, try to find the module considering the src directory
        3. If not found locally, try finding through sys.path
        """
        # First try searching through package hierarchy
        outer_root: Path = find_outermost_package_root(search_dir, self.logger)

        module_path: Path | None = new_find_module_in_package_hierarchy(
            module_name, search_dir, outer_root, self.logger
        ) # TODO: FRAME 1

        if module_path:
            return module_path

        # Check if we're in a src-layout project
        if self.is_src_layout_project():
            self.logger.debug(
                f"Detected src-layout project, trying alternative resolution for {module_name}"
            )
            # Find the src directory in the path
            path_parts = os.path.normpath(self.parent_path_str).split(os.sep)
            if "src" in path_parts:
                src_index = path_parts.index("src")
                # The project root should be the directory containing src/
                src_project_root = os.sep.join(path_parts[:src_index])

                # Try to resolve absolute imports through the src directory
                if module_name.count(".") > 0:
                    # Split the module name into package and submodule parts
                    parts = module_name.split(".")
                    # Try reconstructing the path based on src-layout conventions
                    possible_paths = []

                    # Try as a direct path from src directory
                    src_path = os.path.join(src_project_root, "src")
                    package_path = os.path.join(src_path, *parts)
                    possible_paths.append(package_path + ".py")
                    possible_paths.append(os.path.join(package_path, "__init__.py"))

                    # Try with src/parts[0]/parts[1:] structure
                    if len(parts) > 1:
                        package_path = os.path.join(src_path, parts[0])
                        submodule_path = os.path.join(package_path, *parts[1:])
                        possible_paths.append(submodule_path + ".py")
                        possible_paths.append(
                            os.path.join(submodule_path, "__init__.py")
                        )

                    # Check all possible paths
                    for path in possible_paths:
                        if os.path.exists(path):
                            self.logger.debug(f"Found module in src-layout: {path}")
                            return path

        # If not found locally, try finding through sys.path
        module_path = self.find_module_in_syspath(module_name)
        if module_path:
            return module_path

        return None

    def find_module_in_syspath(self, module_name: str) -> Optional[str]:
        """
        Attempts to find the module through sys.path.
        Returns the path if found and is a local module, None otherwise.
        For src-layout projects, temporarily adds the src parent directory to sys.path.
        """
        # Save the original sys.path to restore it later
        original_sys_path = sys.path.copy()

        try:
            # Check if we're in a src-layout project and add the src parent to path if needed
            if self.is_src_layout_project():
                path_parts = os.path.normpath(self.parent_path_str).split(os.sep)
                if "src" in path_parts:
                    src_index = path_parts.index("src")
                    # The project root should be the directory containing src/
                    src_project_root = os.sep.join(path_parts[:src_index])
                    self.logger.debug(
                        f"Adding src project root to sys.path: {src_project_root}"
                    )
                    sys.path.insert(0, src_project_root)

            # Look for the module using importlib
            spec = find_spec(module_name)
            if spec and spec.origin:
                # Filter out compiled modules and non-local modules
                if spec.origin.endswith(".py"):
                    module_path = os.path.abspath(spec.origin)
                    # Check if module is in standard library
                    for stdlib_path in self.stdlib_path_strs:
                        if module_path.startswith(stdlib_path):
                            return None
                    # Check if module is within project directory or src directory
                    if self.is_src_layout_project():
                        # For src-layout, consider modules in the src directory as local
                        path_parts = os.path.normpath(self.parent_path_str).split(os.sep)
                        if "src" in path_parts:
                            src_index = path_parts.index("src")
                            src_project_root = os.sep.join(path_parts[:src_index])
                            if module_path.startswith(src_project_root):
                                return module_path
                    # Otherwise use the standard project_root check
                    elif module_path.startswith(self.parent_path_str):
                        return module_path
        except (ImportError, AttributeError):
            pass
        finally:
            # Restore the original sys.path
            sys.path = original_sys_path

        return None

    def get_unresolved_imports(self) -> Dict[str, List[str]]:
        """Returns unresolved imports as a dictionary for JSON output."""
        return self.import_categorizer.get_unresolved_imports()

    def is_src_layout_project(self) -> bool:
        """
        Detect if this is a src-layout project by looking for common
        markers like src/ directory and pyproject.toml
        """
        # Get the directory containing the file
        path_parts = os.path.normpath(self.parent_path_str).split(os.sep)

        # Look for src/ in the path
        if "src" not in path_parts:
            return False

        # Find the index of 'src' in the path
        src_index = path_parts.index("src")

        # The project root should be the directory containing src/
        potential_project_root = os.sep.join(path_parts[:src_index])

        # Check for project configuration files
        for config_file in ["pyproject.toml", "setup.py", "setup.cfg"]:
            if os.path.exists(os.path.join(potential_project_root, config_file)):
                return True

        return False
