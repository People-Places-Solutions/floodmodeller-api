from pathlib import Path

from floodmodeller_api import DAT
from floodmodeller_api.units import FLOODPLAIN, RIVER


def uplift_floodplain_and_river_mannings(dat, uplift_factor):
    for unit in dat._all_units:
        if isinstance(unit, (FLOODPLAIN, RIVER)):
            unit.data["Mannings n"] *= uplift_factor


if __name__ == "__main__":
    dat_filepath = Path("<...>.dat")
    for uplift_factor, suffix in [(0.8, "_Nmin20"), (1.2, "_Nplus20")]:
        dat = DAT(dat_filepath)
        uplift_floodplain_and_river_mannings(dat, uplift_factor)
        new_dat_filepath = dat_filepath.with_stem(dat_filepath.stem + suffix)
        dat.save(new_dat_filepath)
