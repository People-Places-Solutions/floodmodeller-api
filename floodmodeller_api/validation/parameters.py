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

parameter_options = {
    "name": {
        "type": "string-length",
        "max_length": 12,
    },
    "timeunit": {
        "type": "type-value-match",
        "options": (
            (float, int),
            [
                "SECONDS",
                "MINUTES",
                "HOURS",
                "DAYS",
                "WEEKS",
                "FORTNIGHTS",
                "MONTHS",
                "MONTH",
                "LUNAR MONTHS",
                "QUARTERS",
                "YEARS",
                "DECADES",
                "DATES",
                "MULTIPLIER",
            ],
        ),
    },
    "timeoffset": {
        "type": "type-match",
        "options": (float, int),
    },
    "timedatamultiplier": {
        "type": "type-match",
        "options": (float, int),
    },
    "flowmultiplier": {
        "type": "type-match",
        "options": (float, int),
    },
    "minflow": {
        "type": "type-match",
        "options": (float, int),
    },
    "extendmethod": {
        "type": "value-match",
        "options": ["EXTEND", "NOEXTEND", "REPEAT"],
    },
    "interpmethod": {
        "type": "value-match",
        "options": ["LINEAR", "SPLINE"],
    },
    "ds_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "us_reference_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "ds_reference_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "constriction_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "spill": {
        "type": "string-length",
        "max_length": 12,
    },
    "spill1": {
        "type": "string-length",
        "max_length": 12,
    },
    "spill2": {
        "type": "string-length",
        "max_length": 12,
    },
    "lat1": {
        "type": "string-length",
        "max_length": 12,
    },
    "lat2": {
        "type": "string-length",
        "max_length": 12,
    },
    "lat3": {
        "type": "string-length",
        "max_length": 12,
    },
    "lat4": {
        "type": "string-length",
        "max_length": 12,
    },
    "dist_to_next": {
        "type": "type-match",
        "options": (float, int),
    },
    "slope": {
        "type": "type-match",
        "options": (float, int),
    },
    "density": {
        "type": "type-match",
        "options": (float, int),
    },
    "remote_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "us_remote_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "ds_remote_label": {
        "type": "string-length",
        "max_length": 12,
    },
    "br_type": {
        "type": "value-match",
        "options": ["ARCH", "USBPR1978", "PIERLOSS"],
    },
    "calibration_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "skew": {
        "type": "type-match",
        "options": (float, int),
    },
    "bridge_width_dual": {
        "type": "type-match",
        "options": (float, int),
    },
    "bridge_dist_dual": {
        "type": "type-match",
        "options": (float, int),
    },
    "orifice_lower_transition_dist": {
        "type": "type-match",
        "options": (float, int),
    },
    "orifice_upper_transition_dist": {
        "type": "type-match",
        "options": (float, int),
    },
    "orifice_discharge_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "orifice_flow": {
        "type": "type-match",
        "options": (bool),
    },
    "specify_piers": {
        "type": "type-match",
        "options": (bool),
    },
    "abutment_type": {
        "type": "value-match",
        "options": ["3", "2", "1", 3, 2, 1],
    },
    "abutment_alignment": {
        "type": "value-match",
        "options": ["ALIGNED", "SKEW"],
    },
    "total_pier_width": {
        "type": "type-match",
        "options": (float, int),
    },
    "npiers": {
        "type": "type-match",
        "options": (int),
    },
    "pier_use_calibration_coeff": {
        "type": "type-match",
        "options": (bool),
    },
    "pier_calibration_coeff": {
        "type": "type-match",
        "options": (float, int),
    },
    "pier_shape": {
        "type": "value-match",
        "options": ["RECTANGLE", "CYLINDER", "SQUARE", "I-BEAM"],
    },
    # Pier_faces is an optional parameter
    "pier_faces": {
        "type": "value-match",
        "options": ["", "STREAMLINE", "SEMICIRCLE", "TRIANGLE", "DIAPHRAGM", "DIA"],
    },
    "soffit_shape": {
        "type": "value-match",
        "options": ["FLAT", "ARCH"],
    },
    "c_type": {
        "type": "value-match",
        "options": ["RECTANGULAR", "CIRCULAR"],
    },
    "friction_eq": {
        "type": "value-match",
        "options": ["MANNING", "COLEBROOK-WHITE"],
    },
    "invert": {
        "type": "type-match",
        "options": (float, int),
    },
    "diameter": {
        "type": "type-match",
        "options": (float, int),
    },
    "width": {
        "type": "type-match",
        "options": (float, int),
    },
    "height": {
        "type": "type-match",
        "options": (float, int),
    },
    "bottom_slot_dist": {
        "type": "type-match",
        "options": (float, int),
    },
    "bottom_slot_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "top_slot_dist": {
        "type": "type-match",
        "options": (float, int),
    },
    "top_slot_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "friction_below_axis": {
        "type": "type-match",
        "options": (float, int),
    },
    "friction_above_axis": {
        "type": "type-match",
        "options": (float, int),
    },
    "use_bottom_slot": {
        "type": "value-match",
        "options": ["ON", "OFF", "GLOBAL"],
    },
    "use_top_slot": {
        "type": "value-match",
        "options": ["ON", "OFF", "GLOBAL"],
    },
    "friction_on_invert": {
        "type": "type-match",
        "options": (float, int),
    },
    "friction_on_walls": {
        "type": "type-match",
        "options": (float, int),
    },
    "friction_on_soffit": {
        "type": "type-match",
        "options": (float, int),
    },
    "equation": {
        "type": "type-match",
        "options": (str),
    },
    "elevation_invert": {
        "type": "type-match",
        "options": (float, int),
    },
    "height_springing": {
        "type": "type-match",
        "options": (float, int),
    },
    "height_crown": {
        "type": "type-match",
        "options": (float, int),
    },
    "easting": {
        "type": "type-match",
        "options": (float, int),
    },
    "northing": {
        "type": "type-match",
        "options": (float, int),
    },
    "time_delay": {
        "type": "type-match",
        "options": (float, int),
    },
    "timestep": {
        "type": "type-match",
        "options": (float, int),
    },
    "scale_value": {
        "type": "type-match",
        "options": (float, int),
    },
    "sim_type": {
        "type": "value-match",
        "options": ["", "FULL", "PFONLY", "BFONLY"],
    },
    "scale_method": {
        "type": "value-match",
        "options": ["PEAKVALUE", "SCALEFACT"],
    },
    "boundary_type": {
        "type": "value-match",
        "options": ["HYDROGRAPH", "HYETOGRAPH"],
    },
    "scale_type": {
        "type": "value-match",
        "options": ["FULL", "RUNOFF"],
    },
    "allow_override": {
        "type": "value-match",
        "options": ["", "OVERRIDE", "NOOVERRIDE"],
    },
    "area": {
        "type": "type-match",
        "options": (float, int),
    },
    "urbext": {
        "type": "type-match",
        "options": (float),
    },
    "saar": {
        "type": "type-match",
        "options": (float, int),
    },
    "season": {
        "type": "value-match",
        "options": ["DEFAULT", "SUMMER", "WINTER"],
    },
    "calc_source": {
        "type": "value-match",
        "options": ["DLL", "REPORT"],
    },
    "storm_area": {
        "type": "type-match",
        "options": (float, int),
    },
    "storm_duration": {
        "type": "type-match",
        "options": (float, int),
    },
    "arf_method": {
        "type": "value-match",
        "options": ["USER", "DESIGN"],
    },
    "observed_rainfall_depth": {
        "type": "type-match",
        "options": (float, int),
    },
    "return_period": {
        "type": "type-match",
        "options": (float, int),
    },
    "arf": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_c": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_d1": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_d2": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_d3": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_e": {
        "type": "type-match",
        "options": (float, int),
    },
    "ddf_f": {
        "type": "type-match",
        "options": (float, int),
    },
    "weir_flow_coefficient": {
        "type": "value-range",
        "options": (0.4, 3.0),
    },
    "under_gate_flow": {
        "type": "value-range",
        "options": (0.4, 3.0),
    },
    "over_gate_flow": {
        "type": "value-range",
        "options": (0.4, 3.0),
    },
    "weir_breadth": {
        "type": "type-match",
        "options": (float, int),
    },
    "crest_elevation": {
        "type": "type-match",
        "options": (float, int),
    },
    "gate_height_or_chord": {
        "type": "type-match",
        "options": (float, int),
    },
    "weir_length": {
        "type": "type-match",
        "options": (float, int),
    },
    "us_weir_height": {
        "type": "type-match",
        "options": (float, int),
    },
    "ds_weir_height": {
        "type": "type-match",
        "options": (float, int),
    },
    "discharge_coefficeient": {
        "type": "type-match",
        "options": (float, int),
    },
    "exponent": {
        "type": "type-match",
        "options": (float, int),
    },
    "bias_factor": {
        "type": "type-match",
        "options": (float, int),
    },
    "modular_limits": {
        "type": "dict-match",
        "options": {
            "weir_flow": {
                "type": "value-range",
                "options": (0.0, 1.0),
            },
            "under_gate_flow": {
                "type": "value-range",
                "options": (0.0, 1.0),
            },
            "over_gate_flow": {
                "type": "value-range",
                "options": (0.0, 1.0),
            },
        },
    },
    "ngates": {
        "type": "type-match",
        "options": (int),
    },
    "rules": {
        "type": "list-dict-match",
        "options": {
            "name": {
                "type": "type-match",
                "options": (str),
            },
            "logic": {
                "type": "end-value-match",
                "options": ["END", "ENDIF"],
            },
        },
    },
    "varrules": {
        "type": "list-dict-match",
        "options": {
            "name": {
                "type": "type-match",
                "options": (str),
            },
            "logic": {
                "type": "end-value-match",
                "options": ["END", "ENDIF"],
            },
        },
    },
    "use_degrees": {
        "type": "type-match",
        "options": (bool),
    },
    "allow_free_flow_under": {
        "type": "type-match",
        "options": (bool),
    },
    "pivot_height": {
        "type": "type-match",
        "options": (float, int),
    },
    "gate_radius": {
        "type": "type-match",
        "options": (float, int),
    },
    "flapped": {
        "type": "type-match",
        "options": (bool),
    },
    "soffit": {
        "type": "type-match",
        "options": (float, int),
    },
    "bore_area": {
        "type": "type-match",
        "options": (float, int),
    },
    "upstream_sill": {
        "type": "type-match",
        "options": (float, int),
    },
    "downstream_sill": {
        "type": "type-match",
        "options": (float, int),
    },
    "weir_flow": {
        "type": "type-match",
        "options": (float, int),
    },
    "surcharged_flow": {
        "type": "type-match",
        "options": (float, int),
    },
    "modular_limit": {
        "type": "type-match",
        "options": (float, int),
    },
    "shape": {
        "type": "value-match",
        "options": ["RECTANGLE", "CIRCULAR"],
    },
    "weir_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "inlet_loss": {
        "type": "type-match",
        "options": (float, int),
    },
    "outlet_loss": {
        "type": "type-match",
        "options": (float, int),
    },
    "loss_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "headloss_type": {
        "type": "value-match",
        "options": ["TOTAL", "STATIC"],
    },
    "reverse_flow_mode": {
        "type": "value-match",
        "options": [0, "CALCULATED", "ZERO"],
    },
    "type_code": {
        "type": "value-match",
        "options": ["A", "B", "C"],
    },
    "k": {
        "type": "type-match",
        "options": (float, int),
    },
    "m": {
        "type": "type-match",
        "options": (float, int),
    },
    "c": {
        "type": "type-match",
        "options": (float, int),
    },
    "y": {
        "type": "type-match",
        "options": (float, int),
    },
    "ki": {
        "type": "type-match",
        "options": (float, int),
    },
    "screen_width": {
        "type": "type-match",
        "options": (float, int),
    },
    "bar_proportion": {
        "type": "value-range",
        "options": (0.0, 1.0),
    },
    "debris_proportion": {
        "type": "value-range",
        "options": (0.0, 1.0),
    },
    "velocity_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "weir_elevation": {
        "type": "type-match",
        "options": (float, int),
    },
    "upstream_crest_height": {
        "type": "type-match",
        "options": (float, int),
    },
    "downstream_crest_height": {
        "type": "type-match",
        "options": (float, int),
    },
    "coriolis_coefficient": {
        "type": "type-match",
        "options": (float, int),
    },
    "v_slope": {
        "type": "type-match",
        "options": (float, int),
    },
    "side_slope": {
        "type": "type-match",
        "options": (float, int),
    },
    "ds_face_slope": {
        "type": "value-match",
        "options": [2, 5],
    },
    "bank_top_elevation": {
        "type": "type-match",
        "options": (float, int),
    },
    "num_pairs": {
        "type": "type-match",
        "options": (float, int),
    },
    "runoff_factor": {
        "type": "type-match",
        "options": (float, int),
    },
    "bed_level_drop": {
        "type": "type-match",
        "options": (float, int),
    },
    "labels": {
        "type": "list-string-length",
        "max_length": 12,
    },
    "upstream_separation": {
        "type": "type-match",
        "options": (float, int),
    },
    "downstream_separation": {
        "type": "type-match",
        "options": (float, int),
    },
    "force_friction_flow": {
        "type": "type-match",
        "options": (bool),
    },
    "ds_area_constraint": {
        "type": "type-match",
        "options": (float, int),
    },
}
