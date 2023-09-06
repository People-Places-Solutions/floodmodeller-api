from floodmodeller_api import IEF, DAT
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller_definition import TuflowToFloodModeller as T2FM
from pathlib import Path

#t2fm = T2FM()
#t2fm.run_gui()

from floodmodeller_api.toolbox import StructureLog

StructureLog.run(
    input_path="C:\FloodModellerJacobs\Structure Log\DAT_for_API\Bourn_Rea_OBC_BLN_DEF_006.dat",
    output_path="C:\FloodModellerJacobs\Structure Log\output\output3.csv"
)

print("")