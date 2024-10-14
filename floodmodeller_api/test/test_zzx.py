from pathlib import Path

import pytest

from floodmodeller_api import ZZX


def test_zzx(test_workspace):
    zzx = ZZX(Path(test_workspace, "network.zzx"))
    df = zzx.to_dataframe()
    pass


if __name__ == "__main__":
    pytest.main([__file__, "-s"])
