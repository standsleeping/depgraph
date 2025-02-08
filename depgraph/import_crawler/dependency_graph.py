from dataclasses import dataclass
from typing import Dict, Set
from .module_info import ModuleInfo


@dataclass
class DependencyGraph:
    """Represents a dependency graph of Python modules."""
    dependencies: Dict[ModuleInfo, Set[ModuleInfo]]

    def __init__(self) -> None:
        self.dependencies = {}

    def add_dependency(self, source: ModuleInfo, target: ModuleInfo) -> None:
        """Add a dependency from source to target module."""
        self.dependencies.setdefault(source, set()).add(target)
        # Ensure target exists in graph even if it has no dependencies
        self.dependencies.setdefault(target, set())

    def to_json(self) -> Dict[str, Dict[str, list[str]]]:
        """
        Convert the dependency graph to a JSON-serializable dictionary.
        
        Returns:
            A dictionary with file paths as keys and their import information as values.
            Each value contains 'imports' and 'imported_by' lists.
        """
        json_graph: Dict[str, Dict[str, list[str]]] = {}

        # First pass: Create nodes and add imports
        for source, targets in self.dependencies.items():
            source_path = str(source)
            if source_path not in json_graph:
                json_graph[source_path] = {"imports": [], "imported_by": []}

            json_graph[source_path]["imports"] = sorted(
                [str(target) for target in targets]
            )

        # Second pass: Build imported_by relationships
        for source, targets in self.dependencies.items():
            for target in targets:
                target_path = str(target)
                json_graph[target_path]["imported_by"].append(str(source))

        # Sort imported_by lists for consistency
        for node in json_graph.values():
            node["imported_by"].sort()

        return json_graph 