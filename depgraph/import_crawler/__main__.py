import sys
from .import_crawler import ImportCrawler
from .tree_printer import TreePrinter
from .module_info import ModuleInfo
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_graph.py <entry_script.py>")
        sys.exit(1)

    entry_file = sys.argv[1]
    crawler = ImportCrawler(entry_file)
    crawler.build_graph(entry_file)
    print("-" * 80)
    crawler.print_graph()
    print("-" * 80)
    printer = TreePrinter(crawler.graph)
    root = ModuleInfo(entry_file)
    print(printer.tree(root))