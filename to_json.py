"""
Function to convert the different objects of Flood Modeller API top json format
"""
import os
from floodmodeller_api import IEF
from floodmodeller_api import IED
from floodmodeller_api import DAT
import mpu.io

VERSION_API = "0.4.2.post1"

def fileA(text):
    string = fileD["file"]
    listStr = string.split("\n")
    del fileD["file"]
    fileD["file"] = listStr[0]
    fileD["Path"] = listStr[1][6:]
    fileD["ID"] = listStr[2][4:]
    return fileD["file"], fileD["Path"], fileD["ID"]


def dictionary():
    fileDD = {}
    fileDD["API Class"] = "IEF"
    fileDD["API Version"] = VERSION_API
    fileDD["Object Attributes"] = fileD
    return fileDD

def to_json(file):
    # to identify type of file
    filename, extension = os.path.splitext(file)
    # as there could be a risk of having capital letters, we create a variable with lower case in all the cases
    extension = extension.str.lower()
    # match/case with the different type of files
    match extension:
        case ".ief":
            ief2 = IEF(file)
            fileD = ief2.__dict__
            fileD["_filepath"] = fileD["_filepath"].__str__()
            fileD["file"] = str(fileD["file"])
            fileA(fileD["file"])
            dictionary()
            mpu.io.write('IEF.json', fileDD)
        case ".ied":
            ief2 = IED(file)
            fileD = ief2.__dict__
            fileD["_filepath"] = fileD["_filepath"].__str__()
            fileD["file"] = str(fileD["file"])
            fileA(fileD["file"])

            try:
                iedD["_unsupported"] = str(iedD["_unsupported"])
            except TypeError:
                iedD["_unsupported"] = "{}"

            try:
                iedD["boundaries"] = str(iedD["boundaries"])
            except TypeError:
                iedD["boundaries"] = "{}"

            try:
                iedD["_all_units"] = str(iedD["_all_units"])
            except TypeError:
                iedD["_all_units"] = "{}"

            try:
                iedD["sections"] = str(iedD["sections"])
            except TypeError:
                iedD["sections"] = "{}"

            try:
                ied["structures"] = str(iedD["structures"])
            except TypeError:
                iedD["structures"] = "{}"

            try:
                ied["conduits"] = str(iedD["conduits"])
            except TypeError:
                iedD["structures"] = "{}"

            try:
                ied["losses"] = str(iedD["losses"])
            except TypeError:
                iedD["losses"] = "{}"

            dictionary()
            mpu.io.write('IEF.json', fileDD)
        case ".dat":
            ief2 = DAT(file)
            fileD = ief2.__dict__
            fileD["_filepath"] = fileD["_filepath"].__str__()
            fileD["file"] = str(fileD["file"])
            fileA(fileD["file"])

            try:
                datD["sections"] = str(datD["sections"])
            except TypeError:
                datD["sections"] = "{}"

            try:
                datD["_unsupported"] = str(datD["_unsupported"])
            except TypeError:
                datD["_unsupported"] = "{}"

            try:
                datD["conduits"] = str(datD["conduits"])
            except TypeError:
                datD["conduits"] = "{}"

            try:
                datD["losses"] = str(datD["losses"])
            except TypeError:
                datD["losses"] = "{}"

            try:
                datD["structures"] = str(datD["structures"])
            except TypeError:
                datD["structures"] = "{}"

            try:
                datD["boundaries"] = str(datD["boundaries"])
            except TypeError:
                datD["boundaries"] = "{}"

            try:
                datD["_all_units"] = str(datD["_all_units"])
            except TypeError:
                datD["_all_units"] = "{}"

            try:
                datD["initial_conditions"] = str(datD["initial_conditions"])
            except TypeError:
                datD["initial_conditions"] = "{}"

            dictionary()
            mpu.io.write('IEF.json', fileDD)





