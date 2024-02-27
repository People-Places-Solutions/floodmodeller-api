
from typing import Any
import json
from pathlib import Path
import pandas as pd
from .version import __version__


"""
TODO:
- Update variable names to be more clear            ## DONE
- pandas dataframe and series, include class type   ## DONE
- general tidy up                                   ## DONE
- Better handle type imports so not circular        ## DONE

"""

def to_json(obj: Any) -> str:
    return json.dumps(recursive_to_json(obj), indent=4)


def is_jsonable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except:
        return False


def recursive_to_json(obj: Any) -> Any:
    from ._base import FMFile
    from .units._base import Unit
    from .units import IIC
    from .backup import File

    if is_jsonable(obj):
        return obj

    if isinstance(obj, (pd.DataFrame, pd.Series)):
        data_pd = {}
        if isinstance(obj, pd.DataFrame):
            return {"class": "pandas.DataFrame",
                                         "object": obj.to_dict()
                                         }
        elif isinstance(obj, pd.Series):
            return {"class": "pandas.Series",
                                         "object": obj.to_dict()
                                         }


    if isinstance(obj, Path):
        return str(obj)

    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        items = []
        for item in obj:
            items.append(recursive_to_json(item))

        return items

    return_dict = {}

    if isinstance(obj, dict):
        for key, value in obj.items():
            return_dict[key] = recursive_to_json(value)

        return return_dict

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):
        obj_class = obj.__class__

        return_dict["API Class"] = str(obj_class)[8:-2]
        return_dict["API Version"] = __version__

        obj_dic = {}
        for key, value in obj.__dict__.items():
            obj_dic[key] = recursive_to_json(value)

        return_dict["Object Attributes"] = obj_dic

        return return_dict


def from_json():
    pass


