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
from .junctions import JUNCTIONS

# from .outfalls import OUTFALLS
from .raingauges import RAINGAUGES

"""class JUNCTIONS_SECTION(Urban1D):

    unit = 'JUNCTIONS' # NOTE: this is used to assigned class name via setter
    
    def _read(self, raw_subsection_data): #REVIEW: has more arguments that parent class method
        
        # Compile list to allow _write in correct order and capturing comments      


        for line in raw_subsection_data:
            if line.strip() != "" and line.upper() not in SUPPORTED_SUBSECTIONS and not line.startswith(';'):
                unit_name = line[0:17].strip(' ')
                #unit_params = units.helpers.split_n_char(line[17:],11)
                unit_data = units.helpers.split_n_char(line[17:],11) # REVIEW: why was i not able to pass a text string as unit_data? caused error on eval line
                
                
                #subsection_group = getattr(self, SUPPORTED_SUBSECTIONS[block['Subsection_Type']]['attribute']) #REVIEW: we adjusted this to 'attribute' from type.  Do we really want seperate lists for each unit type? Not the way it's done in DAT
                
                #subsection_group[unit_name] = SUPPORTED_SUBSECTIONS[block['Subsection_Type']]['class'](unit_data)
                
                #TODO: consider functionality that allows for 
            else: # This line is a title, header or divider row
                continue 
        
            a = JUNCTION(unit_data)
        
            pass"""

### UNIT TYPES AND SUPPORT ###
# TODO: Update functionality - SWMM manual indicates only first 4 characters of subsection heading are needed
SUPPORTED_SUBSECTIONS = {
    #'[TITLE]': {'attribute': 'Title', 'class': 'Title'}
    "[OPTIONS]": {"group": "general", "attribute": "Options", "class": "Options"},
    "[JUNCTIONS]": {"group": "units", "attribute": "_junctions", "class": JUNCTIONS},
    #'[OUTFALLS]': {'group': 'units', 'attribute': '_outfalls', 'class': OUTFALLS}
    "[RAINGAGES]": {"group": "units", "attribute": "_raingauges", "class": RAINGAUGES}
    #'SPILL': {'group': 'structures', 'has_subtype': False},
    #'INITIAL CONDITIONS': {'group': 'other', 'has_subtype': False},
    #'[TITLE]' : {
    #   'attribute' : 'title',
    #    'class' : Title}
}

UNSUPPORTED_SUBSECTIONS = {
    "[TITLE]",
    #'[OPTIONS]',
    "[REPORT]",
    "[FILES]",
    #'[RAINGAGES]',
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
    #'[JUNCTIONS]',
    "[OUTFALLS]",
    "[DIVIDERS]",
    "[STORAGE]",
    "[CONDUITS]",
    "[PUMPS]",
    "[ORIFICES]",
    "[WEIRS]",
    "[OUTLETS]",
    "[XSECTIONS]",
    "[TRANSECTS]",
    "[LOSSES]",
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
    "[MAP]",  # THis and the below are Map Data
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
