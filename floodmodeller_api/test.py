from floodmodeller_api import IEF, DAT
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller_definition import TuflowToFloodModeller as T2FM
from pathlib import Path

t2fm = T2FM()
t2fm.run_gui()

print("")