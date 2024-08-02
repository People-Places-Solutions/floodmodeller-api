from pathlib import Path

from hydrograph import HydrographPlusExport


def load_hydrology_plus_csv_export(file: Path):  # initially, the argument was csv: Path

    return HydrographPlusExport(file)


if __name__ == "__main__":
    load_hydrology_plus_csv_export(
        Path(r"..\floodmodeller-api\floodmodeller_api\test\test_data\Baseline_unchecked.csv"),
    )
