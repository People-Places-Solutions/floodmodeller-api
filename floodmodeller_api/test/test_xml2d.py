from pathlib import Path

import pytest

from floodmodeller_api import XML2D
from floodmodeller_api.util import FloodModellerAPIError


@pytest.fixture()
def xml_fp(test_workspace):
    return Path(test_workspace, "Domain1_Q.xml")


@pytest.fixture()
def data_before(xml_fp):
    return XML2D(xml_fp)._write()


def test_xml2d_str_representation(xml_fp, data_before):
    """XML2D: Test str representation equal to xml file with no changes"""
    x2d = XML2D(xml_fp)
    assert x2d._write() == data_before


def test_xml2d_link_dtm_changes(xml_fp, data_before):
    """XML2D: Test changing and reverting link1d file and dtm makes no changes"""
    x2d = XML2D(xml_fp)
    prev_link = x2d.link1d[0]["link"]
    domain = next(iter(x2d.domains))
    prev_dtm = x2d.domains[domain]["topography"]

    x2d.link1d[0]["link"] = ["new_link"]
    x2d.domains[domain]["topography"] = ["new_dtm"]
    assert x2d._write() != data_before

    x2d.link1d[0]["link"] = prev_link
    x2d.domains[domain]["topography"] = prev_dtm
    assert x2d._write() == data_before


def test_xml2d_all_files(test_workspace, tmpdir):
    """XML2D: Check all '.xml' files in folder by reading the _write() output into a
    new XML2D instance and checking it stays the same."""
    for xmlfile in Path(test_workspace).glob("*.xml"):
        x2d = XML2D(xmlfile)
        first_output = x2d._write()
        new_path = Path(tmpdir) / "tmp.xml"
        x2d.save(new_path)
        second_x2d = XML2D(new_path)
        assert x2d == second_x2d
        second_output = second_x2d._write()
        assert first_output == second_output


# New tests being added for the add/remove functionalility
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


# validation/reordering tests


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


def test_xml2d_update_value(xml_fp, data_before):
    """XML2D: Test changing and reverting link1d file and dtm makes no changes"""
    x2d = XML2D(xml_fp)
    domain = next(iter(x2d.domains))
    x2d.domains[domain]["run_data"]["scheme"] = "TVD"

    assert x2d._write()
