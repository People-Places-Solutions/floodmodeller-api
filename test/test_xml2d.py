import pytest
from floodmodeller_api import XML2D
import os
from pathlib import Path

@pytest.fixture 
def xml_fp(test_workspace):
    return os.path.join(test_workspace, "Domain1_Q.xml")

@pytest.fixture 
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
    domain = list(x2d.domains)[0]
    prev_dtm = x2d.domains[domain]["topography"]

    x2d.link1d[0]["link"] = "new_link"
    x2d.domains[domain]["topography"] = "new_dtm"
    assert x2d._write() != data_before

    x2d.link1d[0]["link"] = prev_link
    x2d.domains[domain]["topography"] = prev_dtm
    assert x2d._write() == data_before

def test_xml2d_all_files(test_workspace):
    """XML2D: Check all '.xml' files in folder by reading the _write() output into a
    new XML2D instance and checking it stays the same."""
    for xmlfile in Path(test_workspace).glob("*.xml"):
        x2d = XML2D(xmlfile)
        first_output = x2d._write()
        x2d.save("__temp.xml")
        second_x2d = XML2D("__temp.xml")
        assert x2d == second_x2d
        second_output = second_x2d._write()
        assert first_output == second_output
        os.remove("__temp.xml")