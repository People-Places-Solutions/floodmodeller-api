from floodmodeller_api import XML2D
from component_converter import (
    concat,
    rename_and_select,
    filter,
    LocLineConverter,
    TopographyConverter,
    RoughnessConverter,
    SchemeConverter,
    BoundaryConverter,
)

from pathlib import Path
from shapely.geometry import LineString, Polygon
import pandas as pd
import geopandas as gpd
import pytest


@pytest.fixture
def xml():
    return XML2D()


def test_rename_and_select():
    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})

    df1 = rename_and_select(df, {"a": "A", "b": "B"})
    assert df1.equals(pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}))

    df2 = rename_and_select(df, {"aa": "A", "b": "B"})
    assert df2.equals(pd.DataFrame({"B": [4, 5, 6]}))


def test_filter():
    gdf = gpd.GeoDataFrame(
        {
            "code": [0, 1],
            "geometry": [
                Polygon([(0, 0), (1, 1), (1, 0)]),
                Polygon([(0, 0), (1, 1), (0, 1)]),
            ],
        }
    )

    deactive = filter(gdf, column="code", value=0)
    assert deactive.equals(
        gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (1, 0)])]}, index=[0])
    )

    active = filter(gdf, column="code", value=1)
    assert active.equals(
        gpd.GeoDataFrame({"geometry": [Polygon([(0, 0), (1, 1), (0, 1)])]}, index=[1])
    )


def test_concat():
    assert True


@pytest.mark.parametrize(
    "start,end,rotation",
    [
        ((1, 0), (10, 20), 66),
        ((1, 0), (-10, 20), 119),
        ((1, 0), (10, -20), 294),
        ((1, 0), (-10, -20), 241),
    ],
)
def test_loc_line_converter(mocker, tmpdir, xml, start, end, rotation):

    active_area = Path.joinpath(Path(tmpdir), "active_area.shp")
    deactive_area = Path.joinpath(Path(tmpdir), "deactive_area.shp")

    filter = mocker.patch("component_converter.filter")
    loc_line = LocLineConverter(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        dx=2.5,
        lx_ly=(30.3, 40.4),
        all_areas=[gpd.GeoDataFrame()],
        loc_line=LineString([start, end]),
    )
    assert filter.call_count == 2
    assert (filter.call_args_list[0][0][0]).equals(gpd.GeoDataFrame())
    assert (filter.call_args_list[1][0][0]).equals(gpd.GeoDataFrame())
    assert filter.mock_calls[1][1][0] == deactive_area
    assert filter.mock_calls[3][1][0] == active_area

    loc_line.edit_file()
    assert xml.domains["Domain 1"]["computational_area"] == {
        "xll": 1,
        "yll": 0,
        "dx": 2.5,
        "nrows": 12,
        "ncols": 16,
        "active_area": active_area,
        "deactive_area": deactive_area,
        "rotation": rotation,
    }


# TODO:
# concat geodataframes
# topography
# roughness
# scheme
# boundary
# general: model & one component
# 2D: save & rollback

if __name__ == "__main__":
    test_filter()