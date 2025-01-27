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

urban_parameter_options = {
    "name": {
        "type": "string-length",
        "max_length": 15,  # Match nominal lenght imposed during _write (units). No column width defined by Flood Modeller     ,
    },
    "elevation": {
        "type": "type-match",
        "options": (float, int),
    },
    "max_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "initial_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "surface_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "area_ponded": {
        "type": "type-match",
        "options": (float, int),
    },
    "format": {
        "type": "value-match",
        "options": ["INTENSITY", "VOLUME", "CUMULATIVE"],
    },
    "interval": {
        # try turing to float else keep as string
        "type": "type-match",
        "options": (float, int, str),
    },
    "snow_catch_factor": {
        "type": "type-match",
        "options": (float, int),
    },
    "data_option": {
        "type": "value-match",
        "options": ["TIMESERIES", "FILE"],
    },
    "timeseries": {
        "type": "type-match",
        "options": (str),
    },
    "filename": {
        "type": "type-match",
        "options": (str),
    },
    "station": {
        "type": "type-match",
        "options": (str),
    },
    "units": {
        "type": "value-match",
        "options": ["IN", "MM"],
    },
    "type": {  # outfall type
        "type": "value-match",
        "options": ["FREE", "NORMAL", "FIXED", "TIDAL", "TIMESERIES"],
    },
    "stage": {
        "type": "type-match",
        "options": (float, int),
    },
    "tcurve": {  # tidal curve name
        "type": "type-match",
        "options": (str),
    },
    "tseries": {  # tidal curve name
        "type": "type-match",
        "options": (str),
    },
    "gated": {  # outfall type
        "type": "value-match",
        "options": [None, "", "YES", "NO"],
    },
    "routeto": {  # outfall type
        "type": "type-match",
        "options": (str),
    },
    "node1": {
        "type": "type-match",
        "options": (str),
    },
    "node2": {
        "type": "type-match",
        "options": (str),
    },
    "length": {
        "type": "type-match",
        "options": (float, int),
    },
    "n": {
        "type": "type-match",
        "options": (float, int),
    },
    "z1": {
        "type": "type-match",
        "options": (float, int),
    },
    "z2": {
        "type": "type-match",
        "options": (float, int),
    },
    "q0": {
        "type": "type-match",
        "options": (type(None), float, int),
    },
    "qmax": {
        "type": "type-match",
        "options": (type(None), float, int),
    },
    "kentry": {
        "type": "type-match",
        "options": (float, int),
    },
    "kexit": {
        "type": "type-match",
        "options": (float, int),
    },
    "kavg": {
        "type": "type-match",
        "options": (float, int),
    },
    "flap": {  # outfall type
        "type": "value-match",
        "options": [None, "YES", "NO"],
    },
    "seepage": {  # outfall type
        "type": "type-match",
        "options": (type(None), float, int),
    },
    "shape": {  # xsection shape
        "type": "value-match",
        "options": [
            "CIRCULAR",
            "FORCE_MAIN",
            "FILLED_CIRCULAR2",
            "RECT_CLOSED",
            "RECT_OPEN",
            "TRAPEZOIDAL",
            "TRIANGULAR",
            "HORIZ_ELLIPSE",
            "VERT_ELLIPSE",
            "ARCH",
            "PARABOLIC",
            "POWER",
            "RECT_TRIANGULAR",
            "RECT_ROUND",
            "MODBASKETHANDLE",
            "EGG",
            "HORSESHOE",
            "GOTHIC",
            "CATENARY",
            "SEMIELLIPTICAL",
            "BASKETHANDLE",
            "SEMICIRCULAR",
            "CUSTOM",
            "IRREGULAR",
        ],
    },
    "geom1": {
        "type": "type-match",
        "options": (type(None), float, int, str),
    },
    "geom2": {
        "type": "type-match",
        "options": (type(None), float, int, str),
    },
    "geom3": {
        "type": "type-match",
        "options": (type(None), float, int, str),
    },
    "geom4": {
        "type": "type-match",
        "options": (type(None), float, int, str),
    },
    "barrels": {
        "type": "type-match",
        "options": (type(None), int),
    },
    "culvert": {
        "type": "type-match",
        "options": (type(None), int, str),
    },
    "curve": {  # curve name
        "type": "type-match",
        "options": (str),
    },
    "tsec": {
        "type": "type-match",
        "options": (str),
    },
    "options": {
        "type": "dict-match",
        "options": {
            "flow_units": {
                "type": "value-match",
                "options": [None, "CFS", "GPM", "MGD", "CMS", "LPS", "MLD"],
            },
            "infiltration": {
                "type": "value-match",
                "options": [
                    None,
                    "HORTON",
                    "MODIFIED_HORTON",
                    "GREEN_AMPT",
                    "MODIFIED_GREEN_AMPT",
                    "CURVE_NUMBER",
                ],
            },
            "flow_routing": {
                "type": "value-match",
                "options": [None, "STEADY", "KINWAVE", "DYNWAVE"],
            },
            "link_offsets": {
                "type": "value-match",
                "options": [None, "DEPTH", "ELEVATION"],
            },
            "force_main_equation": {
                "type": "value-match",
                "options": [None, "H-W", "D-W"],
            },
            "ignore_rainfall": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "ignore_snowmelt": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "ignore_groundwater": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "ignore_rdii": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "ignore_routing": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "ignore_quality": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "allow_ponding": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "skip_steady_state": {
                "type": "value-match",
                "options": [None, "YES", "NO"],
            },
            "sys_flow_tol": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "lat_flow_tol": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "start_date": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "start_time": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "end_date": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "end_time": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "report_start_date": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "report_start_time": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "sweep_start": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "sweep_end": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "dry_days": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "report_step": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "wet_step": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "dry_step": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "routing_step": {
                "type": "type-match",
                "options": (type(None), str),
            },
            "lengthening_step": {  # in INT format
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "variable_step": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "minimum_step": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "inertial_damping": {
                "type": "value-match",
                "options": [None, "NONE", "PARTIAL", "FULL"],
            },
            "normal_flow_limited": {
                "type": "value-match",
                "options": [None, "SLOPE", "FROUDE", "BOTH"],
            },
            "min_surfarea": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "min_slope": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "max_trials": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "head_tolerance": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "threads": {
                "type": "type-match",
                "options": (type(None), float, int),
            },
            "tempdir": {
                "type": "type-match",
                "options": (type(None), str),
            },
            # Rule step in software but not manual
            "rule_step": {
                "type": "type-match",
                "options": (type(None), str),
            },
        },
    },
}
