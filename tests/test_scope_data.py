import ast
import pytest
from depgraph.data.scope_info import ScopeInfo
from depgraph.data.scope_name import ScopeName


def test_valid_module_scope():
    """Module scope can be created with valid parameters."""
    node = ast.Module(body=[], type_ignores=[])
    scope = ScopeInfo(name=ScopeName("<module>"), node=node, type="module")
    assert str(scope.name) == "<module>"
    assert scope.type == "module"
    assert scope.parent is None


def test_valid_function_scope():
    """Function scope can be created with valid parameters."""
    node = ast.FunctionDef(
        name="func",
        args=ast.arguments([], [], None, [], [], None, []),
        body=[],
        decorator_list=[],
    )
    scope = ScopeInfo(
        name=ScopeName("<module>.func"),
        node=node,
        type="function",
        parent=ScopeName("<module>"),
    )
    assert str(scope.name) == "<module>.func"
    assert scope.type == "function"
    assert str(scope.parent) == "<module>"


def test_invalid_scope_type():
    """Creating scope with invalid type raises TypeError."""
    node = ast.Module(body=[], type_ignores=[])
    with pytest.raises(TypeError, match="Invalid scope type"):
        ScopeInfo(
            name=ScopeName("<module>"),
            node=node,
            type="invalid_type",  # type: ignore
        )


def test_mismatched_node_type():
    """Creating scope with mismatched node type raises TypeError."""
    node = ast.ClassDef(
        name="MyClass",
        bases=[],
        keywords=[],
        body=[],
        decorator_list=[],
    )
    with pytest.raises(TypeError, match="Invalid node type for scope type"):
        ScopeInfo(
            name=ScopeName("<module>.func"),
            node=node,
            type="function",
            parent=ScopeName("<module>"),
        )


def test_empty_scope_name():
    """Creating scope with empty name raises ValueError."""
    node = ast.Module(body=[], type_ignores=[])
    with pytest.raises(ValueError, match="Scope name cannot be empty"):
        ScopeInfo(
            name=ScopeName(""),
            node=node,
            type="module",
        )


def test_invalid_module_name():
    """Creating module scope with invalid name raises ValueError."""
    node = ast.Module(body=[], type_ignores=[])
    with pytest.raises(ValueError, match="Module scope must be named"):
        ScopeInfo(
            name=ScopeName("not_module"),
            node=node,
            type="module",
        )


def test_missing_parent():
    """Creating non-module scope without parent raises ValueError."""
    node = ast.FunctionDef(
        name="func",
        args=ast.arguments([], [], None, [], [], None, []),
        body=[],
        decorator_list=[],
    )
    with pytest.raises(ValueError, match="must have a parent scope"):
        ScopeInfo(
            name=ScopeName("func"),
            node=node,
            type="function",
        )
