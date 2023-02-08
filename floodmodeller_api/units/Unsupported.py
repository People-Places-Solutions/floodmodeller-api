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


class Unsupported(Unit):
#class for all unsupported types, ignore/dont pass the arguments
    #_unit = "UNSUPPORTED"
    
    def _read(self, block):

        
    #recognise type, pass all text
        if self._subtype is False:     #IF THERE'S NO SUBTYPE READ THIS WAY
             
             
        ## option 1, find name the way boundary units find them - This would pass the entire 2nd line as the name....
            self.name = block[1][: self._label_len].strip()


        ## option 2, find name the way other units find them - issue is wwe don't know how many labels each of these would have
            labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
            self.name = labels[0]
            self.label = labels[1]  #all other labels on one line
            
            self._unit = block[0].split(" ", 1)            #this should be self._unit? or do we have a _type? This would recognise the first chunck of first line
            self.comment = block[0].replace(self._unit, "").strip()  #_unit? or type of somesort
            
            
         else:                          #FOR UNITS WITH SUBTYPE
            self._subtype = block[1].split(" ")[0].strip()     #FIGURE OUT DIFFERENCE BETWEEN SELF.SUBTYPE AND SELF._SUBTYPE
            
            labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
            self.name = labels[0]
            self.label = labels[1] #all other labels on one line
            
            self._unit = block[0].split(" ", 1)
            self.comment = block[0].replace(self._unit, "").strip()
        
