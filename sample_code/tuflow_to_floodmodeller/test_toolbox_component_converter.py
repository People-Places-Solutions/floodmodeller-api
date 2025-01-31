from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pytest
from shapely.geometry import LineString, Point, Polygon

from floodmodeller_api import DAT, IEF, XML2D

from .component_converter import (
    BoundaryConverterXML2D,
    ComponentConverter,
    ComponentConverterDAT,
    ComponentConverterIEF,
    ComponentConverterXML2D,
    ComputationalAreaConverterXML2D,
    LocLineConverterXML2D,
    RoughnessConverterXML2D,
    SchemeConverterIEF,
    SchemeConverterXML2D,
    TopographyConverterXML2D,
    concat,
    filter_dataframe,
    rename_and_select,
)

path_to_cc = "sample_code.tuflow_to_floodmodeller.component_converter"


@pytest.fixture()
def xml():
    return XML2D()


@pytest.fixture()
def ief():
    return IEF()


@pytest.fixture()
def point1():
    return Point(0, 1)


@pytest.fixture()
def point2():
    return Point(1, 0)


@pytest.fixture()
def polygon1():
    return Polygon([(0, 0), (1, 1), (1, 0)])


@pytest.fixture()
def polygon2():
    return Polygon([(0, 0), (1, 1), (0, 1)])


@pytest.fixture()
def gdf1(point1):
    return gpd.GeoDataFrame({"x": [1], "geometry": [point1]})


@pytest.fixture()
def gdf2(point2):
    return gpd.GeoDataFrame({"x": [0], "geometry": [point2]})


@pytest.fixture()
def tuflow_p():
    return gpd.GeoDataFrame(
        {
            "a": [50.0, 80.0, 90.0, 20.0],
            "b": [0, 0, 0, 0],
            "c": np.nan,
            "d": np.nan,
            "geometry": [Point(2, 0), Point(2, 3), Point(3, 4), Point(4, 4)],
        },
    )


@pytest.fixture()
def tuflow_l():
    return gpd.GeoDataFrame(
        {
            "e": np.nan,
            "f": np.nan,
            "g": [2.0, 3.0],
            "h": ["MAX", "MAX"],
            "geometry": [
                LineString([(2, 0), (2, 4), (3, 4)]),
                LineString([(3, 4), (4, 4)]),
            ],
        },
    )


@pytest.fixture()
def tuflow_r():
    return gpd.GeoDataFrame(
        {
            "a": [2.0, 3.0],
            "b": np.nan,
            "c": np.nan,
            "d": ["ADD", "add"],
            "geometry": [
                Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
                Polygon([[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]),
            ],
        },
    )


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
            },
        ),
    )


def test_rename_and_select():
    original_data = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})

    selected_renamed_data_1 = rename_and_select(original_data, {"aa": "A", "b": "B"})
    assert selected_renamed_data_1.equals(pd.DataFrame({"B": [4, 5, 6]}))

    selected_renamed_data_2 = rename_and_select(original_data, {"a": "A", "b": "B"})
    assert selected_renamed_data_2.equals(pd.DataFrame({"A": [1, 2, 3], "B": [4, 5, 6]}))


def test_filter(polygon1, polygon2):
    gdf = gpd.GeoDataFrame({"code": [0, 1], "geometry": [polygon1, polygon2]})

    deactive = filter_dataframe(gdf, column="code", value=0)
    assert deactive.equals(gpd.GeoDataFrame({"geometry": [polygon1]}, index=[0]))

    active = filter_dataframe(gdf, column="code", value=1)
    assert active.equals(gpd.GeoDataFrame({"geometry": [polygon2]}, index=[1]))


def test_abc():
    abc = ComponentConverter("test")
    with pytest.raises(NotImplementedError):
        abc.edit_fm_file()

    abc = ComponentConverterDAT(DAT, "test")
    with pytest.raises(NotImplementedError):
        abc.edit_fm_file()

    abc = ComponentConverterIEF(IEF, "test")
    with pytest.raises(NotImplementedError):
        abc.edit_fm_file()

    abc = ComponentConverterXML2D(XML2D, "test", "test")
    with pytest.raises(NotImplementedError):
        abc.edit_fm_file()


def test_computational_area_converter(tmpdir, xml, gdf1, gdf2, point1, point2):
    active_area_path = Path.joinpath(Path(tmpdir), "active_area.shp")
    deactive_area_path = Path.joinpath(Path(tmpdir), "deactive_area.shp")

    comp_area = ComputationalAreaConverterXML2D(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        xll=3,
        yll=2,
        dx=2.5,
        lx_ly=(30.3, 40.4),
        all_areas=[gdf1, gdf2],
    )
    assert gpd.read_file(active_area_path).equals(
        gpd.GeoDataFrame({"FID": 0, "geometry": [point1]}),
    )
    assert gpd.read_file(deactive_area_path).equals(
        gpd.GeoDataFrame({"FID": 0, "geometry": [point2]}),
    )

    comp_area.edit_fm_file()
    assert xml.domains["Domain 1"]["computational_area"] == {
        "xll": 3,
        "yll": 2,
        "dx": 2.5,
        "nrows": 12,
        "ncols": 16,
        "active_area": active_area_path,
        "deactive_area": deactive_area_path,
    }


@pytest.mark.parametrize(
    ("start", "end", "rotation"),
    [
        ((1, 0), (10, 20), 65.772),
        ((1, 0), (-10, 20), 118.811),
        ((1, 0), (10, -20), 294.228),
        ((1, 0), (-10, -20), 241.189),
    ],
)
def test_loc_line_converter(tmpdir, xml, gdf1, start, end, rotation):
    loc_line = LocLineConverterXML2D(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        dx=2.5,
        lx_ly=(30.3, 40.4),
        all_areas=[gdf1],
        loc_line=LineString([start, end]),
    )

    loc_line.edit_fm_file()
    assert xml.domains["Domain 1"]["computational_area"] == {
        "xll": 1.0,
        "yll": 0.0,
        "dx": 2.5,
        "nrows": 12,
        "ncols": 16,
        "rotation": rotation,
        "active_area": Path(tmpdir, "active_area.shp"),
    }


