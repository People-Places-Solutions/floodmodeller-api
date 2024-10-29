from pathlib import Path
from unittest.mock import patch

import pytest


@pytest.fixture(scope="session")
def test_workspace() -> Path:
    return Path(__file__).parent / "test_data"


@pytest.fixture()
def log_timeout():
    with patch("floodmodeller_api.logs.lf.LOG_TIMEOUT", new=0):
        yield
