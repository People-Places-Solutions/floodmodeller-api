"""Generate an overview diagram for the Flood Modeller Python API.

The diagram is deliberately data-driven: edit the card definitions below to
change the wording or grouping without changing the drawing code.

Usage::

    python scripts/generate_api_overview.py
    python scripts/generate_api_overview.py --output docs/source/getting_started/api_overview_current.png
    python scripts/generate_api_overview.py --theme light

Requires matplotlib (already used by the repository's documentation/examples).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.font_manager import FontProperties
from matplotlib.patches import FancyBboxPatch

def load_fonts(font_dir=Path(r"C:\Windows\Fonts")):
    regular_path = font_dir / "JACOBSCHRONOS_RG.ttf"
    bold_path = font_dir / "JACOBSCHRONOS_BD.ttf"

    if regular_path.exists() and bold_path.exists():
        font_manager.fontManager.addfont(regular_path)
        font_manager.fontManager.addfont(bold_path)
        return (
            FontProperties(fname=regular_path),
            FontProperties(fname=bold_path),
        )

    # CI or another machine without the Jacobs fonts
    return FontProperties(), FontProperties(weight="bold")


CHRONOS_REGULAR, CHRONOS_BOLD = load_fonts()

DARK_COLORS = {
    "background": "#242424",
    "frame": "#777777",
    "overview": "#1f61aa",
    "coming_soon": "#a85c2b",
    "feature": "#0bd18b",
    "format": "#147cf0",
    "capability": "#061a32",
    "future": "#ef7d2c",
    "text": "#f8f8f8",
    "muted": "#d8d8d8",
    "card_text": "#ffffff",
}

LIGHT_COLORS = {
    "background": "#f4f6f8",
    "frame": "#68727d",
    "overview": "#b9d8f5",
    "coming_soon": "#f0c5a8",
    "feature": "#35b98a",
    "format": "#65a8ed",
    "capability": "#c7d8e8",
    "future": "#f2a56f",
    "text": "#16202a",
    "muted": "#4d5965",
    "card_text": "#16202a",
}

COLORS = DARK_COLORS


# Coordinates are in a 0..100 by 0..50 design space.  Each card is
# (title, description); descriptions can contain a newline.
USER_FEATURES = [
    (
        "Interoperable with common\nPython data formats",
        "Pandas, GeoPandas and standard\nPython data workflows",
    ),
    (
        "Simple scripting syntax",
        "Use familiar Python objects to\nread, edit, validate and save models",
    ),
    (
        "Community-driven\ndevelopment",
        "Share scripts, tools and ideas\nthrough the open-source project",
    ),
]

FILE_FORMATS = [
    ("DAT", ""),
    ("IED", ""),
    ("IEF", ""),
    ("INP", ""),
    ("XML2D", ""),
    ("ZZN / ZZX", ""),
]

CAPABILITIES = [
    ("Rich unit \nclasses", "Work with rivers, bridges,\nweirs, culverts and boundaries"),
    ("Cross class \nfunctions", "Easily work between \n files and references"),
    ("Logs and \ndiagnostics", "Read log files and inspect\nresults and convergence"),
    ("Automate \nmodel build", "Build and update models\nprogrammatically"),
    ("Safe model \nediting", "Compare, back up, serialise\nand restore model data"),
    ("Integrate \nHydrology+", "Import and export hydrology\ndata for workflows"),
    ("Develop in the \n cloud", "Build and run tools on \nGitHub Codespaces"),
    ("Urban 1D", "Represent conduits, junctions,\noutfalls and rain gauges"),
    ("Advanced results\nanalysis", "Read and analyse \nresults fast"),
    ("Validation", "Check model parameters\nagainst supported rules"),
    ("API toolbox", "Reusable model-build and\nanalysis tools"),
    ("Work beyond \nFlood Modeller", "Connect model data to the\nwider Python ecosystem"),
]

FUTURE = [
    ("New units coming soon", "Fullarch, gated weir, vertical\nand radial sluices"),
    ("Share your tools", "Contribute examples and ideas\nthrough the project community"),
]


def rounded_box(ax, x, y, width, height, color, radius=0.8, edgecolor=None, linewidth=0.8):
    """Add a rounded rectangle in design-space coordinates."""
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle=f"round,pad=0.18,rounding_size={radius}",
        facecolor=color,
        edgecolor=edgecolor or color,
        linewidth=linewidth,
    )
    ax.add_patch(patch)
    return patch


def card(ax, x, y, width, height, title, description, color, title_size=10.5):
    rounded_box(ax, x, y, width, height, color)
    ax.text(
        x + width / 2,
        y + height * 0.61,
        title,
        ha="center",
        va="center",
        color=COLORS["text"],
        fontsize=title_size,
        fontproperties=CHRONOS_BOLD,
        linespacing=1.1,
    )
    ax.text(
        x + width / 2,
        y + height * 0.25,
        description,
        ha="center",
        va="center",
        color=COLORS["card_text"],
        fontsize=6.2,
        fontproperties=CHRONOS_REGULAR,
        linespacing=1.05,
        wrap=True,
    )


def section_label(ax, label, top, bottom):
    """Draw the old diagram's left-hand grouping brace and label."""
    y = (top + bottom) / 2
    ax.text(
        8.0,
        y,
        label,
        ha="right",
        va="center",
        color=COLORS["text"],
        fontsize=8.2,
        fontproperties=CHRONOS_BOLD,
        linespacing=1.05,
    )
    ax.plot(
        [10.8, 10.8],
        [bottom + 0.4, top - 0.4],
        color=COLORS["frame"],
        linewidth=1.5,
        solid_capstyle="round",
    )