def test_convert_points_and_lines(tuflow_p, tuflow_l):
    combined = TopographyConverterXML2D.combine_layers((tuflow_p, tuflow_l))

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
            },
        ),
    )


def test_convert_polygons(tuflow_r):
    combined = TopographyConverterXML2D.combine_layers((tuflow_r,))

    assert combined.equals(
        gpd.GeoDataFrame(
            {
                "height": [2.0, 3.0],
                "method": ["add", np.nan],
                "geometry": [
                    Polygon([[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]),
                    Polygon([[0, 0], [2, 0], [2, 2], [0, 2], [0, 0]]),
                ],
            },
        ),
    )


def test_convert_unsupported_shape(tuflow_p, tuflow_l, tuflow_r):
    with pytest.raises(RuntimeError) as e:
        TopographyConverterXML2D.combine_layers((tuflow_l,))
    assert str(e.value) == "Combination not supported: lines"

    with pytest.raises(RuntimeError) as e:
        TopographyConverterXML2D.combine_layers((tuflow_p,))
    assert str(e.value) == "Combination not supported: points"

    with pytest.raises(RuntimeError) as e:
        TopographyConverterXML2D.combine_layers((tuflow_l, tuflow_r))
    assert str(e.value) == "Combination not supported: lines, polygons"

    with pytest.raises(RuntimeError) as e:
        TopographyConverterXML2D.combine_layers((tuflow_p, tuflow_r))
    assert str(e.value) == "Combination not supported: points, polygons"

    with pytest.raises(RuntimeError) as e:
        TopographyConverterXML2D.combine_layers((tuflow_l, tuflow_p, tuflow_r))
    assert str(e.value) == "Combination not supported: lines, points, polygons"


@pytest.mark.parametrize("tuple_input", [True, False])
def test_topography_converter(mocker, tmpdir, xml, gdf1, gdf2, tuple_input):
    inputs = (gdf1, gdf2) if tuple_input else gdf1
    outputs = (gdf1, gdf2) if tuple_input else (gdf1,)

    raster_path = str(Path(tmpdir, "raster.asc"))
    vector_path = str(Path(tmpdir, "topography_0.shp"))

    combine_layers = mocker.patch(f"{path_to_cc}.TopographyConverterXML2D.combine_layers")
    topography_converter = TopographyConverterXML2D(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        rasters=[raster_path],
        vectors=[inputs],
    )
    assert combine_layers.call_count == 1
    for i, gdf in enumerate(outputs):
        assert (combine_layers.call_args_list[0][0][0][i]).equals(gdf)
    assert combine_layers.mock_calls[1][1][0] == vector_path

    topography_converter.edit_fm_file()
    assert xml.domains["Domain 1"]["topography"] == [raster_path, vector_path]


def test_material_to_roughness(point1, polygon1, polygon2):
    roughness = RoughnessConverterXML2D.material_to_roughness(
        gpd.GeoDataFrame({"material_id": [7, 3, 5], "geometry": [polygon1, polygon2, point1]}),
        pd.DataFrame({"material_id": [3, 5, 7], "value": [0.1, 0.9, 0.7]}),
    )

    assert roughness.equals(
        gpd.GeoDataFrame({"value": [0.7, 0.1, 0.9], "geometry": [polygon1, polygon2, point1]}),
    )


def test_roughness_converter(mocker, tmpdir, xml, gdf1, gdf2, point1, point2):
    roughness_path = Path.joinpath(Path(tmpdir), "roughness.shp")
    mapping = pd.DataFrame({"A": [3], "B": [0.1], "C": ["D"]})
    standardised_material = gpd.GeoDataFrame({"material_id": [1, 0], "geometry": [point1, point2]})
    standardised_mapping = pd.DataFrame({"material_id": [3], "value": [0.1]})

    material_to_roughness = mocker.patch(
        f"{path_to_cc}.RoughnessConverterXML2D.material_to_roughness",
    )
    roughness_converter = RoughnessConverterXML2D(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        law="manning",
        global_material=3,
        file_material=[gdf1, gdf2],
        mapping=mapping,
    )
    assert material_to_roughness.call_count == 1
    assert (material_to_roughness.call_args_list[0][0][0]).equals(standardised_material)
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
    ("in_scheme", "in_hardware", "fm_scheme", "fm_proc"),
    [
        ("HPC", "GPU", "TVD", "GPU"),
        ("HPC", "CPU", "ADI", "CPU"),
        ("Classic", "GPU", "ADI", "CPU"),
        ("x", "y", "ADI", "CPU"),
    ],
)
def test_scheme_converter_2d(tmpdir, xml, in_scheme, in_hardware, fm_scheme, fm_proc):
    scheme_converter = SchemeConverterXML2D(
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


def test_boundary_converter(tmpdir, xml, gdf1, gdf2):
    boundary_converter = BoundaryConverterXML2D(
        xml=xml,
        folder=Path(tmpdir),
        domain_name="Domain 1",
        vectors=[gdf1, gdf2],
    )
    with pytest.raises(NotImplementedError):
        boundary_converter.edit_fm_file()


def test_scheme_converter_1d(tmpdir, ief):
    scheme_converter = SchemeConverterIEF(
        ief=ief,
        folder=Path(tmpdir),
        time_step=3,
    )
    scheme_converter.edit_fm_file()

    assert ief.Timestep == 3
