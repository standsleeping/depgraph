import ast
import pytest
from depgraph.visitors.data.assignment_data import AssignmentData
from depgraph.visitors.data.scope_name import ScopeName


def test_assignment_data_creation():
    """AssignmentData objects can be created with valid inputs."""
    node = ast.Assign(
        targets=[ast.Name(id="x", ctx=ast.Store())],
        value=ast.Constant(value=1),
    )

    assignment = AssignmentData(name="x", node=node, type="basic", scope_name=ScopeName("<module>"))

    assert assignment.name == "x"
    assert isinstance(assignment.node, ast.Assign)
    assert assignment.type == "basic"
    assert assignment.scope_name == ScopeName("<module>")


def test_assignment_data_invalid_type():
    """AssignmentData raises error with invalid assignment type."""
    node = ast.Assign(
        targets=[ast.Name(id="x", ctx=ast.Store())],
        value=ast.Constant(value=1),
    )

    with pytest.raises(TypeError):
        AssignmentData(
            name="x",
            node=node,
            type="some-invalid-type",  # type: ignore
            scope_name=ScopeName("<module>"),
        )
