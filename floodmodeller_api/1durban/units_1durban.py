'''
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
'''

### UNIT CLASSES ###
#from .boundaries import HTBDY, QHBDY, QTBDY, REFHBDY
#from .iic import IIC
#from .sections import RIVER
#from .structures import BRIDGE, CONDUIT, SLUICE, ORIFICE, SPILL

### UNIT TYPES AND SUPPORT ###
SUPPORTED_UNIT_TYPES = {

    #'SPILL': {'group': 'structures', 'has_subtype': False},
    #'INITIAL CONDITIONS': {'group': 'other', 'has_subtype': False}
}

UNSUPPORTED_UNIT_TYPES = {
'[OPTIONS]',
'[REPORT]',
'[FILES]',
'[RAINGAGES]',
'[EVAPORATION]',
'[TEMPERATURE]',
'[ADJUSTMENTS]',
'[SUBCATCHMENTS]',
'[SUBAREAS]',
'[INFILTRATION]',
'[LID_CONTROLS]',
'[LID_USAGE]',
'[AQUIFERS]',
'[GROUNDWATER]',
'[GWF]',
'[SNOWPACKS]',
'[JUNCTIONS]',
'[OUTFALLS]',
'[DIVIDERS]',
'[STORAGE]',
'[CONDUITS]',
'[PUMPS]',
'[ORIFICES]',
'[WEIRS]',
'[OUTLETS]',
'[XSECTIONS]',
'[TRANSECTS]',
'[LOSSES]',
'[CONTROLS]',
'[POLLUTANTS]',
'[LANDUSES]',
'[COVERAGES]',
'[LOADINGS]',
'[BUILDUP]',
'[WASHOFF]',
'[TREATMENT]',
'[INFLOWS]',
'[DWF]',
'[RDII]',
'[HYDROGRAPHS]',
'[CURVES]',
'[TIMESERIES]',
'[PATTERNS]'
}

ALL_UNIT_TYPES = set(SUPPORTED_UNIT_TYPES.keys()).union(UNSUPPORTED_UNIT_TYPES)
