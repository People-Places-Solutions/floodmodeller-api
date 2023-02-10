import pandas as pd

from ._base import Unit
from .helpers import (
    join_10_char,
    join_12_char_ljust,
    join_n_char_ljust,
    split_10_char,
    split_12_char,
    split_n_char,
    _to_float,
    _to_str,
    _to_int,
    _to_data_list,
)
from floodmodeller_api.validation import _validate_unit


class UNSUPPORTED(Unit):
#class for all unsupported types, ignore/dont pass the arguments
    #_unit = "UNSUPPORTED"
    
    def _read(self, block, unit_name, unit_type, subtype):
        self.name = unit_name
        self._unit = unit_type
        self._subtype = subtype
        
    #recognise type, pass all text
        if self._subtype is False:     #IF THERE'S NO SUBTYPE READ THIS WAY

        ## option 2, find name the way other units find them - issue is wwe don't know how many labels each of these would have
            self.labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
            #self.name = labels[0]
                        
            #self._unit = block[0].split(" ", 1)            #this should be self._unit? or do we have a _type? This would recognise the first chunck of first line
            self.comment = block[0].replace(self._unit, "").strip()  #_unit? or type of somesort
            labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
            self.name = labels[0]
            self.label = labels[1]  #all other labels on one line
            
            self._unit = block[0].split(" ", 1)            #this should be self._unit? or do we have a _type? This would recognise the first chunck of first line
            self.comment = block[0].replace(str(self._unit), "").strip()  #_unit? or type of somesort
            
            
        else:                          #FOR UNITS WITH SUBTYPE
            self._subtype = block[1].split(" ")[0].strip()     #FIGURE OUT DIFFERENCE BETWEEN SELF.SUBTYPE AND SELF._SUBTYPE
            
            self.labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
            #self.name = labels[0]
            #self.labels = labels[1] #all other labels on one line
            labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
            self.name = labels[0]
            self.label = labels[1] #all other labels on one line
            
            self._unit = block[0].split(" ", 1)
            self.comment = block[0].replace(str(self._unit), "").strip()
 
