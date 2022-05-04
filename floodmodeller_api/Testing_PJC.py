

from floodmodeller_api import INP, DAT


#temp_dat = DAT(r"C:\Projects\FloodModellerAPI\Development\Example Data\Douglas_2018_DN_002_DesQ.dat")
#temp_dat.update()
temp_inp = INP(r'C:\Projects\FloodModellerAPI\Development\Example Data\example2.inp')
temp_inp.save(r'C:\Projects\FloodModellerAPI\Development\Example Data\example2_out.inp')
pass