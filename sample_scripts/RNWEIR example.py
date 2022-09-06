#Import modules
from floodmodeller_api import DAT

#Initialise DAT class
dat = DAT("C:/Users/CHRISTA4/OneDrive - Jacobs/Documents/FM API/floodmodeller-api/test/test_data/ex4.DAT")

#Iterate through all round nosed weir sections
for name, structure in dat.structures.items():
    if(structure._unit == "RNWEIR"):
        structure.upstream_crest_height += 0.3 #Increase upstream crest height by 0.3m

dat.save("C:/Users/CHRISTA4/OneDrive - Jacobs/Documents/FM API/floodmodeller-api/test/test_data/ex4_changed.DAT")