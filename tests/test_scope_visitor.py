import ast
from textwrap import dedent
from depgraph.scope_visitor import ScopeVisitor


def test_module_scope():
    """Module-level scope is correctly identified."""
    code = "x = 1"
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "<module>" in visitor.scopes
    assert isinstance(visitor.scopes["<module>"], ast.Module)


def test_function_scope():
    """Function scope is correctly identified."""
    code = dedent("""
        def my_function():
            pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "my_function" in visitor.scopes
    assert isinstance(visitor.scopes["my_function"], ast.FunctionDef)


def test_class_scope():
    """Class scope is correctly identified."""
    code = dedent("""
        class MyClass:
            pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    assert "MyClass" in visitor.scopes
    assert isinstance(visitor.scopes["MyClass"], ast.ClassDef)


def test_nested_scopes():
    """Nested scopes are correctly identified and named."""
    code = dedent("""
        class MyClass:
            def method(self):
                def inner():
                    pass
    """)
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    expected_scopes = {"<module>", "MyClass", "MyClass.method", "MyClass.method.inner"}

    assert set(visitor.scopes.keys()) == expected_scopes
    assert isinstance(visitor.scopes["MyClass.method"], ast.FunctionDef)
    assert isinstance(visitor.scopes["MyClass.method.inner"], ast.FunctionDef)


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
        "top_level",
        "FirstClass",
        "FirstClass.method1",
        "FirstClass.method2",
        "SecondClass",
        "SecondClass.method",
        "SecondClass.method.nested",
    }

    assert set(visitor.scopes.keys()) == expected_scopes
