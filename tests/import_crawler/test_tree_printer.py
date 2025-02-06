import pytest
from depgraph.import_crawler.tree_printer import TreePrinter
from depgraph.import_crawler.module_info import ModuleInfo


@pytest.fixture
def module_a():
    return ModuleInfo("module_a.py")


@pytest.fixture
def module_b():
    return ModuleInfo("module_b.py")


@pytest.fixture
def module_c():
    return ModuleInfo("module_c.py")


def test_empty_graph():
    """Graph with no dependencies."""
    module = ModuleInfo("test.py")
    graph = {}
    printer = TreePrinter(graph)

    result = printer.tree(module)
    assert result == "test.py\n"


def test_single_level_tree():
    """Tree with one level of dependencies."""
    root = ModuleInfo("root.py")
    dep1 = ModuleInfo("dep1.py")
    dep2 = ModuleInfo("dep2.py")

    graph = {root: {dep1, dep2}}
    printer = TreePrinter(graph)

    expected = "root.py\n    dep1.py\n    dep2.py\n"
    result = printer.tree(root)
    assert result == expected


def test_multi_level_tree(module_a, module_b, module_c):
    """Tree with multiple levels of dependencies."""
    graph = {module_a: {module_b}, module_b: {module_c}}
    printer = TreePrinter(graph)

    expected = "module_a.py\n    module_b.py\n        module_c.py\n"
    result = printer.tree(module_a)
    assert result == expected


def test_tree_with_missing_dependency(module_a, module_b):
    """Tree where some nodes have no dependencies."""
    graph = {module_a: {module_b}}
    printer = TreePrinter(graph)

    expected = "module_a.py\n    module_b.py\n"
    result = printer.tree(module_a)
    assert result == expected


def test_tree_with_root_not_in_graph(module_a):
    """Tree where the root node isn't in the graph."""
    graph = {}
    printer = TreePrinter(graph)

    expected = "module_a.py\n"
    result = printer.tree(module_a)
    assert result == expected