def build_figure(theme: str = "dark") -> plt.Figure:
    global COLORS
    COLORS = {"dark": DARK_COLORS, "light": LIGHT_COLORS}[theme]
    fig, ax = plt.subplots(figsize=(16, 8.5), dpi=160)
    fig.patch.set_facecolor(COLORS["background"])
    ax.set_facecolor(COLORS["background"])
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 50)
    ax.axis("off")

    # Outer frame and title tab, matching the supplied overview's visual language.
    rounded_box(ax, 0.5, 0.5, 99, 49, "none", radius=1.0, edgecolor=COLORS["frame"], linewidth=1.6)
    ax.text(
        5,
        49.1,
        "Flood Modeller API",
        color=COLORS["text"],
        fontsize=17,
        fontproperties=CHRONOS_BOLD,
        va="center",
        bbox={"facecolor": COLORS["background"], "pad": 4, "edgecolor": "none"},
    )

    # Main overview panel and future panel.
    rounded_box(ax, 15, 1.3, 66.5, 46.8, COLORS["overview"], radius=1.3)
    rounded_box(ax, 82.5, 1.3, 16.0, 46.8, COLORS["coming_soon"], radius=1.3)
    ax.text(
        48.25,
        45.8,
        "Overview",
        ha="center",
        va="center",
        color=COLORS["text"],
        fontsize=14,
        fontproperties=CHRONOS_BOLD,
    )
    ax.text(
        90.5,
        45.8,
        "Coming soon",
        ha="center",
        va="center",
        color=COLORS["text"],
        fontsize=12,
        fontproperties=CHRONOS_BOLD,
    )

    section_label(ax, "User\nfacing", 43.8, 31.9)
    card(ax, 15.8, 38.0, 31.4, 5.8, *USER_FEATURES[0], COLORS["feature"], title_size=10.5)
    card(ax, 15.8, 31.9, 31.4, 5.2, *USER_FEATURES[1], COLORS["feature"], title_size=11)
    card(ax, 48.2, 31.9, 32.2, 11.9, *USER_FEATURES[2], "#b000a8", title_size=11)

    section_label(ax, "Core\nclasses", 28.5, 23.1)
    format_width = 10.05
    for index, (title, description) in enumerate(FILE_FORMATS):
        card(
            ax,
            15.8 + index * 10.75,
            23.1,
            format_width,
            5.4,
            title,
            description,
            COLORS["format"],
            title_size=8.5,
        )

    section_label(ax, "Extensive\nfunctionality", 22.2, 2.2)
    for index, (title, description) in enumerate(CAPABILITIES):
        row, column = divmod(index, 4)
        card(
            ax,
            15.8 + column * 16.1,
            16.2 - row * 7.0,
            15.0,
            6.0,
            title,
            description,
            COLORS["capability"],
            title_size=8.2,
        )

    for index, (title, description) in enumerate(FUTURE):
        card(
            ax,
            83.2,
            37.0 - index * 7.7,
            14.6,
            6.3,
            title,
            description,
            COLORS["future"],
            title_size=9.0,
        )
    
    card(
        ax,
        83.2,
        5.0,
        14.6,
        8.4,
        "Have your say",
        "Suggest features, report issues\nand help shape the API",
        COLORS["future"],
        title_size=9.0,
    )
    return fig


def main(
    theme: str = "dark",
    output: Path = Path("docs/source/getting_started/api_overview.png"),
) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)

    figure = build_figure(theme)
    figure.savefig(
        output,
        dpi=220,
        facecolor=figure.get_facecolor(),
        bbox_inches="tight",
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
