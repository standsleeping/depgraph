import ast
from textwrap import dedent
from depgraph.scope_visitor import ScopeVisitor
from depgraph.scope_data import ScopeInfo


def test_module_scope():
    """Module-level scope is correctly identified."""
    code = "x = 1"
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "<module>" in visitor.scopes
    scope_info = visitor.scopes["<module>"]
    assert scope_info.type == "module"


def test_function_scope():
    """Function scope is correctly identified."""
    code = dedent("""
        def my_function():
            pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "<module>.my_function" in visitor.scopes
    scope_info = visitor.scopes["<module>.my_function"]
    assert scope_info.type == "function"


def test_class_scope():
    """Class scope is correctly identified."""
    code = dedent("""
        class MyClass:
            pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "<module>.MyClass" in visitor.scopes
    scope_info = visitor.scopes["<module>.MyClass"]
    assert scope_info.type == "class"


def test_nested_scopes():
    """Nested functions and classes create proper scope hierarchies."""
    code = dedent("""
        def outer():
            class Inner:
                def method(): 
                    pass
    """)
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    assert set(visitor.scopes.keys()) == {
        "<module>",
        "<module>.outer",
        "<module>.outer.Inner",
        "<module>.outer.Inner.method",
    }

    module_scope = visitor.scopes["<module>"]
    assert module_scope.parent is None

    outer_scope = visitor.scopes["<module>.outer"]
    assert outer_scope.parent == "<module>"
    assert outer_scope.type == "function"

    inner_scope = visitor.scopes["<module>.outer.Inner"]
    assert inner_scope.parent == "<module>.outer"
    assert inner_scope.type == "class"

    method_scope = visitor.scopes["<module>.outer.Inner.method"]
    assert method_scope.parent == "<module>.outer.Inner"
    assert method_scope.type == "function"


def test_async_function():
    """Async functions create proper scopes."""
    code = dedent("""
        async def handler():
            pass
    """)
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    assert "<module>.handler" in visitor.scopes
    handler_scope = visitor.scopes["<module>.handler"]
    assert handler_scope.type == "async_function"
    assert handler_scope.parent == "<module>"


def test_lambda_scope():
    """Lambda expressions create proper scopes."""
    code = "f = lambda x: x + 1"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    assert "<module>.<lambda_line_1>" in visitor.scopes
    lambda_scope = visitor.scopes["<module>.<lambda_line_1>"]
    assert lambda_scope.type == "lambda"
    assert lambda_scope.parent == "<module>"


def test_multiple_lambdas():
    """Multiple lambdas in the same scope get unique names based on line numbers."""
    code = dedent("""
        f = lambda x: x + 1
        g = lambda y: y * 2
    """)
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    lambda_scopes = [s for s in visitor.scopes.values() if s.type == "lambda"]
    assert len(lambda_scopes) == 2

    # Check that we have two distinct lambda scopes with correct line numbers
    lambda_names = {s.name for s in lambda_scopes}
    assert len(lambda_names) == 2
    assert "<module>.<lambda_line_2>" in lambda_names
    assert "<module>.<lambda_line_3>" in lambda_names

    # Verify parent relationships
    assert all(s.parent == "<module>" for s in lambda_scopes)


def test_scope_info_attributes():
    """ScopeInfo objects contain all required attributes."""
    visitor = ScopeVisitor()
    visitor.visit(ast.parse("def func(): pass"))

    func_scope = visitor.scopes["<module>.func"]
    assert isinstance(func_scope, ScopeInfo)
    assert func_scope.name == "<module>.func"
    assert isinstance(func_scope.node, ast.FunctionDef)
    assert func_scope.type == "function"
    assert func_scope.parent == "<module>"


def test_multiple_classes_and_functions():
    """Multiple classes and functions at different levels are handled correctly."""
    code = dedent("""
        def top_level():
            pass
            
        class FirstClass:
            def method1(self):
                pass
                
            def method2(self):
                pass
                
        class SecondClass:
            def method(self):
                def nested():
                    pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    expected_scopes = {
        "<module>",
        "<module>.top_level",
        "<module>.FirstClass",
        "<module>.FirstClass.method1",
        "<module>.FirstClass.method2",
        "<module>.SecondClass",
        "<module>.SecondClass.method",
        "<module>.SecondClass.method.nested",
    }

    assert set(visitor.scopes.keys()) == expected_scopes


def test_empty_module():
    """An empty module creates just the module scope."""
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(""))

    assert len(visitor.scopes) == 1
    assert "<module>" in visitor.scopes
    assert visitor.scopes["<module>"].type == "module"
    assert visitor.scopes["<module>"].parent is None
