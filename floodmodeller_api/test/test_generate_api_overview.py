import matplotlib.pyplot as plt
import pytest
from docs.source.getting_started.generate_api_overview import build_figure, load_fonts, main


def test_build_figure_dark_theme():
    figure = build_figure("dark")
    try:
        assert len(figure.axes) == 1
    finally:
        plt.close(figure)


def test_build_figure_light_theme():
    figure = build_figure("light")
    try:
        assert len(figure.axes) == 1
    finally:
        plt.close(figure)


def test_build_figure_rejects_unknown_theme():
    with pytest.raises(KeyError):
        build_figure("purple")


def test_main_saves_png(tmp_path):
    output = tmp_path / "overview.png"

    main(theme="light", output=output)

    assert output.is_file()
    assert output.stat().st_size > 0


def test_load_fonts_falls_back_when_chronos_missing(tmp_path):
    regular, bold = load_fonts(tmp_path)

    assert regular.get_file() is None
    assert bold.get_file() is None
