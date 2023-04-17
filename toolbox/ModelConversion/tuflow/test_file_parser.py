from file_parser import TuflowParser

from pathlib import Path
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import pytest


@pytest.fixture
def tuflow_parser(tmpdir) -> Path:

    text = """
    var1 == folder1/file1
    var1 == file2
    var2 == a | b
    var3 == 5 | 7
    var4 == 4.123 !comment
    !var5 == test
    var2 == c | d
    """

    file_path = Path.joinpath(Path(tmpdir), "tuflow_file.txt")

    with open(file_path, "w") as f:
        f.write(text)

    tuflow_parser = TuflowParser(file_path)

    return tuflow_parser


@pytest.fixture
def path1(tmpdir) -> Path:
    return Path(f"{tmpdir}\\folder1\\file1")


@pytest.fixture
def path2(tmpdir) -> Path:
    return Path(f"{tmpdir}\\file2")


def test_dict(tuflow_parser):
    assert tuflow_parser._dict == {
        "var1": ["folder1/file1", "file2"],
        "var2": ["a | b", "c | d"],
        "var3": ["5 | 7"],
        "var4": ["4.123"],
    }


def test_value(tuflow_parser):
    assert tuflow_parser.get_value("var1") == "file2"
    assert tuflow_parser.get_value("var1", index=0) == "folder1/file1"
    assert tuflow_parser.get_value("var2") == "c | d"
    assert tuflow_parser.get_value("var2", index=0) == "a | b"
    assert tuflow_parser.get_value("var3") == "5 | 7"
    assert tuflow_parser.get_value("var4") == "4.123"
    assert tuflow_parser.get_value("var4", cast=float) == 4.123


def test_tuple(tuflow_parser):
    assert tuflow_parser.get_tuple("var2", "|") == ("c", "d")
    assert tuflow_parser.get_tuple("var2", "|", index=0) == ("a", "b")
    assert tuflow_parser.get_tuple("var3", "|") == ("5", "7")
    assert tuflow_parser.get_tuple("var3", "|", cast=int) == (5, 7)


def test_path(tuflow_parser, path1, path2):
    assert tuflow_parser.get_path("var1") == path2
    assert tuflow_parser.get_path("var1", index=0) == path1


def test_geodataframe(tuflow_parser, mocker, path2):
    empty_gdf = gpd.GeoDataFrame()
    read_gdf = mocker.patch("geopandas.read_file", return_value=empty_gdf)
    assert tuflow_parser.get_geodataframe("var1").equals(empty_gdf)
    assert read_gdf.call_count == 1
    assert str(read_gdf.call_args_list[0][0][0]) == str(path2)


def test_dataframe(tuflow_parser, mocker, path2):
    empty_df = pd.DataFrame()
    read_df = mocker.patch("pandas.read_csv", return_value=empty_df)
    assert tuflow_parser.get_dataframe("var1").equals(empty_df)
    assert read_df.call_count == 1
    assert str(read_df.call_args_list[0][0][0]) == str(path2)
    assert str(read_df.call_args_list[0][1]["comment"]) == "!"


def test_single_geometry(tuflow_parser, mocker, path1, path2):

    point1 = Point(0, 1)
    point2 = Point(1, 0)
    gdf = gpd.GeoDataFrame({"x": ["a", "b"], "geometry": [point1, point2]})
    read_gdf = mocker.patch("geopandas.read_file", return_value=gdf)

    assert tuflow_parser.get_single_geometry("var1") == point1
    assert read_gdf.call_count == 1
    assert str(read_gdf.call_args_list[0][0][0]) == str(path2)

    assert tuflow_parser.get_single_geometry("var1", index=0, geom_index=1) == point2
    assert read_gdf.call_count == 2
    assert str(read_gdf.call_args_list[1][0][0]) == str(path1)


def test_all_paths(tuflow_parser, path1, path2):
    assert tuflow_parser.get_all_paths("var1") == [path1, path2]


def test_all_geodataframes(tuflow_parser, mocker, path1, path2):
    empty_gdf = gpd.GeoDataFrame()
    read_gdf = mocker.patch("geopandas.read_file", return_value=empty_gdf)
    result = tuflow_parser.get_all_geodataframes("var1")
    assert len(result) == 2
    assert type(result) == list
    assert result[0].equals(empty_gdf)
    assert result[1].equals(empty_gdf)
    assert read_gdf.call_count == 2
    assert str(read_gdf.call_args_list[0][0][0]) == str(path1)
    assert str(read_gdf.call_args_list[1][0][0]) == str(path2)