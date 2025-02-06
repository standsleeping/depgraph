from depgraph.import_crawler.module_info import ModuleInfo


class TreePrinter:
    def __init__(self, graph: dict[ModuleInfo, set[ModuleInfo]]):
        self.graph = graph

    def tree(self, root: ModuleInfo, indent: int = 0) -> str:
        """Prints the tree of modules."""
        # Create the current line with proper indentation
        result = f"{self._indent(indent)}{root.file_name}\n"

        if root not in self.graph:
            return result

        # Sort dependencies by filename for consistent output
        sorted_deps = sorted(self.graph[root], key=lambda x: x.file_name)
        for module in sorted_deps:
            result += self.tree(module, indent + 1)

        return result

    def _indent(self, indent: int) -> str:
        return "    " * indent
