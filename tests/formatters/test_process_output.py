import ast
from pathlib import Path
from depgraph.processors.functions.format_analysis import (
    format_analysis as process_output,
)
from depgraph.processors.data.file_analysis import FileAnalysis
from depgraph.visitors.data.scope_info import ScopeInfo
from depgraph.visitors.data.scope_name import ScopeName
from depgraph.visitors.data.assignment_data import AssignmentData


def test_process_output_basic():
    """With no filter or assignments, the output is the entire module."""
    # Create a simple module with one class and one function
    module_node = ast.Module(body=[], type_ignores=[])

    class_node = ast.ClassDef(
        name="TestClass",
        bases=[],
        keywords=[],
        body=[],
        decorator_list=[],
    )

    func_node = ast.FunctionDef(
        name="test_func",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[],
        decorator_list=[],
    )

    # Create scope info objects
    module_scope = ScopeInfo(
        name=ScopeName("<module>"), node=module_node, type="module"
    )

    class_scope = ScopeInfo(
        name=ScopeName("<module>.TestClass"),
        node=class_node,
        type="class",
        parent=ScopeName("<module>"),
    )

    func_scope = ScopeInfo(
        name=ScopeName("<module>.test_func"),
        node=func_node,
        type="function",
        parent=ScopeName("<module>"),
    )

    # Create file analysis
    analysis = FileAnalysis(
        abs_file_path=Path("test.py"),
        ast_tree=module_node,
        scopes={
            ScopeName("<module>"): module_scope,
            ScopeName("<module>.TestClass"): class_scope,
            ScopeName("<module>.test_func"): func_scope,
        },
    )

    # Process the output
    result = process_output(analysis=analysis)

    # Check the result
    assert "scopes" in result
    assert "assignments" in result
    assert result["scopes"]["name"] == "<module>"
    assert result["scopes"]["type"] == "module"
    assert len(result["scopes"]["children"]) == 2

    # Check that children are properly included and sorted
    children_names = [child["name"] for child in result["scopes"]["children"]]
    assert children_names == ["<module>.TestClass", "<module>.test_func"]
    assert result["assignments"] == []


def test_process_output_with_filter():
    """With a scope filter, the output is the module and the filtered scope."""
    # Create a simple module with one class and one method in that class
    module_node = ast.Module(body=[], type_ignores=[])

    class_node = ast.ClassDef(
        name="TestClass",
        bases=[],
        keywords=[],
        body=[],
        decorator_list=[],
    )

    method_node = ast.FunctionDef(
        name="test_method",
        args=ast.arguments(
            posonlyargs=[],
            args=[],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
        ),
        body=[],
        decorator_list=[],
    )

    # Create scope info objects
    module_scope = ScopeInfo(
        name=ScopeName("<module>"), node=module_node, type="module"
    )

    class_scope = ScopeInfo(
        name=ScopeName("<module>.TestClass"),
        node=class_node,
        type="class",
        parent=ScopeName("<module>"),
    )

    method_scope = ScopeInfo(
        name=ScopeName("<module>.TestClass.test_method"),
        node=method_node,
        type="function",
        parent=ScopeName("<module>.TestClass"),
    )

    # Create file analysis
    analysis = FileAnalysis(
        abs_file_path=Path("test.py"),
        ast_tree=module_node,
        scopes={
            ScopeName("<module>"): module_scope,
            ScopeName("<module>.TestClass"): class_scope,
            ScopeName("<module>.TestClass.test_method"): method_scope,
        },
    )

    # Process the output with a filter on TestClass
    result = process_output(analysis=analysis, scope_filter="<module>.TestClass")

    # Check the result
    assert "scopes" in result
    assert result["scopes"]["name"] == "<module>.TestClass"
    assert result["scopes"]["type"] == "class"
    assert len(result["scopes"]["children"]) == 1
    assert result["scopes"]["children"][0]["name"] == "<module>.TestClass.test_method"


def test_process_output_with_invalid_filter():
    """With an invalid scope filter, the output is an error message."""
    # Create a simple module
    module_node = ast.Module(body=[], type_ignores=[])

    module_scope = ScopeInfo(
        name=ScopeName("<module>"), node=module_node, type="module"
    )

    # Create file analysis
    analysis = FileAnalysis(
        abs_file_path=Path("test.py"),
        scopes={
            ScopeName("<module>"): module_scope,
        },
        ast_tree=module_node,
    )

    # Process the output with an invalid filter
    result = process_output(analysis=analysis, scope_filter="<module>.NonExistentScope")

    # Check for the error message
    assert "error" in result
    assert "not found" in result["error"]


def test_process_output_with_assignments():
    """With assignments, the output is the assignments."""
    # Create a simple module
    module_node = ast.Module(body=[], type_ignores=[])

    # Create assignments
    assign_node1 = ast.Assign(
        targets=[ast.Name(id="x", ctx=ast.Store())],
        value=ast.Constant(value=1),
    )

    assign_node2 = ast.AugAssign(
        target=ast.Name(id="y", ctx=ast.Store()),
        op=ast.Add(),
        value=ast.Constant(value=2),
    )

    assign_node3 = ast.AnnAssign(
        target=ast.Name(id="z", ctx=ast.Store()),
        annotation=ast.Name(id="int", ctx=ast.Load()),
        value=ast.Constant(value=3),
        simple=1,
    )

    # Create assignment data
    assignments = [
        AssignmentData(
            name="x",
            node=assign_node1,
            type="basic",
            scope_name="<module>",
        ),
        AssignmentData(
            name="y",
            node=assign_node2,
            type="augmented",
            scope_name="<module>",
        ),
        AssignmentData(
            name="z",
            node=assign_node3,
            type="annotated",
            scope_name="<module>",
        ),
    ]

    # Create file analysis
    analysis = FileAnalysis(
        abs_file_path=Path("test.py"),
        ast_tree=module_node,
        scopes={
            ScopeName("<module>"): ScopeInfo(
                name=ScopeName("<module>"), node=module_node, type="module"
            ),
        },
    )

    # Process the output with assignments
    result = process_output(analysis=analysis, assignments=assignments)

    # Check the assignments in the output
    assert len(result["assignments"]) == 3

    # Assignments should be sorted by name
    assert result["assignments"][0]["name"] == "x"
    assert result["assignments"][0]["type"] == "basic"
    assert result["assignments"][0]["operator"] == "="

    assert result["assignments"][1]["name"] == "y"
    assert result["assignments"][1]["type"] == "augmented"
    assert result["assignments"][1]["operator"] == "+=/-=/*=/etc"

    assert result["assignments"][2]["name"] == "z"
    assert result["assignments"][2]["type"] == "annotated"
    assert result["assignments"][2]["operator"] == ": type ="
