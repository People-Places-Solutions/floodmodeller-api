"""
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

### UNIT CLASSES ###
from .boundaries import HTBDY, QHBDY, QTBDY, REFHBDY
from .iic import IIC
from .sections import RIVER
from .structures import BRIDGE, CONDUIT, SLUICE, ORIFICE, SPILL, BLOCKAGE, CULVERT, RNWEIR

### UNIT TYPES AND SUPPORT ###
SUPPORTED_UNIT_TYPES = {
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
    "BLOCKAGE": {"group": "losses", "has_subtype": False},
    "CULVERT": {"group": "losses", "has_subtype": True},
    "RNWEIR": {"group":"structures","has_subtype": False},
}

UNSUPPORTED_UNIT_TYPES = {
    "2DCELL",
    "ABSTRACTION",
    "AIR VESSEL",
    "BERNOULLI",
    "BREACH",
    "CHECK VALVE",
    "COMMENT",
    "CONPUMP",
    "CONVALVE",
    "CRUMP",
    "FEHBDY",
    "FLAT-V WEIR",
    "FLOOD RELIEF",
    "FLOODPLAIN",
    "FLOW CONTROL",
    "FRQSIM",
    "FSRBDY",
    "FSSR16BDY",
    "GATED WEIR",
    "GAUGE",
    "GERRBDY",
    "HBDY",
    "INTERPOLATE",
    "INVERTED SYPHON",
    "JUNCTION",
    "LABYRINTH WEIR",
    "LATERAL",
    "LDPUMP",
    "LOSS",
    "MANHOLE",
    "NCBDY",
    "NCDBDY",
    "NOTWEIR",
    "NOZZLE",
    "OCPUMP",
    "OUTFALL",
    "PIPE",
    "POND",
    "QH CONTROL",
    "QRATING",
    "REBDY",
    "REFH2BDY",
    "REPLICATE",
    "RESERVOIR",
    "SCSBDY",
    "SCWEIR",
    "SYPHON",
    "TIDAL",
    "TIDBDY",
    "WEIR",
}

ALL_UNIT_TYPES = set(SUPPORTED_UNIT_TYPES.keys()).union(UNSUPPORTED_UNIT_TYPES)
