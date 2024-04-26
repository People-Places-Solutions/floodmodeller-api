from pathlib import Path
from unittest.mock import call, patch

import pytest

from floodmodeller_api import IEF
from floodmodeller_api.util import FloodModellerAPIError


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


@pytest.fixture()
def p_open():
    with patch("floodmodeller_api.ief.Popen") as p_open:
        yield p_open


@pytest.fixture()
def sleep():
    with patch("floodmodeller_api.ief.time.sleep") as sleep:
        yield sleep


def test_ief_open_does_not_change_data(ief: IEF, data_before: str):
    """IEF: Test str representation equal to ief file with no changes"""
    assert ief._write() == data_before


@pytest.mark.usefixtures("log_timeout")
@pytest.mark.parametrize(
    ("precision", "method", "amend", "exe"),
    [
        ("DEFAULT", "WAIT", False, "ISISf32.exe"),
        ("DEFAULT", "WAIT", True, "ISISf32_DoubleP.exe"),
        ("SINGLE", "WAIT", False, "ISISf32.exe"),
        ("SINGLE", "WAIT", True, "ISISf32.exe"),
        ("DOUBLE", "WAIT", False, "ISISf32_DoubleP.exe"),
        ("DOUBLE", "WAIT", True, "ISISf32_DoubleP.exe"),
        ("DEFAULT", "RETURN_PROCESS", False, "ISISf32.exe"),
        ("DEFAULT", "RETURN_PROCESS", True, "ISISf32_DoubleP.exe"),
        ("SINGLE", "RETURN_PROCESS", False, "ISISf32.exe"),
        ("SINGLE", "RETURN_PROCESS", True, "ISISf32.exe"),
        ("DOUBLE", "RETURN_PROCESS", False, "ISISf32_DoubleP.exe"),
        ("DOUBLE", "RETURN_PROCESS", True, "ISISf32_DoubleP.exe"),
    ],
)
def test_simulate(
    ief: IEF,
    ief_fp: Path,
    exe_bin: Path,
    p_open,
    sleep,
    precision: str,
    method: str,
    amend: bool,
    exe: str,
):
    if amend:
        ief.launchdoubleprecisionversion = 1

    p_open.return_value.poll.side_effect = [None, None, 0]

    exe_path = Path(exe_bin, exe)
    ief.simulate(method=method, precision=precision, enginespath=str(exe_bin))

    p_open.assert_called_once_with(f'"{exe_path}" -sd "{ief_fp}"', cwd=str(ief_fp.parent))

    if method == "WAIT":
        assert p_open.return_value.poll.call_count == 3
        assert sleep.call_args_list[-3:] == [call(0.1), call(1), call(1)]


def test_simulate_error_without_bin(tmpdir, ief: IEF):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: Flood Modeller non-default engine path not found! .*"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        ief.simulate(enginespath=str(Path(tmpdir, "bin")))


def test_simulate_error_without_exe(tmpdir, ief: IEF):
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: Flood Modeller engine not found! Expected location: .*"
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        ief.simulate(enginespath=str(tmpdir))


def test_simulate_error_without_save():
    ief = IEF()
    ief._filepath = None
    msg = (
        r"\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
        r"\nAPI Error: Problem encountered when trying to simulate IEF file .*\."
        r"\n"
        r"\nDetails: .*-floodmodeller_api/ief\.py-\d+"
        r"\nMsg: IEF must be saved to a specific filepath before simulate\(\) can be called\."
        r"\n"
        r"\nFor additional support, go to: https://github\.com/People-Places-Solutions/floodmodeller-api"
    )
    with pytest.raises(FloodModellerAPIError, match=msg):
        ief.simulate()
