from toolbox.model_conversion.helpers.file_parser import TuflowParser

from pathlib import Path
from shapely.geometry import Point
import pandas as pd
import geopandas as gpd
import pytest


@pytest.fixture
def tuflow_parser(tmpdir) -> Path:

    text = """
    var1 == folder1/file1.csv
    var1 == ../file2.tmf
    var2 == file3 | file4
    var3 == 5 | 7
    var4 == 4.123 !comment
    !var5 == test
    var2 == file5 | file6
    """

    file_path = Path.joinpath(Path(tmpdir), "tuflow_file.txt")

    with open(file_path, "w") as f:
        f.write(text)

    tuflow_parser = TuflowParser(file_path)

    return tuflow_parser


@pytest.fixture
def path1(tmpdir) -> Path:
    return Path(f"{tmpdir}\\folder1\\file1.csv")


@pytest.fixture
def path2(tmpdir) -> Path:
    tmpdir_parent = str(Path(tmpdir).parent)
    return Path(f"{tmpdir_parent}\\file2.tmf")


@pytest.fixture
def path3(tmpdir) -> Path:
    return Path(f"{tmpdir}\\file3")


@pytest.fixture
def path4(tmpdir) -> Path:
    return Path(f"{tmpdir}\\file4")


@pytest.fixture
def path5(tmpdir) -> Path:
    return Path(f"{tmpdir}\\file5")


@pytest.fixture
def path6(tmpdir) -> Path:
    return Path(f"{tmpdir}\\file6")


def test_dict(tuflow_parser):
    assert tuflow_parser._dict == {
        "var1": ["folder1/file1.csv", "../file2.tmf"],
        "var2": ["file3 | file4", "file5 | file6"],
        "var3": ["5 | 7"],
        "var4": ["4.123"],
    }


def test_value(tuflow_parser):
    assert tuflow_parser.get_value("var1") == "../file2.tmf"
    assert tuflow_parser.get_value("var1", index=0) == "folder1/file1.csv"
    assert tuflow_parser.get_value("var2") == "file5 | file6"
    assert tuflow_parser.get_value("var2", index=0) == "file3 | file4"
    assert tuflow_parser.get_value("var3") == "5 | 7"
    assert tuflow_parser.get_value("var4") == "4.123"
    assert tuflow_parser.get_value("var4", cast=float) == 4.123


def test_tuple(tuflow_parser):
    assert tuflow_parser.get_tuple("var2", "|") == ("file5", "file6")
    assert tuflow_parser.get_tuple("var2", "|", index=0) == ("file3", "file4")
    assert tuflow_parser.get_tuple("var3", "|") == ("5", "7")
    assert tuflow_parser.get_tuple("var3", "|", cast=int) == (5, 7)


def test_path(tuflow_parser, path1, path2):
    assert tuflow_parser.get_path("var1") == path2
    assert tuflow_parser.get_path("var1", index=0) == path1


def test_geodataframe(tuflow_parser, mocker, path2):
    read_file = mocker.patch("geopandas.read_file", return_value="test")
    assert tuflow_parser.get_geodataframe("var1") == "test"
    assert read_file.call_count == 1
    assert read_file.call_args_list[0][0][0] == path2


def test_dataframe(tuflow_parser, mocker, path1, path2):

    read_csv = mocker.patch("pandas.read_csv", return_value="test")

    assert tuflow_parser.get_dataframe("var1") == "test"
    assert read_csv.call_count == 1
    assert read_csv.call_args_list[0][0][0] == path2
    assert read_csv.call_args_list[0][1]["comment"] == "!"
    assert read_csv.call_args_list[0][1]["header"] == False

    assert tuflow_parser.get_dataframe("var1", index=0) == "test"
    assert read_csv.call_count == 2
    assert read_csv.call_args_list[1][0][0] == path1
    assert read_csv.call_args_list[1][1]["comment"] == "!"
    assert read_csv.call_args_list[1][1]["header"] == True


def test_single_geometry(tuflow_parser, mocker, path1, path2):

    point1 = Point(0, 1)
    point2 = Point(1, 0)
    gdf = gpd.GeoDataFrame({"x": ["a", "b"], "geometry": [point1, point2]})
    read_gdf = mocker.patch("geopandas.read_file", return_value=gdf)

    assert tuflow_parser.get_single_geometry("var1") == point1
    assert read_gdf.call_count == 1
    assert read_gdf.call_args_list[0][0][0] == path2

    assert tuflow_parser.get_single_geometry("var1", index=0, geom_index=1) == point2
    assert read_gdf.call_count == 2
    assert read_gdf.call_args_list[1][0][0] == path1


def test_all_paths(tuflow_parser, path1, path2):
    assert tuflow_parser.get_all_paths("var1") == [path1, path2]


def test_all_geodataframes(
    tuflow_parser, mocker, path1, path2, path3, path4, path5, path6
):

    read_gdf = mocker.patch("geopandas.read_file", return_value="test")

    assert tuflow_parser.get_all_geodataframes("var1") == ["test", "test"]
    assert read_gdf.call_count == 2
    assert read_gdf.call_args_list[0][0][0] == path1
    assert read_gdf.call_args_list[1][0][0] == path2

    assert tuflow_parser.get_all_geodataframes("var2") == [
        ("test", "test"),
        ("test", "test"),
    ]
    assert read_gdf.call_count == 6
    assert read_gdf.call_args_list[2][0][0] == path3
    assert read_gdf.call_args_list[3][0][0] == path4
    assert read_gdf.call_args_list[4][0][0] == path5
    assert read_gdf.call_args_list[5][0][0] == path6
