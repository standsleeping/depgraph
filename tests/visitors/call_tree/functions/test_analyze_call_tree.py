from textwrap import dedent

from depgraph.visitors.call_tree import analyze_call_tree


def test_finds_direct_callers():
    """Finds all direct callers of target function."""
    source_code = dedent("""
        def calculate_score(value, multiplier=1.0):
            return value * multiplier * 100

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

    result = analyze_call_tree(source_code, "calculate_score")

    assert result["target_function"] == "calculate_score"
    assert len(result["direct_callers"]) == 2

    caller_names = {caller["name"] for caller in result["direct_callers"]}
    assert caller_names == {"process_user_data", "batch_processor"}


def test_captures_arguments():
    """Captures positional and keyword arguments."""
    source_code = dedent("""
        def target_func(a, b, c=None):
            return a + b
        
        def caller1():
            return target_func(1, 2, c=3)
        
        def caller2():
            return target_func(x, y)
    """)

    result = analyze_call_tree(source_code, "target_func")

    # Check caller1 arguments
    caller1 = next(c for c in result["direct_callers"] if c["name"] == "caller1")
    args = caller1["call_sites"][0]["arguments"]
    assert args["positional"] == ["1", "2"]
    assert args["keyword"] == {"c": "3"}

    # Check caller2 arguments
    caller2 = next(c for c in result["direct_callers"] if c["name"] == "caller2")
    args = caller2["call_sites"][0]["arguments"]
    assert args["positional"] == ["x", "y"]
    assert args["keyword"] == {}


def test_handles_methods():
    """Handles method calls within classes."""
    source_code = dedent("""
        def calculate(x):
            return x * 2
            
        class Calculator:
            def compute(self, value):
                return calculate(value)
            
            def batch_compute(self, values):
                return [calculate(v) for v in values]
    """)

    result = analyze_call_tree(source_code, "calculate")

    caller_names = {caller["name"] for caller in result["direct_callers"]}
    assert "compute" in caller_names
    assert "batch_compute" in caller_names


def test_multiple_call_sites():
    """Handles functions with multiple calls to target."""
    source_code = dedent("""
        def target(x):
            return x * 2
            
        def caller():
            a = target(1)
            b = target(2)
            return a + b
    """)

    result = analyze_call_tree(source_code, "target")

    caller = result["direct_callers"][0]
    assert caller["name"] == "caller"
    assert len(caller["call_sites"]) == 2

    # Check both call sites have correct arguments
    assert caller["call_sites"][0]["arguments"]["positional"] == ["1"]
    assert caller["call_sites"][1]["arguments"]["positional"] == ["2"]
