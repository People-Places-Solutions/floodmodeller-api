"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd
from pandas import Index

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


def pandas_to_json(obj: pd.DataFrame | pd.Series) -> dict:
    if isinstance(obj, pd.DataFrame):
        if isinstance(obj.columns, pd.MultiIndex):
            # Handle multi index columns (i.e. ZZN dataframe results)
            obj.columns = pd.Index(map(str, obj.columns.values))

        return {"class": "pandas.DataFrame", "object": obj.to_dict()}

    # otherwise returns as series
    return {
        "class": "pandas.Series",
        "variable_name": obj.name,
        "index_name": obj.index.name,
        "object": obj.to_dict(),
    }


def recursive_to_json(obj: Any, is_top_level: bool = True) -> Any:  # noqa: PLR0911
    """
    Function to undertake a recursion through the different elements of the python object

    Args:
        Obj (object):  Any flood modeller object (dat, ied, ief, cross sections...)

    Returns:
        if the object is serializable, it creates the object to go to the function to_json and to create the JSON file,
        otherwise, it will move back through this function recursively until the object is finally serializable.
    """
    from ._base import FMFile
    from .backup import File
    from .ief import FlowTimeProfile
    from .units import IIC
    from .units._base import Unit
    from .urban1d._base import UrbanSubsection, UrbanUnit

    if is_jsonable(obj):
        return obj

    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return pandas_to_json(obj)

    # To convert WindowsPath, no serializable, objects to string, serializable.
    if isinstance(obj, Path):
        return str(obj)

    if isinstance(obj, set):
        # create list and append
        return {"python_set": [recursive_to_json(item, is_top_level=False) for item in sorted(obj)]}

    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        return [recursive_to_json(item, is_top_level=False) for item in obj]

    # Dictionary to the all the serializable objects
    if isinstance(obj, dict):
        return {key: recursive_to_json(value, is_top_level=False) for key, value in obj.items()}

    # Either a type of FM API Class
    if isinstance(
        obj,
        (FMFile, Unit, IIC, File, UrbanSubsection, UrbanUnit, FlowTimeProfile),
    ):
        # Information from the flood modeller object will be included in the JSON output
        # slicing undertaken to remove quotation marks
        return_dict: dict[str, Any] = {"API Class": str(obj.__class__)[8:-2]}
        if is_top_level:
            return_dict["API Version"] = __version__

        return_dict["Object Attributes"] = {
            key: recursive_to_json(value, is_top_level=False) for key, value in obj.__dict__.items()
        }

        return return_dict

    return None


def from_json(obj: str | dict) -> dict:
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


def recursive_from_json(obj: dict | Any) -> Any:
    """
    Function to undertake a recursion through the different elements of the JSON object

    Args:
        obj (dict):  A JSON dict.  IT was converted from str to dict in from_json

    Returns:
        A FMP object
    """

    if "API Class" in obj:
        class_type = obj["API Class"]
        from .mapping import api_class_mapping

        return api_class_mapping[class_type].from_json(obj)

    if "class" in obj and obj["class"] == "pandas.DataFrame":
        reconstructed_df = pd.DataFrame.from_dict(obj["object"])
        reconstructed_df.index = convert_dataframe_index(reconstructed_df.index)
        return reconstructed_df
    if "class" in obj and obj["class"] == "pandas.Series":
        reconstructed_sr = pd.Series(obj["object"])
        reconstructed_sr.index = convert_dataframe_index(reconstructed_sr.index)
        reconstructed_sr.index.name = obj["index_name"]
        reconstructed_sr.name = obj["variable_name"]
        return reconstructed_sr

    if "python_set" in obj:
        return set(obj["python_set"])

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


def convert_dataframe_index(index: Index) -> Index:
    try:
        return index.astype("int")
    except ValueError:
        pass
    try:
        return index.astype("float")
    except ValueError:
        return index


class Jsonable:
    """Base class used to provide underlying to_json and from_json methods"""

    def __init__(self, **kwargs):
        pass

    def to_json(self) -> str:
        """Converts the object instance into a JSON string representation.

        Returns:
            str: A JSON string representing the object instance.
        """
        return to_json(self)

    @classmethod
    def from_json(cls, json_string: str):
        """Creates an object instance from a JSON string.

        Args:
            json_string (str): A JSON string representation of the object.

        Returns:
            An object instance of the class.
        """
        object_dict = from_json(json_string)
        api_object = cls(from_json=True)

        # Loop through the dictionary and update the object
        for key, value in object_dict.items():
            setattr(api_object, key, value)

        return api_object
