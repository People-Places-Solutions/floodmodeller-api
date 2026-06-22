from __future__ import annotations

import importlib.util
from io import StringIO
from pathlib import Path

from floodmodeller_api import DAT
from floodmodeller_api.units import CONDUIT

_STRUCTURE_LOG_PATH = (
    Path(__file__).resolve().parents[1]
    / "toolbox"
    / "model_build"
    / "structure_log"
    / "structure_log.py"
)
_SPEC = importlib.util.spec_from_file_location("structure_log_module", _STRUCTURE_LOG_PATH)
assert _SPEC is not None
assert _SPEC.loader is not None
_STRUCTURE_LOG_MODULE = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_STRUCTURE_LOG_MODULE)
StructureLogBuilder = _STRUCTURE_LOG_MODULE.StructureLogBuilder
serialise_keys = _STRUCTURE_LOG_MODULE.serialise_keys


def test_fullarch_structure_log_output():
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

    slb = StructureLogBuilder("", "")
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
                "height_springing": 0.0,
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
