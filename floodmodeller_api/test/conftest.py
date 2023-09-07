import pytest
import os


@pytest.fixture(scope="session")
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")
