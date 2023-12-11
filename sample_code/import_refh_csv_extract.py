from pathlib import Path
from typing import Dict

import pandas as pd

from floodmodeller_api import IED
from floodmodeller_api.units import QTBDY

csv_folder = Path("path/to/data/folder")

ied_files: Dict[int, Dict[str, IED]] = {}

# Iterate through each csv export
for csv_file in csv_folder.glob("*"):
    stem_parts = csv_file.stem.split("_")
    node_label = stem_parts[0]
    storm_duration = stem_parts[1]

    data = pd.read_csv(csv_file, index_col=0)
    data.index = pd.TimedeltaIndex(data.index) / pd.Timedelta("1h")  # type: ignore[operator]
    return_periods = [int(col.split()[0]) for col in data.columns[::8]]

    # Iterate through each return period
    for return_period in return_periods:
        flow_data = data[f"Total flow m3/s ({return_period} year)- urbanised model"]
        qtbdy = QTBDY(name=node_label, data=flow_data)  # Builds new QTBDY

        if return_period not in ied_files:
            ied_files[return_period] = {}

        if storm_duration not in ied_files[return_period]:
            ied = IED()  # Create new ied file
            ied.save(
                Path(
                    csv_folder.parent,
                    "output",
                    f"Q{return_period}_{storm_duration}.ied",
                ),
            )
            ied_files[return_period][storm_duration] = ied

        ied = ied_files[return_period][storm_duration]
        ied.boundaries[node_label] = qtbdy  # Add qtbdy unit into IED
        ied.update()  # Update IED file on disk
