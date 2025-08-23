import tempfile
from pathlib import Path
from textwrap import dedent

from depgraph.visitors.call_tree import analyze_project_call_tree


def test_multi_file_project_call_tree(tmp_path):
    """Analyzes call tree across multiple files in a project."""

    # Create a temporary project structure
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()

    # File 1: main.py (entry point)
    main_py = project_dir / "main.py"
    main_py.write_text(
        dedent("""
        from utils import calculate_score
        from processors import process_user_data, batch_processor
        from game import GameEngine
        
        def main():
            # Direct call to process_user_data
            result = process_user_data(123, ["a", "b", "c"])
            
            # Direct call to batch_processor
            batch_results = batch_processor([{"value": 10}, {"value": 20}])
            
            # Using GameEngine
            engine = GameEngine()
            engine.evaluate_player({"level": 7, "points": 200})
            
            return result, batch_results
        
        def validate_and_score(input_value):
            if input_value > 0:
                return calculate_score(input_value, 0.8)
            return 0
    """)
    )

    # File 2: utils.py (utility functions)
    utils_py = project_dir / "utils.py"
    utils_py.write_text(
        dedent("""
        def calculate_score(value, multiplier=1.0):
            '''Target function: Calculates a score.'''
            return value * multiplier * 100
        
        def helper_function(x):
            # Internal call to calculate_score
            return calculate_score(x * 2, 1.5)
    """)
    )

    # File 3: processors.py (processing functions)
    processors_py = project_dir / "processors.py"
    processors_py.write_text(
        dedent("""
        from utils import calculate_score
        
        def process_user_data(user_id, data):
            base_value = len(data)
            score = calculate_score(base_value, 1.5)
            return {"user_id": user_id, "score": score}
        
        def batch_processor(items):
            results = []
            for item in items:
                item_score = calculate_score(item["value"])
                results.append(item_score)
            return results
    """)
    )

    # File 4: game.py (game logic)
    game_py = project_dir / "game.py"
    game_py.write_text(
        dedent("""
        from utils import calculate_score
        
        class GameEngine:
            def evaluate_player(self, player):
                if player["level"] > 5:
                    return calculate_score(value=player["points"], multiplier=2.0)
                else:
                    return calculate_score(player["points"], multiplier=0.5)
            
            def tournament_score(self, players):
                total = sum(p["points"] for p in players)
                return calculate_score(total / len(players)) if players else 0
    """)
    )

    # File 5: analytics.py (analytics that uses processors)
    analytics_py = project_dir / "analytics.py"
    analytics_py.write_text(
        dedent("""
        from processors import process_user_data
        
        def analytics_report(data):
            # Calls process_user_data which calls calculate_score
            processed = process_user_data(data["user"], data["metrics"])
            return {"report": processed, "timestamp": "2024-01-01"}
        
        def generate_batch_report(users):
            reports = []
            for user in users:
                report = analytics_report({"user": user["id"], "metrics": user["data"]})
                reports.append(report)
            return reports
    """)
    )

    # Analyze the call tree for calculate_score
    result = analyze_project_call_tree(str(project_dir), "calculate_score")

    # Verify structure
    assert result["target_function"] == "calculate_score"
    assert "direct_callers" in result

    # Extract caller info for assertions
    caller_names = {caller["name"] for caller in result["direct_callers"]}
    caller_files = {caller["file"] for caller in result["direct_callers"]}

    # Should find direct callers across multiple files
    expected_callers = {
        "validate_and_score",  # from main.py
        "helper_function",  # from utils.py
        "process_user_data",  # from processors.py
        "batch_processor",  # from processors.py
        "evaluate_player",  # from game.py
        "tournament_score",  # from game.py
    }
    assert caller_names == expected_callers

    # Verify files are correctly identified
    expected_files = {"main.py", "utils.py", "processors.py", "game.py"}
    assert expected_files.issubset(caller_files)

    # Check that process_user_data has correct callers (indirect callers)
    process_user_caller = next(
        c for c in result["direct_callers"] if c["name"] == "process_user_data"
    )
    assert len(process_user_caller["callers"]) > 0

    indirect_caller_names = {c["name"] for c in process_user_caller["callers"]}
    assert "analytics_report" in indirect_caller_names

    # Check that analytics_report has generate_batch_report as a caller
    analytics_caller = next(
        c for c in process_user_caller["callers"] if c["name"] == "analytics_report"
    )
    assert len(analytics_caller["callers"]) > 0
    assert analytics_caller["callers"][0]["name"] == "generate_batch_report"

    # Verify call sites preserve arguments
    validate_caller = next(
        c for c in result["direct_callers"] if c["name"] == "validate_and_score"
    )
    assert len(validate_caller["call_sites"]) == 1
    assert validate_caller["call_sites"][0]["arguments"]["positional"] == [
        "input_value",
        "0.8",
    ]

    # Check evaluate_player has multiple call sites (if/else branches)
    evaluate_caller = next(
        c for c in result["direct_callers"] if c["name"] == "evaluate_player"
    )
    assert len(evaluate_caller["call_sites"]) == 2


def test_handles_import_variations(tmp_path):
    """Handles different import patterns correctly."""

    project_dir = tmp_path / "import_test"
    project_dir.mkdir()

    # File with target function
    utils_py = project_dir / "utils.py"
    utils_py.write_text(
        dedent("""
        def target_func(x):
            return x * 2
    """)
    )

    # Different import patterns
    imports_py = project_dir / "imports.py"
    imports_py.write_text(
        dedent("""
        # Different import styles
        from utils import target_func
        from utils import target_func as renamed_target
        import utils
        
        def caller1():
            return target_func(1)  # Direct import
        
        def caller2():
            return renamed_target(2)  # Renamed import
        
        def caller3():
            return utils.target_func(3)  # Module.function
    """)
    )

    result = analyze_project_call_tree(str(project_dir), "target_func")

    caller_names = {caller["name"] for caller in result["direct_callers"]}
    # Should find all three callers despite different import styles
    assert caller_names == {"caller1", "caller2", "caller3"}


def test_handles_nested_directories(tmp_path):
    """Handles projects with nested directory structures."""

    project_dir = tmp_path / "nested_project"
    project_dir.mkdir()

    # Create nested structure
    core_dir = project_dir / "core"
    core_dir.mkdir()
    utils_dir = project_dir / "utils"
    utils_dir.mkdir()

    # Target function in nested directory
    target_py = utils_dir / "calculations.py"
    target_py.write_text(
        dedent("""
        def compute(value):
            return value * 100
    """)
    )

    # Caller in different nested directory
    caller_py = core_dir / "processor.py"
    caller_py.write_text(
        dedent("""
        from utils.calculations import compute
        
        def process_data(data):
            return compute(len(data))
    """)
    )

    # Caller in root directory
    main_py = project_dir / "main.py"
    main_py.write_text(
        dedent("""
        from utils.calculations import compute
        
        def main():
            return compute(42)
    """)
    )

    result = analyze_project_call_tree(str(project_dir), "compute")

    caller_names = {caller["name"] for caller in result["direct_callers"]}
    assert caller_names == {"process_data", "main"}

    # Check files are correctly identified with relative paths
    caller_files = {caller["file"] for caller in result["direct_callers"]}
    assert any("processor.py" in f for f in caller_files)
    assert any("main.py" in f for f in caller_files)
