from pathlib import Path

import pytest

from floodmodeller_api import XML2D
from floodmodeller_api.test.util import id_from_path, parameterise_glob
from floodmodeller_api.util import FloodModellerAPIError


@pytest.fixture()
def xml_fp(test_workspace) -> Path:
    return Path(test_workspace, "Domain1_Q.xml")


@pytest.fixture()
def data_before(xml_fp: Path):
    return XML2D(xml_fp)._write()


def test_xml2d_str_representation(xml_fp: Path, data_before):
    """XML2D: Test str representation equal to xml file with no changes"""
    x2d = XML2D(xml_fp)
    assert x2d._write() == data_before


def test_xml2d_link_dtm_changes(xml_fp: Path, data_before):
    """XML2D: Test changing and reverting link1d file and dtm makes no changes"""
    x2d = XML2D(xml_fp)
    prev_link = x2d.link1d["link"]
    domain = next(iter(x2d.domains))
    prev_dtm = x2d.domains[domain]["topography"]

    x2d.link1d["link"] = ["new_link"]
    x2d.domains[domain]["topography"] = ["new_dtm"]
    assert x2d._write() != data_before

    x2d.link1d["link"] = prev_link
    x2d.domains[domain]["topography"] = prev_dtm
    assert x2d._write() == data_before


@pytest.mark.parametrize("xml_file", parameterise_glob("*.xml"), ids=id_from_path)
def test_xml2d_all_files(tmpdir, xml_file):
    """XML2D: Check all '.xml' files in folder by reading the _write() output into a
    new XML2D instance and checking it stays the same."""
    x2d = XML2D(xml_file)
    first_output = x2d._write()
    new_path = Path(tmpdir) / "tmp.xml"
    x2d.save(new_path)
    second_x2d = XML2D(new_path)
    assert x2d == second_x2d
    second_output = second_x2d._write()
    assert first_output == second_output


def test_xml2d_change_revert_elem_topography():
    """XML2D: Check that when we change an existing element
    that it is actually adding it and that it is being reverted."""
    x2d = XML2D()
    domain = next(iter(x2d.domains))
    orig_topography = [str(item) for item in x2d.domains[domain]["topography"]]
    orig_xml = x2d._write()
    x2d.domains[domain]["topography"][0] = "my/new/topography"

    assert x2d._write() != orig_xml
    assert "my/new/topography" in x2d._write()
    x2d.domains[domain]["topography"] = orig_topography
    assert x2d._write() == orig_xml
    assert "my/new/topography" not in x2d._write()


def test_xml2d_add_remove_branch_roughness():
    """XML2D: Check that we can actually add a branch and that
    it is being added and passes validation (i.e write)"""
    x2d = XML2D()
    domain = next(iter(x2d.domains))
    orig_xml = x2d._write()
    x2d.domains[domain]["roughness"] = []
    x2d.domains[domain]["roughness"].append(
        {"type": "file", "law": "manning", "value": "my/roughness/file.shp"},
    )
    assert x2d._write() != orig_xml
    assert "my/roughness/file.shp" in x2d._write()
    del x2d.domains[domain]["roughness"]
    assert x2d._write() == orig_xml
    assert "my/roughness/file.shp" not in x2d._write()


def test_xml2d_append_remove_branch_roughness():
    """XML2D: Check that we can append an extra branch to preexisting branch
    so that it passes validation"""
    x2d = XML2D()
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["roughness"] = []
    x2d.domains[domain]["roughness"].append(
        {"type": "file", "law": "manning", "value": "my/roughness/file.shp"},
    )
    xml_1_roughness = x2d._write()
    x2d.domains[domain]["roughness"].append(
        {"type": "file", "law": "manning", "value": "new/roughness/file.shp"},
    )

    assert x2d._write() != xml_1_roughness
    assert "new/roughness/file.shp" in x2d._write()

    del x2d.domains[domain]["roughness"][1]

    assert "new/roughness/file.shp" not in x2d._write()


