import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleInfo:
    """Information about a Python module."""

    full_path: str

    @property
    def file_name(self) -> str:
        """The module's file name without path."""
        return os.path.basename(self.full_path)

    @property
    def dir_name(self) -> str:
        """The directory containing this module."""
        return os.path.dirname(self.full_path)

    def __str__(self) -> str:
        return self.file_name

    def __repr__(self) -> str:
        return f"ModuleInfo(full_path={self.full_path})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ModuleInfo):
            return False
        return str(self.full_path) == str(other.full_path)

    def __hash__(self) -> int:
        return hash(self.full_path)