import json
import os
from pathlib import Path
from typing import Any

import pandas as pd

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


def recursive_to_json(obj: Any, is_top_level: bool = True) -> Any:  # noqa: C901, PLR0911
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
        items = []
        for item in obj:
            items.append(recursive_to_json(item, is_top_level=False))

        return items

    # Dictionary to the all the serializable objects
    return_dict = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            return_dict[key] = recursive_to_json(value, is_top_level=False)

        return return_dict

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):  # noqa: RET503
        # Information from the flood modeller object will be included in the JSON file
        obj_class = obj.__class__
        # slicing undertaken to remove quotation marks
        return_dict["API Class"] = str(obj_class)[8:-2]
        if is_top_level:
            return_dict["API Version"] = __version__

        obj_dic = {}
        for key, value in obj.__dict__.items():
            obj_dic[key] = recursive_to_json(value, is_top_level=False)

        return_dict["Object Attributes"] = obj_dic

        return return_dict


# def from_json(cls, json: Any) -> str:
#     pass


def from_json(obj: str) -> Any:
    """
    Function to convert a JSON string back into Python objects

    Args:
        json_str (str): A JSON string

    Returns:
        A FMP object
    """
    obj = json.loads(obj)
    API_class = obj["API Class"]    # probably to identify the type of class to use it when creating the class
    obj = obj["Object Attributes"]
    return recursive_from_json(obj)


def recursive_from_json(obj: Any) -> Any:
    """
    Function to undertake a recursion through the different elements of the JSON object

    Args:
        obj (dict):  A JSON dict.  IT was converted from str to dict in from_json

    Returns:
        A FMP object
    """
    # from ._base import FMFile  # noqa: I001
    # from .units._base import Unit
    # from .units import IIC
    # from .backup import File

    for key, value in obj.items():
        if isinstance(value, dict):
            obj[key] = recursive_from_json(value)
        elif key == "class" and value == "pandas.DataFrame":
            df = pd.DataFrame.from_dict(obj["object"])
            obj["object"] = df
        elif key == "class" and value == "pandas.Series":
            sr = pd.Series(obj["object"])
            obj["object"] = sr
        elif isinstance(value, list):
            for item in value:
                if not isinstance(item, dict):
                    continue
                elif isinstance(item, dict):
                    recursive_from_json(item)
        # elif not value:
        #     pass
        # elif isinstance(value, int):
        #     pass
        # elif isinstance(value, float):
        #     pass
        # elif isinstance(value, str):
        #     pass
        # elif os.path.isfile(value):
        #     obj[key] = Path(value)
        # elif os.path.isdir(value):
        #     obj[key] = Path(value)
        elif "API Class" in obj:
            pass
    return obj


#######
# 1. Is what has been done so far correct?
# 2. To handle windowsPath
# 3. To handle API class
# 4. To create the proper FMP object
#