def test_xml2d_reorder_elem_computational_area_wrong_position():
    """XML2D: Check that if we add ??? in the wrong position does it reorder"""
    x2d = XML2D()
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["computational_area"] = {
        "yll": ...,
        "xll": ...,
        "dx": ...,
        "active_area": ...,
        "ncols": ...,
        "nrows": ...,
        "rotation": ...,
    }
    x2d.domains[domain]["computational_area"]["yll"] = 1.1
    x2d.domains[domain]["computational_area"]["xll"] = 2.6
    x2d.domains[domain]["computational_area"]["dx"] = float(2)
    x2d.domains[domain]["computational_area"]["active_area"] = "path/to/asc/file.asc"
    x2d.domains[domain]["computational_area"]["ncols"] = 12
    x2d.domains[domain]["computational_area"]["nrows"] = 42
    x2d.domains[domain]["computational_area"]["rotation"] = 3.14159
    x2d.domains[domain]["run_data"]["upwind"] = "upwind value"
    x2d.domains[domain]["run_data"]["wall"] = "Humpty Dumpty"
    assert x2d._write()

    x2d.domains[domain]["run_data"]["upwind123"] = "upwind value"
    with pytest.raises(FloodModellerAPIError):
        assert x2d._write()


def test_xml2d_update_value(xml_fp: Path):
    """XML2D: Test changing and reverting link1d file and dtm makes no changes"""
    x2d = XML2D(xml_fp)
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["run_data"]["scheme"] = "TVD"

    assert x2d._write()


def test_xml2d_change_schema_versions(tmp_path: Path):
    x2d = XML2D()
    x2d.save(tmp_path / "test.xml")
    domain = next(iter(x2d.domains))

    x2d.domains[domain]["topography_2"] = [  # valid in v7.3 but not v6.1
        {"type": "standard", "filelist": {"fmfile": [{"type": "tif", "value": "hi.tif"}]}},
    ]
    assert x2d._schema_version == "7.3"
    x2d.update()  # includes validate

    x2d._update_schema_version("7.2")
    assert x2d._schema_version == "7.2"
    x2d.update()  # includes validate

    x2d._update_schema_version("6.1")
    assert x2d._schema_version == "6.1"
    with pytest.raises(FloodModellerAPIError, match="XML Validation Error"):
        x2d.update()  # includes validate


def test_xml2d_deals_with_non_fm_schemas(tmp_path: Path):
    fake_namespace = "https://example.com/not-flood-modeller"
    fake_schema = "https://example.com/not-flood-modeller/fake.xsd"
    fake_schema_location = f"{fake_namespace} {fake_schema}"
    xml_path = tmp_path / "fake_schema.xml"

    x2d = XML2D()
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["topography_2"] = [
        {"type": "standard", "filelist": {"fmfile": [{"type": "tif", "value": "hi.tif"}]}},
    ]
    x2d.save(xml_path)

    fake_schema_xml = (
        xml_path.read_text()
        .replace("https://www.floodmodeller.com", fake_namespace)
        .replace("http://schema.floodmodeller.com/7.3/2d.xsd", fake_schema)
    )
    xml_path.write_text(fake_schema_xml)
    assert fake_namespace in xml_path.read_text()
    assert fake_schema_location in xml_path.read_text()

    x2d = XML2D(xml_path)
    assert x2d._xmltree.getroot().nsmap[None] == "https://www.floodmodeller.com"
    assert x2d._schema_version == "7.3"
    assert xml_path.read_text() == fake_schema_xml

    x2d.update()
    assert xml_path.read_text() != fake_schema_xml
    assert fake_namespace not in xml_path.read_text()
    assert fake_schema_location not in xml_path.read_text()

    x2d.update("7.2")
    assert x2d._schema_version == "7.2"
    assert fake_namespace not in xml_path.read_text()
    assert fake_schema_location not in xml_path.read_text()

    with pytest.raises(FloodModellerAPIError, match="XML Validation Error"):
        x2d.update("6.1")


def test_xml2d_nested_multivalue_update_keeps_topography_2_entries_separate():
    original_raster_path = "a.tif"
    original_shape_path = "b.shp"
    updated_raster_path = "c.tif"
    updated_shape_path = "d.shp"

    x2d = XML2D()
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["topography_2"] = [
        {
            "type": "standard",
            "filelist": {"fmfile": [{"type": "tif", "value": original_raster_path}]},
        },
        {
            "type": "standard",
            "filelist": {"fmfile": [{"type": "shp", "value": original_shape_path}]},
        },
    ]

    first_xml = x2d._write()
    assert original_raster_path in first_xml
    assert original_shape_path in first_xml

    x2d.domains[domain]["topography_2"][0]["filelist"]["fmfile"][0]["value"] = updated_raster_path
    x2d.domains[domain]["topography_2"][1]["filelist"]["fmfile"][0]["value"] = updated_shape_path
    updated_xml = x2d._write()

    assert updated_raster_path in updated_xml
    assert updated_shape_path in updated_xml
    assert updated_xml.count(updated_raster_path) == 1
    assert updated_xml.count(updated_shape_path) == 1
