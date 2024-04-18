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
    ("precision", "amend", "exe"),
    [
        ("DEFAULT", False, "ISISf32.exe"),
        ("DEFAULT", True, "ISISf32_DoubleP.exe"),
        ("SINGLE", False, "ISISf32.exe"),
        ("SINGLE", True, "ISISf32.exe"),
        ("DOUBLE", False, "ISISf32_DoubleP.exe"),
        ("DOUBLE", True, "ISISf32_DoubleP.exe"),
    ],
)
def test_simulate(ief: IEF, ief_fp: Path, exe_bin: Path, precision: str, amend: bool, exe: str):
    if amend:
        ief.launchdoubleprecisionversion = "1"
    with patch("floodmodeller_api.ief.Popen") as p_open:
        exe_path = Path(exe_bin, exe)
        ief.simulate(enginespath=str(exe_bin), precision=precision)
        p_open.assert_called_once_with(f'"{exe_path}" -sd "{ief_fp}"', cwd=str(ief_fp.parent))


def test_simulate_error_without_bin(tmpdir, ief: IEF):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: \d\.\d\.\d\..*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: Flood Modeller non-default engine path not found! .*"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(Exception, match=msg):
        ief.simulate(enginespath=str(Path(tmpdir, "bin")))


def test_simulate_error_without_exe(tmpdir, ief: IEF):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: \d\.\d\.\d\..*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: Flood Modeller engine not found! Expected location: .*"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(Exception, match=msg):
        ief.simulate(enginespath=str(tmpdir))


def test_simulate_error_without_save():
    ief = IEF()
    ief._filepath = None
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: \d\.\d\.\d\..*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: IEF must be saved to a specific filepath before simulate\(\) can be called\."
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(Exception, match=msg):
        ief.simulate()
