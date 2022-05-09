from ._base import Urban1D
#from .helpers import (join_10_char, join_12_char_ljust, join_n_char_ljust,
#                      split_10_char, split_12_char, split_n_char, _to_float, _to_str, _to_int, _to_data_list)
#from .validation import _validate_unit, parameter_options

class JUNCTIONS(Urban1D): #TODO: need to update to be 'JUNCTION' with no S
 #   """ TO BE COMPLETED
#    """
    _unit = 'JUNCTIONS' # NOTE: this is used to assigned class name via setter
    
    def _read(self, block): #REVIEW: has more arguments that parent class method

      print('class activated')
      self.name = 'Assigned Name'

      self.param = block[0] 
      self.param1 = block[1]
      self.param2 = block[2]
      self.param3 = block[3]
      self.param4 = block[4]

      ### Need to consider additional parameters - extend earlier. 
       
    
class OUTFALLS(Urban1D): #TODO: need to update to be 'OUTFALLS' with no S
#   """ TO BE COMPLETED
#    """
   _unit = 'OUTFALLS' # NOTE: this is used to assigned class name via setter

   def _read(self, block): #REVIEW: has more arguments that parent class method

      print('class activated')
      self.name = 'Assigned Name'

      self.param = block[0] 
      self.param1 = block[1]
      self.param2 = block[2]
      self.param3 = block[3]
      self.param4 = block[4]

   ### Need to consider additional parameters - extend earlier. 
      
