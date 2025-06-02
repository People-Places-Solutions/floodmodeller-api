from pathlib import Path
from unittest.mock import call, patch

import pytest

from floodmodeller_api import IEF
from floodmodeller_api.ief import FlowTimeProfile
from floodmodeller_api.util import FloodModellerAPIError


@pytest.fixture()
def ief_fp(test_workspace: Path) -> Path:
    return test_workspace / "network.ief"


@pytest.fixture()
def ief(ief_fp: Path) -> IEF:
    return IEF(ief_fp)


@pytest.fixture()
def multievent_ief(test_workspace: Path) -> IEF:
    return IEF(test_workspace / "multievent.ief")


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


def test_ief_read_doesnt_change_data(test_workspace, tmpdir):
    """IEF: Check all '.ief' files in folder by reading the _write() output into a new IEF instance and checking it stays the same."""
    # we use this instead of parameterise so it will just automatically test any ief in the test data.
    for ief_file in Path(test_workspace).glob("*.ief"):
        ief = IEF(ief_file)
        first_output = ief._write()
        new_path = Path(tmpdir) / "tmp.ief"
        ief.save(new_path)
        second_ief = IEF(new_path)
        assert ief == second_ief  # Checks equivalence on the class itself
        second_output = second_ief._write()
        assert first_output == second_output


def test_update_property(ief):
    """Check if updating a property is correctly reflected in _write"""
    ief.title = "updated_property"
    assert "Title=updated_property" in ief._write()


def test_delete_property(ief):
    del ief.slot
    assert "Slot=1" not in ief._write()


def test_add_new_group_property(ief):
    ief.FlowScaling1 = "test"
    assert "FlowScaling1=test" in ief._write()
    assert "[Boundary Adjustments]" in ief._write()


def test_add_flowtimeprofile(ief):
    prev_output = ief._write()
    ief.flowtimeprofiles = [FlowTimeProfile("lbl,2,4,../../path.csv,hplus,scoobydoo,where-are-you")]
    output = ief._write()
    assert prev_output in output
    assert ief.noofflowtimeprofiles == 1
    assert ief.noofflowtimeseries == 1
    assert "[Flow Time Profiles]" in output
    assert "FlowTimeProfile0=lbl,2,4,../../path.csv,hplus,scoobydoo,where-are-you" in output


def test_delete_all_flowtimeprofiles(test_workspace):
    ief = IEF(test_workspace / "7082.ief")
    ief.flowtimeprofiles = []
    output = ief._write()
    assert "[Flow Time Profiles]" not in output
    assert not hasattr(ief, "noofflowtimeprofiles")
    assert not hasattr(ief, "noofflowtimeseries")


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

    p_open.assert_called_once_with(f'"{exe_path}" -sd "{ief_fp}"', cwd=ief_fp.parent)

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
    ief.filepath = None
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


def test_datafile_path(test_workspace: Path):
    """Tests that `Datafile` can be converted to `Path` even if it contains backslashes in Linux."""
    ief = IEF(test_workspace / "P3Panels_UNsteady.ief")
    path = Path(ief.Datafile)
    assert path.stem == "UptonP8_Panels"
    assert path.parent == Path("../../networks")


def test_unique_events_retained(multievent_ief: IEF):
    """Tests that the .eventdata attribute retains the same number of items as the original ief"""
    event_dict = multievent_ief.eventdata
    assert len(event_dict) == 7


@pytest.mark.parametrize(
    ("sample_eventdata"),
    [
        ({}),
        ({"Fluvial Inflow": "..\\network.ied", "Event Override": "..\\event_override.ied"}),
        (
            {
                "Fluvial Inflow": "..\\network.ied",
                "Event Override": "..\\event_override.ied",
                "Spill Data": "..\\spill1.ied",
                "Spill Data<0>": "..\\spill2.ied",
                "<0>": "..\\ied_01.IED",
                "<1>": "..\\ied_02.IED",
                "<2>": "..\\ied_03.IED",
                "Added Event": "../added.ied",
            }
        ),
    ],
)
def test_adding_eventdata(multievent_ief, sample_eventdata, tmpdir):
    """Tests modifying, saving and reading eventdata dictionary.

    Compares that the input is equal to the output."""
    multievent_ief.eventdata = sample_eventdata
    new_path = Path(tmpdir) / "tmp.ief"
    multievent_ief.save(new_path)

    new_ief = IEF(new_path)
    assert new_ief.eventdata == sample_eventdata


def test_renaming_eventdata(multievent_ief, tmpdir):
    """Tests renaming an event, after it has been substituted for a temporary one."""

    mapping = {"<1>": "New Title"}

    multievent_ief.eventdata = {
        mapping.get(key, key): value for key, value in multievent_ief.eventdata.items()
    }
    new_path = Path(tmpdir) / "tmp.ief"
    multievent_ief.save(new_path)

    new_ief = IEF(new_path)

    assert new_ief.eventdata == {
        "Fluvial Inflow": "..\\network.ied",
        "Event Override": "..\\event_override.ied",
        "Spill Data": "..\\spill1.ied",
        "Spill Data<0>": "..\\spill2.ied",
        "<0>": "..\\ied_01.IED",
        "New Title": "..\\ied_02.IED",
        "<1>": "..\\ied_03.IED",
    }
