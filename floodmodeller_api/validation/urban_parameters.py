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

urban_parameter_options = {    
        "name": {
        "type": "string-length",
        "max_length": 15 # Match nominal lenght imposed during _write (units). No column width defined by Flood Modeller     
    },
        "elevation": {
        "type": "type-match",
        "options": (float, int)
    },
    "max_depth": {
         "type": "type-match",
        "options": (float, int)
    },
    "initial_depth": {
        "type": "type-match",
        "options": (float, int)
    },
    "surface_depth": {
        "type": "type-match",
        "options": (float, int)
    },
    "area_ponded": {
        "type": "type-match",
        "options": (float, int)
    },
    "format": {
         "type": "value-match",
        "options": ["INTENSITY", "VOLUME", "CUMULATIVE"]
    },
    "interval": {    # TODO: UPDATE TO CONSIDER - decimal hours or hours:minutes format (e.g., 0:15 for 15-minute readings). search for presence of ";" during _read maybe?
    #try turing to float else keep as string
        "type": "type-match",
        "options": (float, int, str) # TODO: add new a type of match called RegEx match for example "[0-9]:[0-9]"
    },
    "snow_catch_factor": {
        "type": "type-match",
        "options": (float, int)
    },
    "data_option": {
         "type": "value-match",
        "options": ["TIMESERIES", "FILE"]
    },
    "timeseries": {
        "type": "type-match",
        "options": (str)
    },
    "filename": {
        "type": "type-match",
        "options": (str)
    },
    "station": {
        "type": "type-match",
        "options": (str)
    },
    "units": {
         "type": "value-match",
        "options": ["IN", "MM"]
    }
}