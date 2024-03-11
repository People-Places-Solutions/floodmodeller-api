import json
from pathlib import Path
from typing import Any

import pandas as pd

from .version import __version__


def to_json(obj: Any) -> str:
    """
    Function to convert any flood modeller object into a JSON file

    Args:
        obj (object):  Any flood modeller object (dat, ied, ief, cross sections...)

    Returns:
        A JSON file.
    """
    return json.dumps(recursive_to_json(obj), indent=4)


def is_jsonable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except Exception:
        return False


def recursive_to_json(obj: Any) -> Any:  # noqa: C901, PLR0911
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
    elif isinstance(obj, pd.Series):
        return {"class": "pandas.Series", "object": obj.to_dict()}

    # To convert WindowsPath, no serializable, objects to string, serializable.
    if isinstance(obj, Path):
        return str(obj)

    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        items = []
        for item in obj:
            items.append(recursive_to_json(item))

        return items

    # Dictionary to the all the serializable objects
    return_dict = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            return_dict[key] = recursive_to_json(value)

        return return_dict

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):  # noqa: RET503
        # Information from the flood modeller object will be included in the JSON file
        obj_class = obj.__class__
        # slicing undertaken to remove quotation marks
        return_dict["API Class"] = str(obj_class)[8:-2]
        return_dict["API Version"] = __version__

        obj_dic = {}
        for key, value in obj.__dict__.items():
            obj_dic[key] = recursive_to_json(value)

        return_dict["Object Attributes"] = obj_dic

        return return_dict


def from_json(cls, json: Any) -> str:
    pass
