import sys
from .import_crawler import ImportCrawler

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_graph.py <entry_script.py>")
        sys.exit(1)

    entry_file = sys.argv[1]
    crawler = ImportCrawler(entry_file)
    crawler.build_graph(entry_file)
    print(crawler.graph)
