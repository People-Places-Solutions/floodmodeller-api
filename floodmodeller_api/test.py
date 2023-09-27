from floodmodeller_api import IEF, DAT
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller_definition import TuflowToFloodModeller as T2FM
from pathlib import Path
import sys
import io

old_stdout = sys.stdout # Memorize the default stdout stream
sys.stdout = buffer = io.StringIO()

print('123')
print("testing")
a = 'HeLLo WorLd!'
print(a)
# Call your algorithm function.
# etc...

sys.stdout = old_stdout # Put the old stream back in place

whatWasPrinted = buffer.getvalue() # Return a str containing the entire contents of the buffer.
print(whatWasPrinted) # Why not to print it?
print("testing")
print(123)



#t2fm = T2FM()
#t2fm.run_gui()
#
#print("")