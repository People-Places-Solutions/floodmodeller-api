from pathlib import Path
from unittest.mock import patch

import pytest

from floodmodeller_api import IEF


@pytest.fixture()
def ief_fp(test_workspace: str) -> Path:
    return Path(test_workspace, "network.ief")


@pytest.fixture()
def ief(ief_fp: Path) -> IEF:
    return IEF(ief_fp)


@pytest.fixture()
def data_before(ief_fp: Path) -> str:
    with open(ief_fp) as ief_file:
        return ief_file.read()


@pytest.fixture()
def exe_path(tmpdir) -> Path:
    exe_path = Path(tmpdir, "ISISf32.exe")
    exe_path.touch()
    return exe_path


def test_ief_open_does_not_change_data(ief: IEF, data_before: str):
    """IEF: Test str representation equal to ief file with no changes"""
    assert ief._write() == data_before


def test_simulate(ief: IEF, ief_fp: Path, exe_path: Path, test_workspace: str):
    with patch("floodmodeller_api.ief.Popen") as p_open:
        ief.simulate(enginespath=exe_path.parent)
        assert p_open.call_args[0][0] == (f'"{exe_path}" -sd "{ief_fp}"')
        assert p_open.call_args[1]["cwd"] == test_workspace
