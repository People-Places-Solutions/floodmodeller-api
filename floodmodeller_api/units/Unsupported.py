from ._base import Unit
from .helpers import split_n_char

class UNSUPPORTED(Unit):
    """Used to read in all unsupported unit types, simply returning the raw data on write"""
    
    def _read(self, block, unit_name, unit_type, subtype):
        self.name = unit_name
        self._unit = unit_type
        self._subtype = subtype
        self._raw_block = block
        self.comment = block[0].replace(self._unit, "").strip()
        
        if self._subtype is False:
            self.labels = split_n_char(f"{block[1]:<{2*self._label_len}}", self._label_len)
            
        else:
            self._subtype = block[1].split(" ")[0].strip()
            if self._unit == "JUNCTION":
                self.labels = split_n_char(block[2], self._label_len)
            self.labels = split_n_char(f"{block[2]:<{2*self._label_len}}", self._label_len)
        
        if self.labels[1] != "":
            self.ds_label = self.labels[1]
            
    def _write(self):
        return self._raw_block
 
