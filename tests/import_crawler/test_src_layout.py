import tempfile
import shutil
from pathlib import Path
import pytest
from textwrap import dedent
from depgraph.import_crawler.dependency_graph import DependencyGraph
from depgraph.import_crawler.is_source_layout_package import is_src_layout_project
from depgraph.import_crawler.build_graph import build_graph
from depgraph.import_crawler.import_categorizer import ImportCategorizer
from depgraph.import_crawler.site_packages import find_project_site_packages
import sysconfig


@pytest.fixture
def sample_src_project():
    """Create a temporary src-layout project for testing."""
    # Create a temporary directory
    project_dir = Path(tempfile.mkdtemp())
    try:
        # Create a src-layout structure
        src_dir = project_dir / "src"
        package_dir = src_dir / "sample_package"

        # Create directories
        package_dir.mkdir(parents=True)
        (package_dir / "submodule").mkdir()

        # Create pyproject.toml
        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(
                dedent("""
            [build-system]
            requires = ["setuptools>=42", "wheel"]
            build-backend = "setuptools.build_meta"
            
            [project]
            name = "sample_package"
            version = "0.1.0"
            """)
            )

        # Create __init__.py files
        (package_dir / "__init__.py").touch()
        (package_dir / "submodule" / "__init__.py").touch()

        # Create a module that imports from another module in the package
        with open(package_dir / "main.py", "w") as f:
            f.write(
                dedent("""
            from sample_package.submodule.helper import helper_function
            
            def main_function():
                return helper_function()
            """)
            )

        # Create the imported module
        with open(package_dir / "submodule" / "helper.py", "w") as f:
            f.write(
                dedent("""
            def helper_function():
                return "Hello from helper"
            """)
            )

        yield project_dir
    finally:
        # Clean up the temporary directory
        shutil.rmtree(project_dir)


@pytest.fixture
def complex_src_project():
    """Create a temporary complex src-layout project with nested imports."""
    project_dir = Path(tempfile.mkdtemp())
    try:
        # Create a more complex project structure
        src_dir = project_dir / "src"
        package_dir = src_dir / "complex_package"

        # Create a deeper structure with multiple modules
        modules = [
            "module_a",
            "module_a/submodule_a1",
            "module_b",
            "module_b/submodule_b1",
            "module_b/submodule_b1/submodule_b1a",
        ]

        # Create directories and __init__.py files
        package_dir.mkdir(parents=True)
        (package_dir / "__init__.py").touch()

        for module in modules:
            module_dir = package_dir / module
            module_dir.mkdir(parents=True, exist_ok=True)
            (module_dir / "__init__.py").touch()

        # Create pyproject.toml
        with open(project_dir / "pyproject.toml", "w") as f:
            f.write(
                dedent("""
            [build-system]
            requires = ["setuptools>=42", "wheel"]
            build-backend = "setuptools.build_meta"
            
            [project]
            name = "complex_package"
            version = "0.1.0"
            """)
            )

        # Create modules with various import patterns

        # Module that imports from multiple other modules
        with open(package_dir / "main.py", "w") as f:
            f.write(
                dedent("""
            # Absolute imports from various levels
            from complex_package.module_a import function_a
            from complex_package.module_a.submodule_a1 import function_a1
            from complex_package.module_b.submodule_b1.submodule_b1a import deep_function
            
            # Relative import
            from .module_b import function_b
            
            def main_function():
                return {
                    "a": function_a(),
                    "a1": function_a1(),
                    "b": function_b(),
                    "deep": deep_function()
                }
            """)
            )

        # Create the imported modules
        with open(package_dir / "module_a" / "common.py", "w") as f:
            f.write(
                dedent("""
            def common_function():
                return "common function"
            """)
            )

        with open(package_dir / "module_a" / "__init__.py", "w") as f:
            f.write(
                dedent("""
            from .common import common_function
            
            def function_a():
                return "function_a using " + common_function()
            """)
            )

        with open(package_dir / "module_a" / "submodule_a1" / "__init__.py", "w") as f:
            f.write(
                dedent("""
            from ..common import common_function
            
            def function_a1():
                return "function_a1 using " + common_function()
            """)
            )

        with open(package_dir / "module_b" / "__init__.py", "w") as f:
            f.write(
                dedent("""
            def function_b():
                return "function_b"
            """)
            )

        with open(
            package_dir / "module_b" / "submodule_b1" / "submodule_b1a" / "__init__.py",
            "w",
        ) as f:
            f.write(
                dedent("""
            from complex_package.module_a.common import common_function
            
            def deep_function():
                return "deep_function using " + common_function()
            """)
            )

        yield project_dir
    finally:
        shutil.rmtree(project_dir)


# Helper function to setup common objects needed for tests
def setup_dependency_graph(file_path):
    """Setup a dependency graph with necessary objects for testing."""
    parent_path = file_path.parent
    visited_paths = set()

    # Get standard library paths
    paths = sysconfig.get_paths()
    stdlib_paths = set([Path(p) for p in paths.values()])

    # Get site-packages paths
    site_packages_paths = find_project_site_packages(parent_path)

    # Initialize the import categorizer
    stdlib_path_strs = set([p for p in paths.values()])
    import_categorizer = ImportCategorizer(stdlib_path_strs, site_packages_paths)

    # Create dependency graph
    graph = DependencyGraph(import_categorizer)

    return graph, visited_paths, stdlib_paths


