from importlib.util import find_spec
import os
from typing import Set, Dict, List
from logging import Logger


class ImportCategorizer:
    def __init__(
        self, stdlib_paths: Set[str], site_packages_paths: Set[str], logger: Logger
    ) -> None:
        self.stdlib_paths = stdlib_paths
        self.site_packages_paths = site_packages_paths
        self.logger = logger
        self.system_imports: Set[str] = set()
        self.third_party_imports: Set[str] = set()
        self.local_imports: Set[str] = set()

    def categorize_import(self, module_name: str) -> None:
        """Categorize an import into system, third-party, or local."""
        try:
            spec = find_spec(module_name)
            if spec and spec.origin:
                is_builtin = spec.origin == "built-in" or spec.origin == "frozen"
                is_stdlib = any(spec.origin.startswith(p) for p in self.stdlib_paths)
                if is_builtin or is_stdlib:
                    self.system_imports.add(module_name)
                    return

                # Check if it's in site-packages
                module_path = os.path.abspath(spec.origin)
                is_third_party = any(
                    module_path.startswith(site_pkg)
                    for site_pkg in self.site_packages_paths
                )
                if is_third_party:
                    self.third_party_imports.add(module_name)
                    return
        except (ImportError, AttributeError):
            pass

        # If find_spec fails or returns None/no origin, try searching site-packages directly
        base_module = module_name.split(".")[0]  # Get the root package name
        for site_pkg in self.site_packages_paths:
            potential_locations = [
                os.path.join(site_pkg, base_module),  # As a directory/package
                os.path.join(site_pkg, f"{base_module}.py"),  # As a .py file
                os.path.join(site_pkg, f"{base_module}.pyi"),  # As a .pyi file
                os.path.join(site_pkg, f"{base_module}.so"),  # As a compiled module
            ]
            if any(os.path.exists(loc) for loc in potential_locations):
                self.third_party_imports.add(module_name)
                return

        # If not system or third-party, assume it's local
        self.local_imports.add(module_name)

    def get_unresolved_imports(self) -> Dict[str, List[str]]:
        """Returns unresolved imports as a dictionary for JSON output."""
        result = {}

        if self.local_imports:
            result["local_imports"] = sorted(list(self.local_imports))

        if self.system_imports:
            result["system_imports"] = sorted(list(self.system_imports))

        if self.third_party_imports:
            result["third_party_imports"] = sorted(list(self.third_party_imports))

        return result
