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
    _unit = "UNSUPPORTED"
    
    def _read(self, block): 
        
         #recognise type, pass all text 
         if self._subtype is False:     #IF THERE'S NO SUBTYPE READ THIS WAY
            self.name = block[1][: self._label_len].strip() #option 1
            
            labels = split_n_char(f"{block[1]:<{7*self._label_len}}", self._label_len)  #option 2
            self.name = labels[0]

            
         else:                          #for units which have subtype 
            self._subtype = block[1].split(" ")[0].strip()
            
            labels = split_n_char(f"{block[2]:<{4*self._label_len}}", self._label_len)  
            self.name = labels[0]
            self.ds_label = labels[1]
            self.us_remote_label = labels[2]
            self.ds_remote_label = labels[3]
            self.comment =                
        