# Basic tests using the simple src-layout project
def test_src_layout_detection(sample_src_project):
    """Detects src-layout projects."""
    main_file = sample_src_project / "src" / "sample_package" / "main.py"

    # Check if the project is a src-layout project
    assert is_src_layout_project(main_file.parent)


def test_import_resolution_in_src_layout(sample_src_project):
    """Imports are correctly resolved in a src-layout project."""
    main_file = sample_src_project / "src" / "sample_package" / "main.py"
    helper_file = (
        sample_src_project / "src" / "sample_package" / "submodule" / "helper.py"
    )

    # Setup necessary objects
    graph, visited_paths, stdlib_paths = setup_dependency_graph(main_file)

    # Build the graph with our file
    build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Check that the graph contains the dependency
    main_file_str = str(main_file)
    helper_file_str = str(helper_file)

    # Use the get_imports method
    imports = graph.get_imports(main_file_str)
    assert helper_file_str in imports


def test_complete_dependency_graph(sample_src_project):
    """The full dependency graph is built correctly for a src-layout project."""
    main_file = sample_src_project / "src" / "sample_package" / "main.py"
    helper_file = (
        sample_src_project / "src" / "sample_package" / "submodule" / "helper.py"
    )

    # Setup necessary objects
    graph, visited_paths, stdlib_paths = setup_dependency_graph(main_file)

    # Build the graph
    build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Check that both files are in the graph
    main_file_str = str(main_file)
    helper_file_str = str(helper_file)

    all_files = graph.get_all_files()
    assert main_file_str in all_files
    assert helper_file_str in all_files

    # Check the import relationship
    assert graph.imports(main_file_str, helper_file_str)
    assert graph.imported_by(helper_file_str, main_file_str)


# Advanced tests using the complex src-layout project
def test_complex_import_resolution(complex_src_project):
    """Complex import patterns are correctly resolved in a src-layout project."""
    main_file = complex_src_project / "src" / "complex_package" / "main.py"

    # Setup necessary objects
    graph, visited_paths, stdlib_paths = setup_dependency_graph(main_file)

    # Build the graph
    build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Expected files that should be imported by main.py
    expected_imports = [
        str(
            complex_src_project / "src" / "complex_package" / "module_a" / "__init__.py"
        ),
        str(
            complex_src_project
            / "src"
            / "complex_package"
            / "module_a"
            / "submodule_a1"
            / "__init__.py"
        ),
        str(
            complex_src_project / "src" / "complex_package" / "module_b" / "__init__.py"
        ),
        str(
            complex_src_project
            / "src"
            / "complex_package"
            / "module_b"
            / "submodule_b1"
            / "submodule_b1a"
            / "__init__.py"
        ),
    ]

    # Get all imports from the main file
    imports = graph.get_imports(str(main_file))

    # Check that each expected import is in the dependencies
    for expected_import in expected_imports:
        assert expected_import in imports


def test_transitive_dependencies(complex_src_project):
    """Crawler correctly identifies transitive dependencies."""
    main_file = complex_src_project / "src" / "complex_package" / "main.py"
    common_file = (
        complex_src_project / "src" / "complex_package" / "module_a" / "common.py"
    )

    # Setup necessary objects
    graph, visited_paths, stdlib_paths = setup_dependency_graph(main_file)

    # Build the graph
    build_graph(
        file_path=main_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Check if there's a transitive dependency from main to common
    assert graph.has_transitive_dependency(str(main_file), str(common_file))


def test_circular_dependencies(complex_src_project):
    """Handles circular dependencies."""
    # Create a circular dependency between two modules
    module_a_file = (
        complex_src_project / "src" / "complex_package" / "module_a" / "__init__.py"
    )
    module_b_file = (
        complex_src_project / "src" / "complex_package" / "module_b" / "__init__.py"
    )

    # Modify module_b to import from module_a
    with open(module_b_file, "w") as f:
        f.write(
            dedent("""
        from complex_package.module_a import function_a
        
        def function_b():
            return "function_b calls " + function_a()
        """)
        )

    # Modify module_a to import from module_b (creating circular dependency)
    with open(module_a_file, "w") as f:
        f.write(
            dedent("""
        from .common import common_function
        from complex_package.module_b import function_b
        
        def function_a():
            return "function_a using " + common_function() + " and " + function_b()
        """)
        )

    # Setup necessary objects
    graph, visited_paths, stdlib_paths = setup_dependency_graph(module_a_file)

    # Build the graph
    build_graph(
        file_path=module_a_file,
        graph=graph,
        visited_paths=visited_paths,
        stdlib_paths=stdlib_paths,
    )

    # Check that both modules import each other (circular dependency)
    module_a_str = str(module_a_file)
    module_b_str = str(module_b_file)

    # Check both import directions
    assert graph.imports(module_a_str, module_b_str)
    assert graph.imports(module_b_str, module_a_str)
