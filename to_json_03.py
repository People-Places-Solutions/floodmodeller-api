"""
Function to convert the different objects of Flood Modeller API top json format
"""
import os

from floodmodeller_api import DAT
import floodmodeller_api
import json


ief = IEF(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\ex3.ief")
dat = DAT(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\EX3.DAT")
ied = IED(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\network.ied")


def to_json(obj):
    # function to check if it is serializable or not.
    def is_jsonable(x):
        try:
            json.dumps(x)
            return True
        except:
            return False

    # converting FMP object to dictionary
    objDic = obj.__dict__

    # converting no serizeable pairs to string
    for key, value in objDic.items():
        if not is_jsonable(value):
            objDic[key] = str(objDic[key])

    # handling the key "file" which has three parts to split
    if "file" in objDic:
        string = objDic["file"]
        strSpl = string.split("\n")
        del objDic["file"]
        objDic["file"] = strSpl[0]
        objDic["Path"] = strSpl[1][6:]
        objDic["ID"] = strSpl[2][4:]

    # creating the final dictionary
    dictObj = {}
    cla = obj.__class__
    dictObj["API Class"] = str(cla)[8:-2]
    dictObj["API Version"] = floodmodeller_api.__version__
    assert isinstance(objDic, object)
    dictObj["Object Attributes"] = objDic

    # creating the final json object and file
    json_obj = json.dumps(dictObj, indent=4)
    with open(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\dat_05.json", "w") as json_file:
        json_file.write(json_obj)


to_json(dat)

