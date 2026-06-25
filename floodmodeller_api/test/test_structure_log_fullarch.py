from __future__ import annotations

import importlib
import sys
import types
from io import StringIO

from floodmodeller_api import DAT
from floodmodeller_api.units import CONDUIT


def test_fullarch_structure_log_output():
    sys.modules.setdefault("tkinter", types.ModuleType("tkinter"))
    structure_log_module = importlib.import_module(
        "floodmodeller_api.toolbox.model_build.structure_log.structure_log",
    )
    structure_log_builder = structure_log_module.StructureLogBuilder
    serialise_keys = structure_log_module.serialise_keys

    dat = DAT()
    conduit = CONDUIT(
        name="A2",
        subtype="FULLARCH",
        dist_to_next=0.0,
        equation="COLEBROOK-WHITE",
        elevation_invert=1.0,
        width=2.0,
        height_crown=0.8,
        friction_on_invert=0.003,
        friction_on_walls=0.003,
        friction_on_soffit=0.003,
    )
    dat.conduits[conduit.name] = conduit
    dat._all_units.append(conduit)

    slb = structure_log_builder("", "")
    slb.dat = dat
    slb.add_conduits()

    assert serialise_keys(slb.unit_store) == {
        "(A2,CONDUIT)": {
            "name": "A2",
            "type": "CONDUIT",
            "subtype": "FULLARCH",
            "comment": "",
            "conduit_data": {
                "length": 0.0,
                "total_length": 0.0,
            },
            "dimensions": {
                "width": 2.0,
                "height_crown": 0.8,
                "invert": 1.0,
            },
            "friction": {
                "friction_eq": "COLEBROOK-WHITE",
                "friction_set": [0.003],
                "all_friction": [0.003, 0.003, 0.003],
            },
        },
    }

    output = StringIO()
    slb.write_csv_output(output)
    assert output.getvalue() == (
        "Unit Name,Unit Type,Unit Subtype,Comment,Friction,Dimensions (m),Weir Coefficient,Culvert Inlet/Outlet Loss\r\n"
        'A2,CONDUIT,FULLARCH,,Colebrook-White: 0.003,"(Springing: 0.00, Crown: 0.80) x w: 2.00 x l: 0.00 (Total conduit length: 0.00)",,\r\n'
    )
