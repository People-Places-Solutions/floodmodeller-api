from floodmodeller_api import XML2D
from toolbox.model_conversion.helpers.component_converter import (
    concat,
    rename_and_select,
    filter,
    ComponentConverter,
    LocLineConverter,
    TopographyConverter,
    RoughnessConverter,
    SchemeConverter,
)

from pathlib import Path
from shapely.geometry import Point, LineString, Polygon
import pandas as pd
import geopandas as gpd
import numpy as np
import pytest

path_to_cc = "toolbox.model_conversion.helpers.component_converter"


@pytest.fixture
def xml():
    return XML2D()


@pytest.fixture
def point1():
    return Point(0, 1)


@pytest.fixture
def point2():
    return Point(1, 0)


@pytest.fixture
def polygon1():
    return Polygon([(0, 0), (1, 1), (1, 0)])


@pytest.fixture
def polygon2():
    return Polygon([(0, 0), (1, 1), (0, 1)])


@pytest.fixture
def gdf1():
    return gpd.GeoDataFrame({"x": [1], "geometry": [point1]})


@pytest.fixture
def gdf2():
    return gpd.GeoDataFrame({"x": [2], "geometry": [point2]})


def test_concat(polygon1, polygon2, point1, point2):

    gdf_list = [
        gpd.GeoDataFrame({"x": [0, 1], "geometry": [polygon1, polygon2]}),
        gpd.GeoDataFrame({"X": [2], "geometry": [point1]}),
        gpd.GeoDataFrame({"y": [3], "geometry": [point2]}),
    ]

    gdf_concat = concat(gdf_list)
    assert gdf_concat.equals(
        gpd.GeoDataFrame(
            {
                "x": [0, 1, np.nan, np.nan],
                "geometry": [polygon1, polygon2, point1, point2],
                "X": [np.nan, np.nan, 2, np.nan],
                "y": [np.nan, np.nan, np.nan, 3],
            }
        ),
    )

    gdf_concat = concat(gdf_list, lower_case=True)
    assert gdf_concat.equals(
        gpd.GeoDataFrame(
            {
                "x": [0, 1, 2, np.nan],
                "geometry": [polygon1, polygon2, point1, point2],
                "y": [np.nan, np.nan, np.nan, 3],
            }
        ),
    )

    gdf_concat = concat(gdf_list, mapper={"y": "x"})
    assert gdf_concat.equals(
        gpd.GeoDataFrame(
            {
                "x": [0, 1, np.nan, 3],
                "geometry": [polygon1, polygon2, point1, point2],
                "X": [np.nan, np.nan, 2, np.nan],
            }
        ),
    )

    gdf_concat = concat(gdf_list, lower_case=True, mapper={"y": "x"})
    assert gdf_concat.equals(
        gpd.GeoDataFrame(
            {
                "x": [0, 1, 2, 3],
                "geometry": [polygon1, polygon2, point1, point2],
            }
        ),
    )


def test_rename_and_select():

    df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})

    df1 = rename_and_select(df, {"aa": "A", "b": "B"})
    assert df1.equals(pd.DataFrame({"B": [4, 5, 6]}))

    df2 = rename_and_select(df, {"a": "A", "b": "B"})
    assert df2.equals(pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}))


def test_filter(polygon1, polygon2):

    gdf = gpd.GeoDataFrame({"code": [0, 1], "geometry": [polygon1, polygon2]})

    deactive = filter(gdf, column="code", value=0)
    assert deactive.equals(gpd.GeoDataFrame({"geometry": [polygon1]}, index=[0]))

    active = filter(gdf, column="code", value=1)
    assert active.equals(gpd.GeoDataFrame({"geometry": [polygon2]}, index=[1]))


def test_abc():
    abc = ComponentConverter("test")
    with pytest.raises(NotImplementedError):
        abc.edit_fm_file()


@pytest.mark.parametrize(
    "start,end,rotation",
    [
        ((1, 0), (10, 20), 65.772),
        ((1, 0), (-10, 20), 118.811),
        ((1, 0), (10, -20), 294.228),
        ((1, 0), (-10, -20), 241.189),
    ],
)
def test_loc_line_converter(mocker, tmpdir, xml, gdf1, start, end, rotation):

    active_area = Path.joinpath(Path(tmpdir), "active_area.shp")
    deactive_area = Path.joinpath(Path(tmpdir), "deactive_area.shp")

    filter = mocker.patch(f"{path_to_cc}.filter")
    loc_line = LocLineConverter(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        dx=2.5,
        lx_ly=(30.3, 40.4),
        all_areas=[gdf1],
        loc_line=LineString([start, end]),
    )
    assert filter.call_count == 2
    assert (filter.call_args_list[0][0][0]).equals(gdf1)
    assert (filter.call_args_list[1][0][0]).equals(gdf1)
    assert filter.mock_calls[1][1][0] == deactive_area
    assert filter.mock_calls[3][1][0] == active_area

    loc_line.edit_fm_file()
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


