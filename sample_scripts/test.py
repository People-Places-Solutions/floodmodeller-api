from floodmodeller_api import IEF, DAT
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller_definition import TuflowToFloodModeller as T2FM
from floodmodeller_api.toolbox.model_conversion.tuflow_to_floodmodeller.convert_estry_001_oop import TuflowToDat

#hi = sc1d(ief,r"C:\FloodModellerJacobs\floodmodeller-api\sample_scripts\test_converter",1.123)
#hi.edit_fm_file()
#bye = hi.tuflow_to_dat(r"filepath")

#T2FM.run(
#    tcf_path=r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\runs\EG14_001.tcf",
#    folder=r"C:\FloodModellerJacobs\TUFLOW_data\test",
#    name=r"test_new_1",
#)

#l = DAT(r"C:\FloodModellerJacobs\floodmodeller-api\floodmodeller_api\test\test_data\All Units 4_6.DAT")
#w = l._write()
from floodmodeller_api.units.conduits import CONDUIT
c_block = [
    "CONDUIT",
    "RECTANGULAR",
    "UNIT013",
    "    10.000",
    "MANNING",
    "     1.000     2.000     0.500",
    "   0.04000   0.04000   0.03000",
]
c = CONDUIT(
    unit_block=c_block,
)

networks = []



d = DAT()
t2d = TuflowToDat()
t2d.convert(
    r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model",
    [
        r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_nwk_EG14_channels_001_L.shp",
        r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_nwk_EG14_culverts_001_L.shp",
    ],
    r"C:\FloodModellerJacobs\TUFLOW_data\TUFLOW\model\gis\1d_xs_EG14_001_L.shp", 
    d)
print("")



print("")