from __future__ import annotations

from pathlib import Path

import pytest

def parameterise_glob(glob_string: str) -> list[Path]:
    return (Path(__file__).parent / "test_data").glob(glob_string)

def id_from_path(path: Path) -> str:
    return f"{path.name}"