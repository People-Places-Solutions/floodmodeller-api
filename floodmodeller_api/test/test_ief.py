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
def exe_bin(tmpdir) -> Path:
    for exe in ["ISISf32.exe", "ISISf32_DoubleP.exe"]:
        exe_path = Path(tmpdir, exe)
        exe_path.touch()
    return Path(tmpdir)


def test_ief_open_does_not_change_data(ief: IEF, data_before: str):
    """IEF: Test str representation equal to ief file with no changes"""
    assert ief._write() == data_before


@pytest.mark.parametrize(
    ("precision", "exe"),
    [
        ("DEFAULT", "ISISf32.exe"),
        ("SINGLE", "ISISf32.exe"),
        ("DOUBLE", "ISISf32_DoubleP.exe"),
    ],
)
def test_simulate(ief: IEF, ief_fp: Path, exe_bin: Path, precision: str, exe: str):
    with patch("floodmodeller_api.ief.Popen") as p_open:
        exe_path = Path(exe_bin, exe)
        ief.simulate(enginespath=str(exe_bin), precision=precision)
        p_open.assert_called_once_with(f'"{exe_path}" -sd "{ief_fp}"', cwd=str(ief_fp.parent))
