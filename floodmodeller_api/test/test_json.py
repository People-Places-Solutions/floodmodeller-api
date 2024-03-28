import json
import os

import pytest

from floodmodeller_api import DAT
from floodmodeller_api.to_from_json import to_json


@pytest.fixture
def dat_test(test_workspace):
    """JSON:  To load an example of dat file"""
    return os.path.join(test_workspace, "EX18.DAT")


@pytest.fixture
def dat_obj(dat_test):
    """JSON:  To create the dat object for the tests"""
    dat = DAT(dat_test)

    return dat.to_json()


@pytest.fixture
def json_expected(test_workspace):
    """JSON:  expected after passing to_json method"""
    return os.path.join(test_workspace, "EX18_expected.json")


def test_dat_json(dat_obj):
    """JSON:  To test if to_json produces the json file"""
    assert to_json(dat_obj)


def test_json_file_produced(dat_obj, json_expected):
    """JSON:  To test if the json object produced in to_json is identical to the expected json file"""
    # First, to create and handle the json (str) object
    # loads is to convert a json string document into a python dictionary
    dat_json = json.loads(dat_obj)
    # to create a dict without the information added of class and version
    dict_dat_values = dat_json.get("Object Attributes")
    # keys with paths and timing that must be removed to avoid issues when testing.
    keys_removed = ["_filepath", "file"]
    # to remove the keys of keys_removed
    for key in keys_removed:
        del dict_dat_values[key]
    # Second, to handle the json file EX18_expected.json which must be the same as the object created above.
    # load is to read a json document
    json_dict = json.load(open(json_expected))  # noqa: SIM115
    dict_expected_values = json_dict.get("Object Attributes")
    for key in keys_removed:
        del dict_expected_values[key]

    assert dict_dat_values == dict_expected_values


def test_is_jsonable(dat_obj):  # I have doubts that it is making the job
    """JSON:  To test that all the elements of the json are indeed serializable"""
    assert json.dumps(dat_obj)


def test_dat_from_json(test_workspace):
    """JSON:  To test the from_json function,  It should produce the same dat file from a json file"""
    for datfile in Path(test_workspace).glob("*.dat"):
        assert DAT(datfile) == DAT.from_json(DAT(datfile).to_json())