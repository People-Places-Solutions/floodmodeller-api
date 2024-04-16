import json
from pathlib import Path
from typing import Any, Union

import pandas as pd

import floodmodeller_api  # noqa: F401.  Needed to execute eval() at line 115 in from_json

from .version import __version__


def to_json(obj: Any) -> str:
    """
    Function to convert any flood modeller object into a JSON object

    Args:
        obj (object):  Any flood modeller object (dat, ied, ief, cross sections...)

    Returns:
        A JSON formatted string.
    """
    return json.dumps(recursive_to_json(obj), indent=2)


def is_jsonable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except Exception:
        return False


def recursive_to_json(obj: Any, is_top_level: bool = True) -> Any:  # noqa: PLR0911
    """
    Function to undertake a recursion through the different elements of the python object

    Args:
        Obj (object):  Any flood modeller object (dat, ied, ief, cross sections...)

    Returns:
        if the object is serializable, it creates the object to go to the function to_json and to create the JSON file,
        otherwise, it will move back through this function recursively until the object is finally serializable.
    """
    from ._base import FMFile  # noqa: I001
    from .units._base import Unit
    from .units import IIC
    from .backup import File

    if is_jsonable(obj):
        return obj

    if isinstance(obj, pd.DataFrame):
        return {"class": "pandas.DataFrame", "object": obj.to_dict()}
    if isinstance(obj, pd.Series):
        return {"class": "pandas.Series", "object": obj.to_dict()}

    # To convert WindowsPath, no serializable, objects to string, serializable.
    if isinstance(obj, Path):
        return str(obj)

    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        return [recursive_to_json(item, is_top_level=False) for item in obj]

    # Dictionary to the all the serializable objects
    if isinstance(obj, dict):
        return {key: recursive_to_json(value, is_top_level=False) for key, value in obj.items()}

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):  # noqa: RET503
        # Information from the flood modeller object will be included in the JSON output
        # slicing undertaken to remove quotation marks
        return_dict: dict[str, Any] = {"API Class": str(obj.__class__)[8:-2]}
        if is_top_level:
            return_dict["API Version"] = __version__

        return_dict["Object Attributes"] = {
            key: recursive_to_json(value, is_top_level=False) for key, value in obj.__dict__.items()
        }

        return return_dict


def from_json(obj: Union[str, dict]) -> dict:
    """
    Function to convert a JSON string back into Python objects

    Args:
        json_str (str): A JSON string

    Returns:
        A FMP object
    """
    # To convert a JSON string into a python dictionary
    if isinstance(obj, str):
        obj_dict = json.loads(obj)["Object Attributes"]
    else:
        obj_dict = obj["Object Attributes"]

    return recursive_from_json(obj_dict)


def recursive_from_json(obj: Union[dict, Any]) -> Any:
    """
    Function to undertake a recursion through the different elements of the JSON object

    Args:
        obj (dict):  A JSON dict.  IT was converted from str to dict in from_json

    Returns:
        A FMP object
    """

    if "API Class" in obj:
        class_type = obj["API Class"]
        return eval(f"{class_type}").from_json(obj)

    if "class" in obj and obj["class"] == "pandas.DataFrame":
        df = pd.DataFrame.from_dict(obj["object"])
        df.index = pd.RangeIndex(len(df))
        return df
    if "class" in obj and obj["class"] == "pandas.Series":
        sr = pd.Series(obj["object"])
        sr.index = sr.index.astype("float64")
        return sr

    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = recursive_from_json(value)
        elif isinstance(value, list):
            new_list = []
            for item in value:
                if isinstance(item, dict):
                    new_list.append(recursive_from_json(item))
                else:
                    new_list.append(item)

            obj[key] = new_list

    return obj