def test_combine_layers():

    tuflow_p = gpd.GeoDataFrame(
        {
            "Z": [50.0, 80.0, 90.0, 20.0],
            "dZ": [0, 0, 0, 0],
            "geometry": [Point(2, 0), Point(2, 3), Point(3, 4), Point(4, 4)],
        }
    )
    tuflow_l = gpd.GeoDataFrame(
        {
            "width": [2.0, 3.0],
            "options": ["MAX", "MAX"],
            "geometry": [
                LineString([(2, 0), (2, 4), (3, 4)]),
                LineString([(3, 4), (4, 4)]),
            ],
        }
    )

    combined = TopographyConverter.combine_layers((tuflow_p, tuflow_l))

    assert combined.equals(
        gpd.GeoDataFrame(
            {
                "geometry": [
                    LineString([(2, 0), (2, 3)]),
                    LineString([(2, 3), (2, 4), (3, 4)]),
                    LineString([(3, 4), (4, 4)]),
                ],
                "height1": [50.0, 80.0, 90.0],
                "height2": [80.0, 90.0, 20.0],
                "thick": [2.0, 2.0, 3.0],
            }
        )
    )


def test_topography_converter(mocker, tmpdir, xml, gdf1, gdf2):

    raster_path = str(Path.joinpath(Path(tmpdir), "raster.asc"))
    vector_path = str(Path.joinpath(Path(tmpdir), "topography_0.shp"))

    combine_layers = mocker.patch(f"{path_to_cc}.TopographyConverter.combine_layers")
    topography_converter = TopographyConverter(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        rasters=[raster_path],
        vectors=[(gdf1, gdf2)],
    )
    assert combine_layers.call_count == 1
    assert (combine_layers.call_args_list[0][0][0][0]).equals(gdf1)
    assert (combine_layers.call_args_list[0][0][0][1]).equals(gdf2)
    assert combine_layers.mock_calls[1][1][0] == vector_path

    topography_converter.edit_fm_file()
    assert xml.domains["Domain 1"]["topography"] == [raster_path, vector_path]


def test_material_to_roughness(point1, polygon1, polygon2):

    roughness = RoughnessConverter.material_to_roughness(
        [
            gpd.GeoDataFrame({"material": [7, 3], "geometry": [polygon1, polygon2]}),
            gpd.GeoDataFrame({"material": [5], "geometry": [point1]}),
        ],
        pd.DataFrame({"material_id": [3, 5, 7], "value": [0.1, 0.9, 0.7]}),
    )

    assert roughness.equals(
        gpd.GeoDataFrame(
            {"value": [0.7, 0.1, 0.9], "geometry": [polygon1, polygon2, point1]}
        )
    )


def test_roughness_converter(mocker, tmpdir, xml, gdf1, gdf2):

    roughness_path = Path.joinpath(Path(tmpdir), "roughness.shp")
    mapping = pd.DataFrame({"A": [3], "B": [0.1], "C": ["D"]})
    standardised_mapping = pd.DataFrame({"material_id": [3], "value": [0.1]})

    material_to_roughness = mocker.patch(
        f"{path_to_cc}.RoughnessConverter.material_to_roughness"
    )
    roughness_converter = RoughnessConverter(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        law="manning",
        global_material=3,
        file_material=[gdf1, gdf2],
        mapping=mapping,
    )
    assert material_to_roughness.call_count == 1
    assert (material_to_roughness.call_args_list[0][0][0][0]).equals(gdf1)
    assert (material_to_roughness.call_args_list[0][0][0][1]).equals(gdf2)
    assert (material_to_roughness.call_args_list[0][0][1]).equals(standardised_mapping)
    assert material_to_roughness.mock_calls[1][1][0] == roughness_path

    roughness_converter.edit_fm_file()
    assert xml.domains["Domain 1"]["roughness"] == [
        {
            "type": "global",
            "law": "manning",
            "value": 0.1,
        },
        {
            "type": "file",
            "law": "manning",
            "value": roughness_path,
        },
    ]


@pytest.mark.parametrize(
    "in_scheme, in_hardware, fm_scheme, fm_proc",
    [
        ("HPC", "GPU", "TVD", "GPU"),
        ("HPC", "CPU", "ADI", "CPU"),
        ("Classic", "GPU", "ADI", "CPU"),
        ("x", "y", "ADI", "CPU"),
    ],
)
def test_scheme_converter(tmpdir, xml, in_scheme, in_hardware, fm_scheme, fm_proc):

    scheme_converter = SchemeConverter(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        time_step=0.5,
        start_offset=3,
        total=5,
        scheme=in_scheme,
        hardware=in_hardware,
    )
    scheme_converter.edit_fm_file()

    assert xml.domains["Domain 1"]["time"] == {
        "start_offset": 3,
        "total": 5,
    }
    assert xml.domains["Domain 1"]["run_data"] == {
        "time_step": 0.5,
        "scheme": fm_scheme,
    }
    assert xml.processor == {"type": fm_proc}
