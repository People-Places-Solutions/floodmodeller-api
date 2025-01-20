"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

from typing import TypedDict


class UnitTypes(TypedDict):
    group: str
    has_subtype: bool


# Unit types and support
SUPPORTED_UNIT_TYPES: dict[str, UnitTypes] = {
    "QTBDY": {"group": "boundaries", "has_subtype": False},
    "HTBDY": {"group": "boundaries", "has_subtype": False},
    "QHBDY": {"group": "boundaries", "has_subtype": False},
    "REFHBDY": {"group": "boundaries", "has_subtype": False},
    "RIVER": {"group": "sections", "has_subtype": True},
    "BRIDGE": {"group": "structures", "has_subtype": True},
    "CONDUIT": {"group": "conduits", "has_subtype": True},
    "SLUICE": {"group": "structures", "has_subtype": True},
    "ORIFICE": {"group": "structures", "has_subtype": True},
    "SPILL": {"group": "structures", "has_subtype": False},
    "INITIAL CONDITIONS": {"group": "other", "has_subtype": False},
    "VARIABLES": {"group": "other", "has_subtype": False},
    "BLOCKAGE": {"group": "losses", "has_subtype": False},
    "CULVERT": {"group": "losses", "has_subtype": True},
    "RNWEIR": {"group": "structures", "has_subtype": False},
    "WEIR": {"group": "structures", "has_subtype": False},  # general weir
    "CRUMP": {"group": "structures", "has_subtype": False},
    "FLAT-V WEIR": {"group": "structures", "has_subtype": False},
    "INTERPOLATE": {"group": "sections", "has_subtype": False},
    "REPLICATE": {"group": "sections", "has_subtype": False},
    "OUTFALL": {"group": "structures", "has_subtype": True},
    "COMMENT": {"group": "comments", "has_subtype": False},
}

UNSUPPORTED_UNIT_TYPES = {
    "ABSTRACTION": {"has_subtype": False},
    "BERNOULLI": {"has_subtype": False},
    "BREACH": {"has_subtype": False},  # breach
    "FEHBDY": {"group": "boundaries", "has_subtype": False},  # RAINFALL RUNOFF METHOD boundary
    "FLOOD RELIEF": {"has_subtype": True},  # found in dat file
    "FLOOD RELIEF ARCH": {"group": "structures", "has_subtype": True},  # found in FM help
    "FLOODPLAIN": {"has_subtype": True},  # floodplain section culvert
    "FRQSIM": {"group": "boundaries", "has_subtype": False},  # flood FReQuency SIMulation
    "FSRBDY": {
        "group": "boundaries",
        "has_subtype": False,
    },  # FEH Method (FEH Rainfall Runoff Method)
    "FSSR16BDY": {"group": "boundaries", "has_subtype": False},  # FSSR16 Method
    "GATED WEIR": {"group": "structures", "has_subtype": False},  # gated weir
    "GAUGE": {"has_subtype": False},  # Gauge
    "GERRBDY": {"group": "boundaries", "has_subtype": False},  # gen rainfall runoff
    "INVERTED SYPHON": {"group": "structures", "has_subtype": True},  # invert syphon
    "JUNCTION": {"has_subtype": True},  # [connector]
    "LABYRINTH WEIR": {"group": "structures", "has_subtype": False},  # labyrinth weir
    "LATERAL": {"has_subtype": False},  # [connector]
    "LOSS": {"has_subtype": False},  # found in .dat
    "LOSSID": {"has_subtype": False},  # found in .dat
    "MANHOLE": {"has_subtype": False},  # Manhole [connector]
    "NCDBDY": {"group": "boundaries", "has_subtype": False},  # Normal/Critical Depth Boundary
    "NOTWEIR": {"group": "structures", "has_subtype": False},  # Notional Weir
    "OCPUMP": {"has_subtype": False},  # pump [junctions]
    "POND": {"has_subtype": True},  # Pond units, online pond etc [connector]
    "QH CONTROL": {"group": "structures", "has_subtype": False},  # Flow-head control weir
    "QRATING": {"group": "boundaries", "has_subtype": False},  # Rating Curves
    "REBDY": {"group": "boundaries", "has_subtype": False},  # Rainfall/Evaporation Boundary
    "REFH2BDY": {"group": "boundaries", "has_subtype": False},  # ReFH2 Method
    "RESERVOIR": {"has_subtype": False},  # reservoir unit [connector]
    "SCSBDY": {
        "group": "boundaries",
        "has_subtype": False,
    },  # US SCS Method now SS for rainfall/runoff
    "SCWEIR": {"group": "structures", "has_subtype": False},  # sharp crested weir
    "SYPHON": {"group": "structures", "has_subtype": False},  # syphon unit
    "TIDBDY": {"group": "boundaries", "has_subtype": False},  # tidal
}

ALL_UNIT_TYPES = set(SUPPORTED_UNIT_TYPES.keys()).union(UNSUPPORTED_UNIT_TYPES)
