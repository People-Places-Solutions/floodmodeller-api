from pathlib import Path

import pytest

from floodmodeller_api import ZZX


@pytest.fixture
def zzx_fp(test_workspace):
    return Path(test_workspace, "network.zzx")


def test_load_zzx_using_dll(zzx_fp):
    ZZX(zzx_fp)


if __name__ == "__main__":
    pytest.main([__file__])
