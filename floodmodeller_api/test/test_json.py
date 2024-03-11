# from typing import Any
import json
import os

import pytest

from floodmodeller_api.to_from_json import to_json


@pytest.fixture
def dat_test(test_workspace):
    """To load an example of dat file"""
    return os.path.join(test_workspace, "EX18.DAT")


# @pytest.fixture
# def json_expected(test_workspace):
#     """JSON expected after passing to_json method"""
#     return os.path.join(test_workspace, "EX18_expected.json")


def test_dat_json(dat_test):
    """JSON: To test if to_json produces the json file"""
    assert to_json(dat_test)


def test_json_file_produced(dat_test, test_workspace):
    """JSON: To test if the json object produced in to_json is identical to the expected json file"""
    obj_json = to_json(dat_test)
    dat_json = json.loads(obj_json)
    with open(os.path.join(test_workspace, "EX18_.json"), "w") as json_file:
        json_file.write(obj_json)
    json_dict = json.load(open(os.path.join(test_workspace, "EX18_.json")))
    assert dat_json == json_dict


def test_is_jsonable(dat_test):  # I have doubts that it is making the job
    """JSON: To test that all the elements of the json are indeed serializable"""
    dat_json = to_json(dat_test)
    assert json.dumps(dat_json)
