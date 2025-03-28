from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from floodmodeller_api import DAT
from floodmodeller_api.units import RIVER


def identify_all_uncut_sections(dat: DAT, output_folder: Path) -> None:
    for section in dat.sections.values():
        if not isinstance(section, RIVER):
            continue
        if bad_indexes := section_not_cut_at_highest_banks(section):
            plot_section(section, bad_indexes, output_folder)


def section_not_cut_at_highest_banks(section: RIVER) -> list[int]:
    bad_indexes = []
    left_bank, right_bank = 0, len(section.active_data) - 1
    left_bank_y, right_bank_y = section.active_data.iloc[0].Y, section.active_data.iloc[-1].Y
    max_y = section.active_data.Y.max()
    max_y_index = int(section.active_data.Y.argmax())
    threshold_max_y = max_y - 0.01
    if (
        left_bank < max_y_index < right_bank
        and threshold_max_y > left_bank_y
        and threshold_max_y > right_bank_y
    ):
        bad_indexes.append(max_y_index)

    bed = int(section.active_data.Y.argmin())
    opposite_bank, opposite_bank_adj = (
        (left_bank, 0) if max_y_index > bed else (right_bank, right_bank + 1)
    )
    start_slice = min(opposite_bank_adj, bed)
    end_slice = max(opposite_bank_adj, bed)
    opposite_side_max = (
        int(section.active_data.iloc[start_slice:end_slice].Y.argmax()) + start_slice
    )

    opposite_bank_y = section.active_data.iloc[opposite_bank].Y
    opposite_side_threshold_y = section.active_data.iloc[opposite_side_max].Y - 0.01

    if opposite_side_max != opposite_bank and opposite_side_threshold_y > opposite_bank_y:
        bad_indexes.append(int(opposite_side_max))

    return bad_indexes


def plot_section(section: RIVER, bad_indexes: list[int], output_folder: Path) -> None:
    fig, ax1 = plt.subplots()

    ax1.plot(section.active_data.X, section.active_data.Y, "#a88b59")
    ax1.fill_between(
        section.active_data.X,
        section.active_data.Y,
        section.active_data.Y.min() - 1,
        color="#ebd4ae",
        alpha=1,
    )
    ax1.set_xlabel("Chainage (m)")
    ax1.set_ylabel("Stage (mAOD)")

    for index in bad_indexes:
        x, y = section.active_data.iloc[index].X, section.active_data.iloc[index].Y
        ax1.plot([x, x], [-10, y], color="red", linestyle="--", linewidth=1.5, alpha=0.4)
        ax1.scatter([x], [y], s=300, facecolors="none", edgecolors="red", linewidths=2, alpha=0.7)
        ax1.text(
            x,
            y,
            f"{y}\n",
            fontsize=10,
            color="red",
            horizontalalignment="center",
            verticalalignment="bottom",
        )

    x, y = section.active_data.iloc[0].X, section.active_data.iloc[0].Y
    ax1.text(
        x,
        y,
        f"{y}",
        fontsize=10,
        color="black",
        horizontalalignment="center",
        verticalalignment="bottom",
    )
    x, y = section.active_data.iloc[-1].X, section.active_data.iloc[-1].Y
    ax1.text(
        x,
        y,
        f"{y}",
        fontsize=10,
        color="black",
        horizontalalignment="center",
        verticalalignment="bottom",
    )

    ax1.set_ylim(section.active_data.Y.min() - 1, section.active_data.Y.max() + 1)
    ax1.set_title(section.name)
    fig.set_size_inches(10, 7)

    # save
    output_name = output_folder / f"{section.name}.png"
    fig.savefig(output_name, bbox_inches="tight")
    plt.close()


if __name__ == "__main__":
    dat = DAT("sample_code/sample_data/EX3.DAT")
    output_folder = Path("uncut_section_plots")
    output_folder.mkdir(parents=True, exist_ok=True)
    identify_all_uncut_sections(dat, output_folder)
