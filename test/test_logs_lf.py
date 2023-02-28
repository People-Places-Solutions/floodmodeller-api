import pytest
from floodmodeller_api import XML2D, LF1, IEF
import os
from pathlib import Path
import pandas as pd 

@pytest.fixture
def test_workspace():
    return os.path.join(os.path.dirname(__file__), "test_data")

@pytest.fixture
def lf1_fp(test_workspace):
    return  os.path.join(test_workspace, "ex3.lf1")


def test_lf1_1(lf1_fp):
    """LF1: Check info dictionary"""
    lf1 = LF1(lf1_fp)
    assert lf1.info["version"] ==  "5.0.0.7752"
    assert lf1.info["max_system_volume"] ==  270549
    assert lf1.info["mass_balance_error"] == -0.03
    assert lf1.info["progress"] == 100

def test_lf1_2(lf1_fp):
    """LF1: Check report_progress()"""
    lf1 = LF1(lf1_fp)
    assert lf1.report_progress() == 100

def test_lf1_3(lf1_fp):
    """LF1: Check to_dataframe()"""
    lf1 = LF1(lf1_fp)
    df = lf1.to_dataframe()
    assert df.iloc[0,3] == 6
    assert df.iloc[-1,-1] == 21.06
    assert df.iloc[4,0] == -0.07

def test_lf1_4(lf1_fp, test_workspace):
    """LF1: Check IEF.get_lf1()"""
    lf1 = LF1(lf1_fp)

    ief_fp = os.path.join(test_workspace, "ex3.ief")
    ief = IEF(ief_fp)
    lf1_from_ief = ief.get_log()

    assert lf1._filepath == lf1_from_ief._filepath
    assert lf1.info == lf1_from_ief.info
    try:    
        pd.testing.assert_frame_equal(lf1.to_dataframe(), lf1_from_ief.to_dataframe())
    except:
        pytest.fail("Dataframes not equal")

# XML
@pytest.fixture 
def xml_fp(test_workspace):
    return os.path.join(test_workspace, "Domain1_Q.xml")

@pytest.fixture 
def data_before(xml_fp):
    return XML2D(xml_fp)._write()


def test_xml2d_1(xml_fp, data_before):
    """XML2D: Test str representation equal to xml file with no changes"""
    x2d = XML2D(xml_fp)
    assert x2d._write() == data_before

def test_xml2d_2(xml_fp, data_before):
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

def test_xml2d_3(test_workspace):
    """XML2D: Check all '.xml' files in folder by reading the _write() output into a
    new XML2D instance and checking it stays the same."""
    for xmlfile in Path(test_workspace).glob("*.xml"):
        x2d = XML2D(xmlfile)
        first_output = x2d._write()
        x2d.save("__temp.xml")
        second_output = XML2D("__temp.xml")._write()
        assert first_output == second_output
        os.remove("__temp.xml")