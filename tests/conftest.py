from pathlib import Path
from textwrap import dedent


def create_test_file(tmp_path: Path, content: str) -> Path:
    """Create a test file with given content.

    Args:
        tmp_path: Pytest fixture providing temporary directory path
        content: Python source code content to write

    Returns:
        Path to the created test file
    """
    test_file = tmp_path / "test.py"
    test_file.write_text(dedent(content))
    return test_file
