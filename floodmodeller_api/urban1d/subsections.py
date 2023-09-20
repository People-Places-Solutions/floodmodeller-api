"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from .conduits import CONDUITS

### UNIT CLASSES ###
from .junctions import JUNCTIONS
from .losses import LOSSES
from .outfalls import OUTFALLS
from .raingauges import RAINGAUGES
from .xsections import XSECTIONS

### UNIT TYPES AND SUPPORT ###
# TODO: Update functionality - SWMM manual indicates only first 4 characters of subsection heading are needed
SUPPORTED_SUBSECTIONS = {
    #'[TITLE]': {'attribute': 'Title', 'class': 'Title'}
    "[OPTIONS]": {"group": "general", "attribute": "Options", "class": "Options"},
    "[JUNCTIONS]": {"group": "units", "attribute": "_junctions", "class": JUNCTIONS},
    "[OUTFALLS]": {"group": "units", "attribute": "_outfalls", "class": OUTFALLS},
    "[RAINGAGES]": {"group": "units", "attribute": "_raingauges", "class": RAINGAUGES},
    "[CONDUITS]": {"group": "units", "attribute": "_conduits", "class": CONDUITS},
    "[LOSSES]": {"group": "units", "attribute": "_losses", "class": LOSSES},
    "[XSECTIONS]": {"group": "units", "attribute": "_xsections", "class": XSECTIONS}
    #'SPILL': {'group': 'structures', 'has_subtype': False},
    #'INITIAL CONDITIONS': {'group': 'other', 'has_subtype': False},
    #'[TITLE]' : {
    #   'attribute' : 'title',
    #    'class' : Title}
}

UNSUPPORTED_SUBSECTIONS = {
    "[TITLE]",
    "[REPORT]",
    "[FILES]",
    "[EVAPORATION]",
    "[TEMPERATURE]",
    "[ADJUSTMENTS]",
    "[SUBCATCHMENTS]",
    "[SUBAREAS]",
    "[INFILTRATION]",
    "[LID_CONTROLS]",  # first four characters not unique
    "[LID_USAGE]",
    "[AQUIFERS]",
    "[GROUNDWATER]",
    "[GWF]",
    "[SNOWPACKS]",
    "[DIVIDERS]",
    "[STORAGE]",
    "[PUMPS]",
    "[ORIFICES]",
    "[WEIRS]",
    "[OUTLETS]",
    "[XSECTIONS]",
    "[TRANSECTS]",
    "[CONTROLS]",
    "[POLLUTANTS]",
    "[LANDUSES]",
    "[COVERAGES]",
    "[LOADINGS]",
    "[BUILDUP]",
    "[WASHOFF]",
    "[TREATMENT]",
    "[INFLOWS]",
    "[DWF]",
    "[RDII]",
    "[HYDROGRAPHS]",
    "[CURVES]",
    "[TIMESERIES]",
    "[PATTERNS]",
    "[MAP]",  # This and the below are Map Data
    "[POLYGONS]",
    "[COORDINATES]",
    "[VERTICES]",
    "[LABELS]",
    "[SYMBOLS]",
    "[BACKDROP]",
    "[TAGS]",  # UNKNOWN - not in manual
}

ALL_SUBSECTIONS = set(SUPPORTED_SUBSECTIONS.keys()).union(UNSUPPORTED_SUBSECTIONS)
All_SUBSECTIONS_SHORTNAMES = set()
