from pathlib import Path

import pytest

from floodmodeller_api import ZZN, ZZX


def test_load_zzx_using_dll(test_workspace):
    zzx = ZZX(Path(test_workspace, "network.zzx"))
    zzn = ZZN(Path(test_workspace, "network.zzn"))
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
