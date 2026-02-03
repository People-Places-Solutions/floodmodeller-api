from __future__ import annotations

from pathlib import Path

import pytest

def parameterise_glob(glob_string: str, path: Path | None = None) -> list[Path]:
    if path is None:
        path = Path(Path(__file__).parent / "test_data")
    return path.glob(glob_string)


def id_from_path(path: Path) -> str:
    return f"{path.name}"
