from floodmodeller_api import IEF, DAT
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller_definition import TuflowToFloodModeller as T2FM
ief = IEF()

#hi = sc1d(ief,r"C:\FloodModellerJacobs\floodmodeller-api\sample_scripts\test_converter",1.123)
#hi.edit_fm_file()
#bye = hi.tuflow_to_dat(r"filepath")

T2FM.run(
    tcf_path=r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\runs\EG14_001.tcf",
    folder=r"C:\FloodModellerJacobs\TUFLOW_data\test",
    name=r"test_new_9",
)


print("")