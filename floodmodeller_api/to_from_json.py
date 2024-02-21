from typing import Any
import json
import pandas as pd
from pathlib import Path
from .version import __version__

"""
TODO:
- Update variable names to be more clear 
- pandas dataframe and series, include class type
- general tidy up 
- Better handle type imports so not circular

"""

def is_jsonable(obj: Any) -> bool:
    try:
        json.dumps(obj)
        return True
    except:
        return False

def to_json(obj: Any) -> str:
    return json.dumps(recursive_to_json(obj), indent=4)
    
def recursive_to_json(obj: Any) -> Any:
    from ._base import FMFile
    from .units._base import Unit
    from .units import IIC
    from .backup import File
    # creating the dictionary
    dictObj = {}
    
    if is_jsonable(obj):
        return obj
    
    if isinstance(obj, (pd.DataFrame, pd.Series)):
        #TODO: handle this case 
        # Do they need a class type?? Probably
        # dictObj["Class"] = str(cla)[8:-2]
        return "pandas object" # DataFrame.to_json()
    
    if isinstance(obj, Path):
        return str(obj) # DataFrame.to_json()
    
    # Case list or dict of non-jsonable stuff
    if isinstance(obj, list):
        # create list and append
        items = []
        for item in obj:
            items.append(recursive_to_json(item))
        
        return items

    if isinstance(obj, dict):
        # create list and append
        for key, value in obj.items():
            dictObj[key] = recursive_to_json(value)
        
        return dictObj

    # Either a type of FM API Class
    if isinstance(obj, (FMFile, Unit, IIC, File)):
        cla = obj.__class__

        dictObj["API Class"] = str(cla)[8:-2]
        dictObj["API Version"] = __version__

        objDic = {}
        for key, value in obj.__dict__.items():
            objDic[key] = recursive_to_json(value)
        
        dictObj["Object Attributes"] = objDic
        return dictObj

# def from_json():
#     pass


