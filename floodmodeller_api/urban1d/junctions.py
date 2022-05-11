from ._base import UrbanSubsection, UrbanUnit
from floodmodeller_api.units.helpers import split_n_char, _to_float, _to_str, join_n_char_ljust



class JUNCTION(UrbanUnit): #TODO: need to update to be 'JUNCTION' with no S
 #   """ TO BE COMPLETED
#    """
    _unit = 'JUNCTION' # NOTE: this is used to assigned class name via setter
    
    def _read(self, line):
        
        unit_data = line.split() 
            
        while len(unit_data)<6:
            unit_data.append('')

        self.name = str(unit_data[0]) #TODO: update once Class inheritance sorted. 
        #TODO: need to catch instence when optional parameters are not provided
        self.elevation = _to_float(unit_data[1], 0.0) # Elevation of junction invert (ft or m). (required)
        self.max_depth = _to_float(unit_data[2], 0.0) # Depth from ground to invert elevation (ft or m) (default is 0). (optional)
        self.initial_depth = _to_float(unit_data[3], 0.0) # Water depth at start of simulation (ft or m) (default is 0). (optional)
        self.surface_depth = _to_float(unit_data[4], 0.0) # Maximum additional head above ground elevation that manhole junction can sustain under surcharge conditions (ft or m) (default is 0). (optional)
        self.area_ponded = _to_float(unit_data[5], 0.0) # Area subjected to surface ponding once water depth exceeds Ymax (ft2 or m2) (default is 0) (optional).
         
    def _write(self):

        #TODO:Improve indentation
        return join_n_char_ljust(15, self.name, self.elevation, self.max_depth, self.initial_depth, self.surface_depth, self.area_ponded)

class JUNCTIONS(UrbanSubsection):
    ''' Class to read the table of junctions'''
    _urban_unit_class = JUNCTION
    _attribute = 'junctions'
    

            
