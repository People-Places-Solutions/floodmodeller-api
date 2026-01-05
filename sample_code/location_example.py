from floodmodeller_api import DAT

dat = DAT("floodmodeller_api/test/test_data/River_Bridge_no_gxy.dat")
# check if unit is updated when change in allunits vs group


for label in ("M029", "M030", "M031"):
    print(f"{label=}, {dat.sections[label].location=}")
