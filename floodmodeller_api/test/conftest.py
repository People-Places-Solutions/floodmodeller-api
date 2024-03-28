import os
from pathlib import Path
import pytest


@pytest.fixture(scope="session")
def test_workspace():
    return Path(os.path.dirname(__file__), "test_data")
