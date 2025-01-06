from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from floodmodeller_api import DAT, IED, IEF, INP, XML2D
from floodmodeller_api.to_from_json import is_jsonable
from floodmodeller_api.util import read_file

if TYPE_CHECKING:
    from floodmodeller_api._base import FMFile


def create_expected_json_files():
    """Helper function to recreate all the expected JSON files if needed at any point due to updates
    to the to_json code"""

    test_workspace = Path(__file__).parent / "test_data"
    for file in [
        "network.dat",
        "network.ied",
        "EX3.DAT",
        "EX6.DAT",
        "EX18.DAT",
        "EX3.IEF",
        "Domain1_Q.xml",
        "Linked1D2D.xml",
    ]:
        file = Path(test_workspace, file)
        obj = read_file(file)
        new_file = file.with_name(f"{file.name.replace('.', '_')}_expected").with_suffix(".json")
        with open(new_file, "w") as json_file:
            json_file.write(obj.to_json())


@pytest.fixture()
def dat_obj(test_workspace):
    """JSON:  To create the dat object for the tests"""
    return DAT(Path(test_workspace, "EX18.DAT"))


@pytest.fixture()
def json_expected(test_workspace):
    """JSON:  expected after passing to_json method"""
    return Path(test_workspace, "EX18_DAT_expected.json")


def test_dat_json(dat_obj):
    """JSON:  To test if to_json runs without failing"""
    assert dat_obj.to_json()


@pytest.fixture()
def parameterised_objs_and_expected(test_workspace) -> list[tuple[FMFile, Path]]:
    """JSON:  expected after passing to_json method"""
    return [
        (DAT(test_workspace / "EX18.DAT"), test_workspace / "EX18_DAT_expected.json"),
        (DAT(test_workspace / "network.dat"), test_workspace / "network_dat_expected.json"),
        (IED(test_workspace / "network.ied"), test_workspace / "network_ied_expected.json"),
        (DAT(test_workspace / "EX3.DAT"), test_workspace / "EX3_DAT_expected.json"),
        (DAT(test_workspace / "EX6.DAT"), test_workspace / "EX6_DAT_expected.json"),
        (IEF(test_workspace / "ex3.ief"), test_workspace / "EX3_IEF_expected.json"),
        (XML2D(test_workspace / "Domain1_Q.xml"), test_workspace / "Domain1_Q_xml_expected.json"),
        (XML2D(test_workspace / "Linked1D2D.xml"), test_workspace / "Linked1D2D_xml_expected.json"),
    ]


def test_to_json_matches_expected(parameterised_objs_and_expected: list[tuple[FMFile, Path]]):
    """JSON:  To test if the json object produced in to_json is identical to the expected json file"""
    for obj, json_expected in parameterised_objs_and_expected:
        # First, to create and handle the json (str) object
        # Fetch "Object Attributes" key only as we don't need to compare API versions
        json_dict_from_obj = json.loads(obj.to_json())["Object Attributes"]

        # Second, to handle the json file ..._expected.json which must be the same as the object created above.
        with open(json_expected) as file:
            json_dict_from_file = json.load(file)["Object Attributes"]

        # keys to ignore when testing for equivalence
        keys_to_remove = ["_filepath", "file", "_log_path"]
        for key in keys_to_remove:
            json_dict_from_obj.pop(key, None)
            json_dict_from_file.pop(key, None)

        assert json_dict_from_obj == json_dict_from_file, f"object not equal for {obj.filepath!s}"


@pytest.mark.parametrize(
    ("api_class", "file_extension_glob"),
    [
        (DAT, "*.dat"),
        (IED, "*.ied"),
        (XML2D, "*.xml"),
        (IEF, "*.ief"),
        (INP, "*.inp"),
    ],
)
def test_obj_reproduces_from_json_for_all_test_api_files(
    test_workspace,
    api_class,
    file_extension_glob,
):
    """JSON:  To test the from_json function,  It should produce the same dat file from a json file"""
    for file in Path(test_workspace).glob(file_extension_glob):
        assert api_class(file) == api_class.from_json(api_class(file).to_json())


def test_is_jsonable_with_jsonable_object():
    assert is_jsonable({"a": 1, "b": 2})


def test_is_jsonable_with_non_jsonable_object():
    class NonJsonable:
        def __init__(self):
            pass

    assert not is_jsonable(NonJsonable())
