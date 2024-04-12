import json
from pathlib import Path
from typing import Any
#from ._base import FMFile
import pandas as pd

import floodmodeller_api
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


def from_json(obj: str) -> Any:
    """
    Function to convert a JSON string back into Python objects

    Args:
        json_str (str): A JSON string

    Returns:
        A FMP object
    """
    # To convert a JSON string into a python dictionary
    #obj = obj.replace("'", '"')
    obj = json.loads(obj)
    # probably to identify the type of class to use it when creating the class
    #if obj.get("API Class"):
    #API_class = obj["API Class"]
    obj = obj["Object Attributes"]
    return recursive_from_json(obj)

# function to define the FMP classes inside of the main FMP object.  For instance, a dat class can have many different other objects inside
# def _class_api(api: Any) -> Any:
#     class_sliced = api[18:].replace(".", " ").split()    # it creates a list
#     if len(class_sliced) == 2:    # if there are 2 items in the list, it is not a unit
#         pass
#     elif len(class_sliced) == 3:  # if there are 3 items in the list, it is a unit
#         pass


def recursive_from_json(obj: Any) -> Any:
    """
    Function to undertake a recursion through the different elements of the JSON object

    Args:
        obj (dict):  A JSON dict.  IT was converted from str to dict in from_json

    Returns:
        A FMP object
    """

    #import_list = []

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
        elif os.path.isfile(value):
            obj[key] = Path(value)
        elif os.path.isdir(value):
            obj[key] = Path(value)
        elif key == "API Class":
            #print(obj["Object Attributes"])
            #class_api = _class_api(obj["API Class"])
            #print(type(obj["Object Attributes"]))
            class_type = obj["API Class"]           # variable with the type of class
            if value.startswith("floodmodeller_api."):
                #api_dict = obj["Object Attributes"]    # dict with the instances of the FMP object
                #print(obj["API Class"])
                #head_flood_modeller_class = obj["API Class"][:17]   # to slice the api class to be able to solve issue with eval().  See comment by eval().
                #tail_flood_modeller_class = obj["API Class"][18:]
                ##################################################################################
                # import_list.append(head_flood_modeller_class)
                # if len(import_list) == 0:
                #     pass
                # if len(import_list) == 1:
                #     __import__(import_list[0])
                # elif len(import_list) > 1:
                #     for n, i in enumerate(import_list):
                #         if import_list[n] != import_list[n-1]:
                #             __import__(import_list[n])
                ####################################################################################
                #eval(f"__import__({head_flood_modeller_class}).{tail_flood_modeller_class}", {"floodmodeller_api": "floodmodeller_api"}).from_json(obj["Object Attributes"])    # error.  NameError: name 'floodmodeller_api' is not defined.  See bookmark.
                #eval(f"{class_type}.from_json({obj['Object Attributes']})")             # everything inside eval() as string
                #eval(f"{class_type}").from_json(json.dumps(obj["Object Attributes"]))   # instance as string
                eval(f"{class_type}").from_json(obj["Object Attributes"])                # instance as dictionary


    return obj

