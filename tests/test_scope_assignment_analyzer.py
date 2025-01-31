import ast
from depgraph.assignment_analyzer import ScopeAssignmentAnalyzer
from depgraph.scope_data import ScopeInfo
from tests.conftest import create_test_file


def test_analyze_module_scope(tmp_path):
    """Analyzing assignments at module level."""
    content = """
        x = 1
        y += 2
        z: int = 3
    """
    test_file = create_test_file(tmp_path, content)

    module = ast.parse(test_file.read_text())
    scope = ScopeInfo(name="<module>", node=module, type="module")

    analyzer = ScopeAssignmentAnalyzer()
    assignments = analyzer.analyze_scope(scope)

    assert len(assignments) == 3
    assert {a.name for a in assignments} == {"x", "y", "z"}
    assert {a.type for a in assignments} == {"basic", "augmented", "annotated"}


def test_analyze_function_scope(tmp_path):
    """Analyzing assignments within a function scope."""
    content = """
        def func():
            x = 1
            y += 2
            z: int = 3
    """
    test_file = create_test_file(tmp_path, content)

    module = ast.parse(test_file.read_text())
    function_node = module.body[0]
    scope = ScopeInfo(
        name="func",
        node=function_node,
        type="function",
        parent="<module>",
    )

    analyzer = ScopeAssignmentAnalyzer()
    assignments = analyzer.analyze_scope(scope)

    assert len(assignments) == 3
    assert {a.name for a in assignments} == {"x", "y", "z"}


def test_analyze_empty_scope(tmp_path):
    """Analyzing a scope with no assignments."""
    content = """
        def empty():
            pass
    """
    test_file = create_test_file(tmp_path, content)

    module = ast.parse(test_file.read_text())
    function_node = module.body[0]
    scope = ScopeInfo(
        name="empty",
        node=function_node,
        type="function",
        parent="<module>",
    )

    analyzer = ScopeAssignmentAnalyzer()
    assignments = analyzer.analyze_scope(scope)

    assert len(assignments) == 0
