import unittest
import sys
import os

# sys.path.insert(0, os.getcwd())
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import pandas as pd
from pathlib import Path
from floodmodeller_api import IEF, IED, DAT, ZZN, INP
from floodmodeller_api.units import QTBDY

test_workspace = os.path.join(os.path.dirname(__file__), "test_data")


class test_IEF(unittest.TestCase):
    """Basic benchmarking to test IEF class"""

    def setUp(self):
        """Used if there is repetative setup before each test"""
        self.ief_fp = os.path.join(test_workspace, "network.ief")
        with open(self.ief_fp, "r") as ief_file:
            self.data_before = ief_file.read()
        pass

    def test_1(self):
        """IEF: Test str representation equal to ief file with no changes"""
        ief = IEF(self.ief_fp)
        self.assertEqual(ief._write(), self.data_before)


class test_IED(unittest.TestCase):
    """Basic benchmarking to test IED class"""

    def setUp(self):
        """Used if there is repetative setup before each test"""
        self.ied_fp = os.path.join(test_workspace, "network.ied")
        with open(self.ied_fp, "r") as ied_file:
            self.data_before = ied_file.read()
        pass

    def test_1(self):
        """IED: Test str representation equal to ied file with no changes"""
        ied = IED(self.ied_fp)
        self.assertEqual(ied._write(), self.data_before)


class test_DAT(unittest.TestCase):
    """Basic benchmarking to test DAT class"""

    def setUp(self):
        """Used if there is repetative setup before each test"""
        self.dat_fp = os.path.join(test_workspace, "network.DAT")
        self.data_before = DAT(self.dat_fp)._write()

    def test_1(self):
        """DAT: Test str representation equal to dat file with no changes"""
        dat = DAT(self.dat_fp)
        self.assertEqual(dat._write(), self.data_before)

    def test_2(self):
        """DAT: Test changing and reverting section name and dist to next makes no changes"""
        dat = DAT(self.dat_fp)
        prev_name = dat.sections["CSRD10"].name
        prev_dist = dat.sections["CSRD10"].dist_to_next
        dat.sections["CSRD10"].name = "check"
        dat.sections["CSRD10"].dist_to_next = 0.0
        self.assertNotEqual(dat._write(), self.data_before)

        dat.sections["check"].name = prev_name
        dat.sections["check"].dist_to_next = prev_dist
        self.assertEqual(dat._write(), self.data_before)

    def test_3(self):
        """DAT: Test changing and reverting QTBDY hydrograph makes no changes"""
        dat = DAT(self.dat_fp)
        prev_qt = {}
        for name, unit in dat.boundaries.items():
            if type(unit) == QTBDY:
                prev_qt[name] = unit.data.copy()
                unit.data *= 2  # Multiply QT flow data by 2
        self.assertNotEqual(dat._write(), self.data_before)

        for name, qt in prev_qt.items():
            dat.boundaries[name].data = qt  # replace QT flow data with original
        self.assertEqual(dat._write(), self.data_before)

    def test_4(self):
        """DAT: Check all '.dat' files in folder by reading the _write() output into a new DAT instance and checking it stays the same."""
        for datfile in Path(test_workspace).glob("*.dat"):
            dat = DAT(datfile)
            first_output = dat._write()
            dat.save("__temp.dat")
            second_output = DAT("__temp.dat")._write()
            self.assertEqual(first_output, second_output)
            os.remove("__temp.dat")
        try:
            os.remove("__temp.gxy")
        except FileNotFoundError:
            pass


class test_INP(unittest.TestCase):
    """Basic benchmarking to test INP class"""

    def setUp(self):
        """Used if there is repetative setup before each test"""
        self.inp_fp = os.path.join(test_workspace, "network.inp")
        self.data_before = INP(self.inp_fp)._write()
        pass

    def test_1(self):
        """INP: Test str representation equal to inp file with no changes"""
        inp = INP(self.inp_fp)
        self.assertEqual(inp._write(), self.data_before)

    def test_2(self):
        """INP: Test changing and reverting section name and snow catch factor makes no changes"""
        inp = INP(self.inp_fp)
        prev_name = inp.raingauges["1"].name
        prev_scf = inp.raingauges["1"].snow_catch_factor
        inp.raingauges["1"].name = "check"
        inp.raingauges["1"].snow_catch_factor = 1.5
        self.assertNotEqual(inp._write(), self.data_before)

        inp.raingauges["check"].name = prev_name
        inp.raingauges["check"].snow_catch_factor = prev_scf

        self.assertEqual(inp._write(), self.data_before)

    def test_4(self):
        """INP: Check all '.inp' files in folder by reading the _write() output into a new INP instance and checking it stays the same."""
        for inpfile in Path(test_workspace).glob("*.inp"):
            inp = INP(inpfile)
            first_output = inp._write()
            inp.save("__temp.inp")
            second_output = INP("__temp.inp")._write()
            self.assertEqual(first_output, second_output)
            os.remove("__temp.inp")


class test_ZZN(unittest.TestCase):
    """Basic benchmarking to test ZZN class"""

    def setUp(self):
        """Used if there is repetative setup before each test"""
        self.zzn_fp = os.path.join(test_workspace, "network.zzn")
        self.tabCSV_output = pd.read_csv(
            os.path.join(test_workspace, "network_from_tabularCSV.csv")
        )
        self.tabCSV_output["Max State"] = self.tabCSV_output["Max State"].astype(
            "float64"
        )

    def test_1(self):
        """ZZN: Check loading zzn okay using dll"""
        zzn = ZZN(self.zzn_fp)
        zzn.export_to_csv(
            result_type="max",
            save_location=os.path.join(test_workspace, "test_output.csv"),
        )
        output = pd.read_csv(os.path.join(test_workspace, "test_output.csv"))
        output = round(output, 3)  # Round to 3dp

        pd.testing.assert_frame_equal(output, self.tabCSV_output, rtol=0.0001)


if __name__ == "__main__":
    unittest.main(verbosity=2)
