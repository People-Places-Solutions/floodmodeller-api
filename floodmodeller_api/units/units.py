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
from .sections import RIVER, INTERPOLATE, REPLICATE
from .structures import (
    BRIDGE, SLUICE, ORIFICE, SPILL, RNWEIR, CRUMP, FLAT_V_WEIR, OUTFALL
)
from .losses import BLOCKAGE, CULVERT
from .conduits import CONDUIT

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
    "CRUMP": {"group":"structures","has_subtype": False},
    "FLAT-V WEIR": {"group":"structures","has_subtype": False},
    #"RESERVOIR": {"group":"structures", "has_subtype": False}, # Needs further testing
    "INTERPOLATE": {"group":"sections", "has_subtype": False},
    "REPLICATE": {"group":"sections", "has_subtype": False},
    "OUTFALL": {"group": "structures", "has_subtype": True},
}

UNSUPPORTED_UNIT_TYPES = {
    #"2DCELL": {"group": ,"has_subtype": }, ### NOT FOUND!! in all UNITS 4_6.dat or Help manual, 
    "ABSTRACTION": {"has_subtype": False},
    #"AIR VESSEL": {"group": ,"has_subtype":}, ### NOT FOUND in .dat
    "BERNOULLI": {"has_subtype": False},
    "BREACH": {"has_subtype": False}, #breach
    #"CHECK VALVE": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    "COMMENT": {"group": 'other' ,"has_subtype": False},
    #"CONPUMP": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    #"CONVALVE": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    "FEHBDY": {"group": "boundaries" ,"has_subtype": False}, # RAINFALL RUNOFF METHOD boundary
    "FLOOD RELIEF": {"has_subtype": True}, # found in dat file 
    "FLOOD RELIEF ARCH": {"group": "structures", "has_subtype": True}, #found in FM help
    "FLOODPLAIN": {"has_subtype": True}, # floodplain section culvert
    #"FLOW CONTROL": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    "FRQSIM": {"group": 'boundaries',"has_subtype": False }, #flood FReQuency SIMulation
    "FSRBDY": {"group": 'boundaries',"has_subtype": False}, #FEH Method (FEH Rainfall Runoff Method)
    "FSSR16BDY": {"group": 'boundaries',"has_subtype": False}, #FSSR16 Method
    "GATED WEIR": {"group": 'structures' ,"has_subtype": False}, #gated weir
    "GAUGE": {"has_subtype": False}, # Gauge
    "GERRBDY": {"group": 'boundaries',"has_subtype": False}, #gen rainfall runoff
    #"HBDY": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    "INVERTED SYPHON": {"group": "structures" ,"has_subtype": True}, #invert syphon 
    "JUNCTION": {"has_subtype": True}, #[connector]
    "LABYRINTH WEIR": {"group": 'structures',"has_subtype": False}, #labyrinth weir
    "LATERAL": {"has_subtype": False}, #[connector]
    #"LDPUMP": {"group": ,"has_subtype": }, ### NOT FOUND in .dat
    "LOSS": {"has_subtype": False}, # found in .dat
    "LOSSID": {"has_subtype": False}, # found in .dat
    "MANHOLE": {"has_subtype": False}, #Manhole [connector]
    #"NCBDY": {"group": ,"has_subtype": }, ### NOT FOUND in .dat or help ###
    "NCDBDY": {"group": 'boundaries' ,"has_subtype": False}, #Normal/Critical Depth Boundary
    "NOTWEIR": {"group":'structures' ,"has_subtype": False}, #Notional Weir
    #"NOZZLE": {"group": ,"has_subtype": }, ### NOT FOUND in .dat or help ###
    "OCPUMP": {"has_subtype": False}, #pump [junctions]
    #"PIPE": {"group": ,"has_subtype": }, # [urban]
    "POND": {"has_subtype":True}, #Pond units, online pond etc [connector]
    "QH CONTROL": {"group": 'structures',"has_subtype": False}, #Flow-head control weir
    "QRATING": {"group": 'boundaries' ,"has_subtype": False}, #Rating Curves
    "REBDY": {"group": 'boundaries',"has_subtype": False}, #Rainfall/Evaporation Boundary
    "REFH2BDY": {"group": 'boundaries' ,"has_subtype": False}, #ReFH2 Method
    "RESERVOIR": {"has_subtype": False}, #reservoir unit [connector]
    "SCSBDY": {"group": 'boundaries',"has_subtype": False }, # US SCS Method now SS for rainfall/runoff
    "SCWEIR": {"group" : "structures" ,"has_subtype": False}, #sharp crested weir
    "SYPHON": {"group": "structures","has_subtype": False}, #syphon unit 
    #"TIDAL": {"has_subtype": },
    "TIDBDY": {"group": "boundaries","has_subtype": False}, #tidal 
    "WEIR":{"group": "structures","has_subtype": False}, #general weir 
}

ALL_UNIT_TYPES = set(SUPPORTED_UNIT_TYPES.keys()).union(UNSUPPORTED_UNIT_TYPES)
