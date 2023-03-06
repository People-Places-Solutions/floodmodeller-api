import sys
import os
from glob import glob
from pathlib import Path

try:
    from floodmodeller_api import DAT
except ImportError:
    print('Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment')
    sys.exit()
from floodmodeller_api.validation.validation import _validate_unit    
dat2 = DAT(r'C:\Users\LAMBERD3\Documents\Python\Flood_modeller_git\floodmodeller-api\sample_scripts\sample_data\river_only.dat')
dat = DAT(r'C:\Users\LAMBERD3\Documents\Python\Flood_modeller_git\floodmodeller-api\sample_scripts\sample_data\EX3.dat')

pass
unit_0 = dat.boundaries['m60']
unit_1 = dat.sections['m60']
unit_10 = dat.sections['BRIDU']
unit_11 = dat.structures['BRIDU']
unit_12 = dat.sections['BRIDD']
unit_42 = dat.sections['700']
unit_43 = dat.boundaries['700']



pass
#dat.insert_unit()
dat.insert_unit(unit_0, add_before=unit_10)
dat.insert_unit(unit_1)
dat.insert_unit(unit_10)
dat.insert_unit(unit_11)
dat.insert_unit(unit_12)
dat.insert_unit(unit_42)
dat.insert_unit(unit_43)


#dat.remove_unit()


pass
#structure = dat._dat_struct

#unit_240 
    



#dat.remove_unit(dat.sections['RIV02'])
#dat.remove_unit(unit_3)

#dat.insert_unit(dat.type['subtype','name', 'prev_unit', 'next_unit'])

#dat.insert_unit(dat.sections[RIVER, 'RIV02', unit_2])
#dat.insert_unit(unit_3)
#dat.insert_unit(dat.boundaries[QTBDY, 'inflow', None, unit_0 ])

#qtbdy = QTBDY(name=..., data=...)

#dat.insert_unit(unit=qtbdy, add_before=..., add_after=..., add_at=...)

#def insert_unit(
#    unit, 
#    add_before = None, # Adding before the given unit
#    add_after = None, # Adding after the given unit
#    add_at = None, # Adding at position n in the DAT
#):
    # Check if the unit is valid (_validate_unit function from validate)
    
    # Add into the _dat_struct and into _all_units add into group (sections/boundaries...)
    
    # update the gxy and GIS info and iic's tables (lower priority)
    
    # _update_raw_data 
    
    # update gen parameter node count
    
    # Add into
    
    
    
    
    
#    if add_before:
        # do the method to add before
#    elif



#print('prev units')
#dat.prev(section_1)
#dat.prev(section_2)
#dat.prev(section_3)
#dat.prev(section_4)


pass