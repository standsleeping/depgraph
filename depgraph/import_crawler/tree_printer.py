from depgraph.import_crawler.module_info import ModuleInfo


class TreePrinter:
    def __init__(self, graph: dict[ModuleInfo, set[ModuleInfo]]):
        self.graph = graph
        self.visited: set[ModuleInfo] = set()

    def tree(self, root: ModuleInfo, indent: int = 0) -> str:
        """Prints the tree of modules."""
        # Create the current line with proper indentation
        result = f"{self._indent(indent)}{root.file_name}\n"

        # Check for cycles
        if root in self.visited:
            # Add a marker to indicate circular dependency
            return f"{self._indent(indent)}{root.file_name} (circular)\n"

        self.visited.add(root)

        if root not in self.graph:
            self.visited.remove(root)
            return result

        # Sort dependencies by filename for consistent output
        sorted_deps = sorted(self.graph[root], key=lambda x: x.file_name)
        for module in sorted_deps:
            result += self.tree(module, indent + 1)

        self.visited.remove(root)
        return result

    def _indent(self, indent: int) -> str:
        return "    " * indent
