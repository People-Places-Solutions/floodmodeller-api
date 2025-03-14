from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from floodmodeller_api import DAT
from floodmodeller_api.units import BRIDGE


def plot_all_bridge_units(dat_path: Path, output_folder: Path) -> None:
    output_folder.mkdir(exist_ok=True, parents=True)
    dat = DAT(dat_path)
    for _, unit in dat.structures.items():
        if not isinstance(unit, BRIDGE):
            continue
        plot_bridge_unit(unit, output_folder)


def plot_bridge_unit(unit: BRIDGE, output_folder: Path):
    # Set up matplotlib plot
    fig, ax1 = plt.subplots()

    x, y = create_bridge_opening_coords(unit)
    ax1.plot(x, y, "grey")
    ax1.fill_between(x, y, y.max() + 1, color="grey", alpha=0.6)

    ax1.plot(unit.section_data.X, unit.section_data.Y, "#a88b59")
    ax1.fill_between(
        unit.section_data.X,
        unit.section_data.Y,
        unit.section_data.Y.min() - 1,
        color="#ebd4ae",
        alpha=1,
    )
    ax1.set_xlabel("Chainage (m)")
    ax1.set_ylabel("Stage (mAOD)")

    ax1.set_ylim(unit.section_data.Y.min() - 1, y.max() + 1)
    ax1.set_aspect(1)
    ax1.set_title(unit.name)
    fig.set_size_inches(20, 10)

    # save
    output_name = output_folder / f"{unit.name}.png"
    fig.savefig(output_name, bbox_inches="tight")


def create_bridge_opening_coords(unit: BRIDGE) -> tuple:
    all_x = [unit.section_data.X.min()]
    all_y = [0]
    for _, start, end, spring, soffit in unit.opening_data.itertuples():
        arch_x = np.linspace(start, end, 100)

        mid_x = (start + end) / 2  # Midpoint of the arch span

        # Define the parabola equation: y = a(x - h)^2 + k
        # where (h, k) is the vertex (midpoint, soffit_y)
        # and it passes through (start_x, springing_y) and (end_x, springing_y)
        a = (spring - soffit) / ((start - mid_x) ** 2)

        # Generate arch points
        arch_y = a * (arch_x - mid_x) ** 2 + soffit

        all_x.extend([start, *arch_x, end])
        all_y.extend([0, *arch_y, 0])

    all_x.append(unit.section_data.X.max())
    all_y.append(0)

    return np.array(all_x), np.array(all_y)


if __name__ == "__main__":
    plot_all_bridge_units(
        dat_path=Path("sample_data/EX3.DAT"), output_folder=Path("bridge_plots")
    )
