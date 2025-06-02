import ast
from depgraph.visitors.assignment_visitor import AssignmentVisitor
from depgraph.visitors.data.scope_name import ScopeName
from tests.conftest import create_test_file


def test_basic_assignment(tmp_path):
    """Visitor captures basic assignments."""
    content = """
        x = 1
    """

    test_file = create_test_file(tmp_path, content)

    tree = ast.parse(test_file.read_text())
    visitor = AssignmentVisitor(scope_name=ScopeName("<module>"))
    visitor.visit(tree)

    assert len(visitor.assignments) == 1
    assignment = visitor.assignments[0]
    assert assignment.name == "x"
    assert assignment.type == "basic"
    assert isinstance(assignment.node, ast.Assign)
    assert assignment.scope_name == ScopeName("<module>")


def test_augmented_assignment(tmp_path):
    """Visitor captures augmented assignments."""
    content = """
        x += 1
    """

    test_file = create_test_file(tmp_path, content)

    tree = ast.parse(test_file.read_text())
    visitor = AssignmentVisitor(scope_name=ScopeName("<module>"))
    visitor.visit(tree)

    assert len(visitor.assignments) == 1
    assignment = visitor.assignments[0]
    assert assignment.name == "x"
    assert assignment.type == "augmented"
    assert isinstance(assignment.node, ast.AugAssign)
    assert assignment.scope_name == ScopeName("<module>")


def test_annotated_assignment(tmp_path):
    """Visitor captures annotated assignments."""
    content = """
        x: int = 1
    """

    test_file = create_test_file(tmp_path, content)

    tree = ast.parse(test_file.read_text())
    visitor = AssignmentVisitor(scope_name=ScopeName("<module>"))
    visitor.visit(tree)

    assert len(visitor.assignments) == 1
    assignment = visitor.assignments[0]
    assert assignment.name == "x"
    assert assignment.type == "annotated"
    assert isinstance(assignment.node, ast.AnnAssign)
    assert assignment.scope_name == ScopeName("<module>")


def test_multiple_assignments(tmp_path):
    """Visitor captures multiple assignments in code."""
    content = """
        x = 1
        y += 2
        z: int = 3
    """

    test_file = create_test_file(tmp_path, content)

    tree = ast.parse(test_file.read_text())
    visitor = AssignmentVisitor(scope_name=ScopeName("<module>"))
    visitor.visit(tree)

    assert len(visitor.assignments) == 3
    assert {a.name for a in visitor.assignments} == {"x", "y", "z"}
    assert {a.type for a in visitor.assignments} == {"basic", "augmented", "annotated"}
    assert all(a.scope_name == ScopeName("<module>") for a in visitor.assignments)


def test_ignore_complex_assignments(tmp_path):
    """Visitor ignores assignments to non-Name nodes."""
    content = """
        a, b = 1, 2
        obj.attr = 3
        lst[0] = 4
    """

    test_file = create_test_file(tmp_path, content)

    tree = ast.parse(test_file.read_text())
    visitor = AssignmentVisitor(scope_name=ScopeName("<module>"))
    visitor.visit(tree)

    assert len(visitor.assignments) == 0
