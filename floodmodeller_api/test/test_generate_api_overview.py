"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""
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
