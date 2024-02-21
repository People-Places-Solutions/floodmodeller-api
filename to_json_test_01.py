
import os
from floodmodeller_api import DAT
from floodmodeller_api import IEF
from floodmodeller_api import IED
import floodmodeller_api
import json
from pathlib import Path


os.chdir(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data")

os.listdir()
print("")
print("")

# open the ied
dat = DAT(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\EX3.DAT")
ief = IEF(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\ex3.ief")
ied = IED(r"C:\PROJECTS\FLOOD_MODELLER_API\JSON\floodmodeller-api\demo\data\network.ied")


# convert ied to dictionary
fmp_obj_dict = dat.__dict__                         ###  FILE FMP

# to identify
for k, v in fmp_obj_dict.items():
    print(k)

print("")
print("")
########################################
## to test not serializable keys
########################################
def is_jsonable(x):
    try:
        json.dumps(x)
        return True
    except:
        return False

## creating a list that has all the keys that the current dat file has no serizeable
keys_to_handle = []
for key,value in fmp_obj_dict.items():
    if not is_jsonable(value):
        keys_to_handle.append(key)

print(keys_to_handle)
print("")
print("")


## no serizeable keys in dat.  Note there are more, but the current dat file doesn't have those units, for instance, conduits.             ###  FILE FMP
print("BEFORE")
print("")
print("_filepath ", type(dat._filepath))
print("file ", type(dat.file))
print("sections ", type(dat.sections))
print("boundaries ", type(dat.boundaries))
print("structures ", type(dat.structures))
print("_all_units ", type(dat._all_units))
print("initial_conditions ", type(dat.initial_conditions))
print("")
print("")


## to add the new dictionaries to the current dictionary
dictionary_dict = {}
columns_dict = []
count_dict = 0
dictionary_list = {}
columns_list = []
count_list = 0

for k, v in fmp_obj_dict.items():
    if k in keys_to_handle and type(v) == dict:
        #print(k)
        columns_dict.append(key)
        new_dict = {}
        for k2 in v:
            #print(k2)
            new_dict[k2] = fmp_obj_dict[k][k2].__dict__
        dictionary_dict[columns_dict[count_dict]] = new_dict
        count_dict += 1
    elif key == k and type(v) == list:
        #print(k)
        columns_list.append(key)

    elif str(fmp_obj_dict[k].__class__)[8:25] == "floodmodeller_api":
        #print(k)
        fmp_obj_dict[k] = fmp_obj_dict[k].__dict__

    elif fmp_obj_dict["_filepath"]:
        fmp_obj_dict["_filepath"] = str(fmp_obj_dict["_filepath"])

for n in columns_dict:
    del fmp_obj_dict[n]
    fmp_obj_dict[n] = dictionary_dict[n]


final_obj_dict = {}
class_obj = dat.__class__                                              ###  FILE FMP
final_obj_dict["API Class"] = str(class_obj)[8:-2]
final_obj_dict["API Version"] = floodmodeller_api.__version__
assert isinstance(fmp_obj_dict, object)
final_obj_dict["Object Attributes"] = fmp_obj_dict


print("AFTER")                                                         ###  FILE FMP
print("")
print("_filepath ", type(dat._filepath))
print("file ", type(dat.file))
print("sections ", type(dat.sections))
print("boundaries ", type(dat.boundaries))
print("structures ", type(dat.structures))
print("_all_units ", type(dat._all_units))
print("initial_conditions ", type(dat.initial_conditions))
print("")
print("")