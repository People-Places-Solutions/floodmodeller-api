from ._base import UrbanSubsection, UrbanUnit
#from floodmodeller_api.units.helpers import split_n_char, _to_float, _to_str


class OUTFALLS(UrbanSubsection): #TODO: need to update to be 'OUTFALLS' with no S
    
   def _read(self, block):
      pass
   
   def _write(self):
      pass

class OUTFALL(UrbanUnit): #TODO: need to update to be 'OUTFALLS' with no S
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