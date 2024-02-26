from typing import Any
import json
import pandas as pd
from pathlib import Path
from version import __version__

"""
TODO:
- Update variable names to be more clear            ## DONE
- pandas dataframe and series, include class type   ## DONE
- general tidy up                                   ##
- Better handle type imports so not circular        ## 

"""

def to_json(obj: Any) -> str:
    return json.dumps(recursive_to_json(obj), indent=4)


def is_jsonable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except:
        return False


def new_dictionary(obj: Any) -> dict:
    obj_class = obj.__class__
    # creating the dictionary
    obj_dic_result = {}

    obj_dic_result["API Class"] = str(obj_class)[8:-2]
    obj_dic_result["API Version"] = __version__

    return obj_dic_result


def recursive_to_json(obj: Any) -> Any:
    global pd_json
    from _base import FMFile
    from units._base import Unit
    from units import IIC
    from backup import File

    obj_dic_result = new_dictionary(obj)


    if is_jsonable(obj):
        return obj

    if isinstance(obj, (pd.DataFrame, pd.Series)):
        return obj.to_json()

    if isinstance(obj, Path):
        return str(obj)

    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        items = []
        for item in obj:
            items.append(recursive_to_json(item))

        return items

    if isinstance(obj, dict):
        for key, value in obj.items():
            obj_dic_result[key] = recursive_to_json(value)

        return obj_dic_result

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):


        obj_dic = {}
        for key, value in obj.__dict__.items():
            obj_dic[key] = recursive_to_json(value)

        obj_dic_result["Object Attributes"] = obj_dic
        return obj_dic_result


def from_json():
    pass


if __name__ == '__main__':
    ief = "C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\ex3.ief"
    to_json(ief)



