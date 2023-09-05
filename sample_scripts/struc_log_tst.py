from sample_scripts.structure_log_oop import StructureLog

log = StructureLog()
input=r"C:\FloodModellerJacobs\Structure Log\DAT_for_API\Bourn_Rea_OBC_BLN_DEF_006.dat"
output=r"C:\FloodModellerJacobs\Structure Log\output\structure_log.csv"
log.create(input, output)