import ast
from textwrap import dedent
from depgraph.visitors.scope_visitor import ScopeVisitor
from depgraph.visitors.data.scope_info import ScopeInfo
from depgraph.visitors.data.scope_name import ScopeName


def test_module_scope():
    """Module-level scope is correctly identified."""
    code = "x = 1"
    tree = ast.parse(code)
    visitor = ScopeVisitor()
    visitor.visit(tree)

    module_name = ScopeName("<module>")
    assert module_name in visitor.scopes
    scope_info = visitor.scopes[module_name]
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

    func_name = ScopeName("<module>.my_function")
    assert func_name in visitor.scopes
    scope_info = visitor.scopes[func_name]
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

    class_name = ScopeName("<module>.MyClass")
    assert class_name in visitor.scopes
    scope_info = visitor.scopes[class_name]
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

    expected_scopes = {
        ScopeName("<module>"),
        ScopeName("<module>.outer"),
        ScopeName("<module>.outer.Inner"),
        ScopeName("<module>.outer.Inner.method"),
    }

    assert set(visitor.scopes.keys()) == expected_scopes

    module_scope = visitor.scopes[ScopeName("<module>")]
    assert module_scope.parent is None

    outer_scope = visitor.scopes[ScopeName("<module>.outer")]
    assert str(outer_scope.parent) == "<module>"
    assert outer_scope.type == "function"

    inner_scope = visitor.scopes[ScopeName("<module>.outer.Inner")]
    assert str(inner_scope.parent) == "<module>.outer"
    assert inner_scope.type == "class"

    method_scope = visitor.scopes[ScopeName("<module>.outer.Inner.method")]
    assert str(method_scope.parent) == "<module>.outer.Inner"
    assert method_scope.type == "function"


def test_async_function():
    """Async functions create proper scopes."""
    code = dedent("""
        async def handler():
            pass
    """)
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    handler_name = ScopeName("<module>.handler")
    assert handler_name in visitor.scopes
    handler_scope = visitor.scopes[handler_name]
    assert handler_scope.type == "async_function"
    assert str(handler_scope.parent) == "<module>"


def test_lambda_scope():
    """Lambda expressions create proper scopes."""
    code = "f = lambda x: x + 1"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    lambda_name = ScopeName("<module>.<lambda_line_1>")
    assert lambda_name in visitor.scopes
    lambda_scope = visitor.scopes[lambda_name]
    assert lambda_scope.type == "lambda"
    assert str(lambda_scope.parent) == "<module>"


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
    lambda_names = {str(s.name) for s in lambda_scopes}
    assert len(lambda_names) == 2
    assert "<module>.<lambda_line_2>" in lambda_names
    assert "<module>.<lambda_line_3>" in lambda_names

    # Verify parent relationships
    assert all(str(s.parent) == "<module>" for s in lambda_scopes)


def test_scope_info_attributes():
    """ScopeInfo objects contain all required attributes."""
    visitor = ScopeVisitor()
    visitor.visit(ast.parse("def func(): pass"))

    func_name = ScopeName("<module>.func")
    func_scope = visitor.scopes[func_name]
    assert isinstance(func_scope, ScopeInfo)
    assert str(func_scope.name) == "<module>.func"
    assert isinstance(func_scope.node, ast.FunctionDef)
    assert func_scope.type == "function"
    assert str(func_scope.parent) == "<module>"


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
        ScopeName("<module>"),
        ScopeName("<module>.top_level"),
        ScopeName("<module>.FirstClass"),
        ScopeName("<module>.FirstClass.method1"),
        ScopeName("<module>.FirstClass.method2"),
        ScopeName("<module>.SecondClass"),
        ScopeName("<module>.SecondClass.method"),
        ScopeName("<module>.SecondClass.method.nested"),
    }

    assert set(visitor.scopes.keys()) == expected_scopes


def test_empty_module():
    """An empty module creates just the module scope."""
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(""))

    assert len(visitor.scopes) == 1
    module_name = ScopeName("<module>")
    assert module_name in visitor.scopes
    assert visitor.scopes[module_name].type == "module"
    assert visitor.scopes[module_name].parent is None


def test_list_comprehension():
    """List comprehensions create proper scopes."""
    code = "squares = [x*x for x in range(10)]"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    listcomp_name = ScopeName("<module>.<listcomp_line_1>")
    assert listcomp_name in visitor.scopes
    listcomp_scope = visitor.scopes[listcomp_name]
    assert listcomp_scope.type == "listcomp"
    assert str(listcomp_scope.parent) == "<module>"


def test_set_comprehension():
    """Set comprehensions create proper scopes."""
    code = "unique_squares = {x*x for x in range(10)}"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    setcomp_name = ScopeName("<module>.<setcomp_line_1>")
    assert setcomp_name in visitor.scopes
    setcomp_scope = visitor.scopes[setcomp_name]
    assert setcomp_scope.type == "setcomp"
    assert str(setcomp_scope.parent) == "<module>"


def test_dict_comprehension():
    """Dictionary comprehensions create proper scopes."""
    code = "squares_dict = {x: x*x for x in range(10)}"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    dictcomp_name = ScopeName("<module>.<dictcomp_line_1>")
    assert dictcomp_name in visitor.scopes
    dictcomp_scope = visitor.scopes[dictcomp_name]
    assert dictcomp_scope.type == "dictcomp"
    assert str(dictcomp_scope.parent) == "<module>"


def test_generator_expression():
    """Generator expressions create proper scopes."""
    code = "squares_gen = (x*x for x in range(10))"
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    genexpr_name = ScopeName("<module>.<genexpr_line_1>")
    assert genexpr_name in visitor.scopes
    genexpr_scope = visitor.scopes[genexpr_name]
    assert genexpr_scope.type == "genexpr"
    assert str(genexpr_scope.parent) == "<module>"


def test_nested_comprehensions():
    """Nested comprehensions create proper scope hierarchies."""
    code = dedent("""
        def outer():
            matrix = [[x*y for x in range(5)] for y in range(5)]
    """)
    visitor = ScopeVisitor()
    visitor.visit(ast.parse(code))

    scopes = [s for s in visitor.scopes.values() if s.type == "listcomp"]
    assert len(scopes) == 2

    assert str(scopes[0].name) == "<module>.outer.<listcomp_line_3>"
    assert str(scopes[1].name) == "<module>.outer.<listcomp_line_3>.<listcomp_line_3>"
