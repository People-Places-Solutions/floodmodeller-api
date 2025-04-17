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

import re

from .lf_helpers import (
    DateTimeParser,
    FloatParser,
    FloatSplitParser,
    StringParser,
    StringSplitParser,
    TimeDeltaHMSParser,
    TimeDeltaHParser,
    TimeDeltaSParser,
    TimeFloatMultParser,
    TimeParser,
    TimeSplitParser,
)

lf1_unsteady_data_to_extract = {
    # start
    "version": {
        "class": StringParser,
        "prefix": "!!Info1 version1d",
        "data_type": "last",
    },
    "number_of_1D_river_nodes": {
        "class": FloatParser,
        "prefix": "!!output1  Number of 1D river nodes in model:",
        "data_type": "last",
    },
    "qtol": {
        "class": FloatParser,
        "prefix": "!!Info1 qtol =",
        "data_type": "last",
    },
    "htol": {
        "class": FloatParser,
        "prefix": "!!Info1 htol =",
        "data_type": "last",
    },
    "start_time": {
        "class": TimeDeltaHParser,
        "prefix": "!!Info1 Start Time:",
        "data_type": "last",
    },
    "end_time": {
        "class": TimeDeltaHParser,
        "prefix": "!!Info1 End Time:",
        "data_type": "last",
    },
    "ran_at": {
        "class": DateTimeParser,
        "prefix": "!!Info1 Ran at",
        "data_type": "last",
        "code": "%H:%M:%S on %d/%m/%Y",
    },
    "max_itr": {
        "class": FloatParser,
        "prefix": "!!Info1 maxitr =",
        "data_type": "last",
    },
    "min_itr": {
        "class": FloatParser,
        "prefix": "!!Info1 minitr =",
        "data_type": "last",
    },
    # run
    "mass_error": {
        "class": TimeFloatMultParser,
        "prefix": "!!Info1 Mass %error =",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "mass_error"],
        "before_index": True,
    },
    "progress": {
        "class": FloatSplitParser,
        "prefix": "!!Progress1",
        "data_type": "last",
        "split": "%",
        "before_index": True,
    },
    "timestep": {
        "class": TimeDeltaSParser,
        "prefix": "!!Info1 Timestep",
        "data_type": "all",
        "before_index": True,
    },
    "elapsed": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info1 Elapsed",
        "data_type": "all",
        "before_index": True,
    },
    "simulated": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info1 Simulated",
        "data_type": "all",
        "is_index": True,
    },
    "EFT": {
        "class": TimeParser,
        "prefix": "!!Info1 EFT:",
        "data_type": "last",
        "exclude": ["calculating..."],
        "code": "%H:%M:%S",
    },
    "ETR": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info1 ETR:",
        "exclude": ["..."],
        "data_type": "last",
    },
    "iterations": {
        "class": TimeFloatMultParser,
        "prefix": "!!PlotI1",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "iter", "log(dt)"],
    },
    "convergence": {
        "class": TimeFloatMultParser,
        "prefix": "!!PlotC1",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "convergence_flow", "convergence_level"],
    },
    "flow": {
        "class": TimeFloatMultParser,
        "prefix": "!!PlotF1",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "inflow", "outflow"],
    },
    "tuflow_vol": {
        "class": TimeFloatMultParser,
        "prefix": "!!HPC_Vol",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "tuflow_vol"],
        "before_index": True,
    },
    "tuflow_n_wet": {
        "class": TimeFloatMultParser,
        "prefix": "!!HPC_nWet",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "tuflow_n_wet"],
        "before_index": True,
    },
    "tuflow_dt": {
        "class": TimeFloatMultParser,
        "prefix": "!!HPC_dt",
        "data_type": "all",
        "subheaders": ["simulated_duplicate", "tuflow_dt"],
        "before_index": True,
    },
    # end
    "simulation_time_elapsed": {
        "class": TimeDeltaSParser,
        "prefix": "!!output1 Simulation time elapsed (s):",
        "data_type": "last",
    },
    "number_of_unconverged_timesteps": {
        "class": FloatParser,
        "prefix": "!!output1  Number of unconverged timesteps:",
        "data_type": "last",
    },
    "proportion_of_simulation_unconverged": {
        "class": FloatSplitParser,
        "prefix": "!!output1  Proportion of simulation unconverged:",
        "data_type": "last",
        "split": "%",
    },
    "mass_balance_calculated_every": {
        "class": TimeDeltaSParser,
        "prefix": "!!output1  Mass balance calculated every",
        "data_type": "last",
    },
    "initial_volume": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Initial volume\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "final_volume": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Final volume\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "total_boundary_inflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Total boundary inflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "total_boundary_outflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Total boundary outflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "total_lat_link_inflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Total lat. link inflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "total_lat_link_outflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Total lat. link outflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "max_system_volume": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Max. system volume\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "max_volume_increase": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Max. \|volume\| increase\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "max_boundary_inflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Max. boundary inflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "max_boundary_outflow": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Max. boundary outflow\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "net_volume_increase": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Net increase in volume\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "net_inflow_volume": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Net inflow volume\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "volume_discrepancy": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Volume discrepancy\s*:(.*)"),
        "data_type": "last",
        "split": "m3",
        "use_regex": True,
    },
    "mass_balance_error": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Mass balance error\s*:(.*)"),
        "data_type": "last",
        "split": "%",
        "use_regex": True,
    },
    "mass_balance_error_2": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output1\s+Mass balance error \[2\]\s*:(.*)"),
        "data_type": "last",
        "split": "%",
        "use_regex": True,
    },
    "tuflow_start_time": {
        "class": FloatParser,
        "prefix": "!!TUFLOW Start Time (h): ",
        "data_type": "last",
    },
    "tuflow_end_time": {
        "class": FloatParser,
        "prefix": "!!TUFLOW End Time (h): ",
        "data_type": "last",
    },
    "tuflow_cpu_time": {
        "class": TimeSplitParser,
        "prefix": "!!TUFLOW CPU Time: ",
        "data_type": "last",
        "split": "[",
        "code": "%H:%M:%S",
    },
    "tuflow_clock_time": {
        "class": TimeSplitParser,
        "prefix": "!!TUFLOW Clock Time: ",
        "data_type": "last",
        "split": "[",
        "code": "%H:%M:%S",
    },
    "tuflow_warnings_prior": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW WARNINGs prior to simulation:",
        "data_type": "last",
        "split": "[",
    },
    "tuflow_warnings_during": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW WARNINGs during simulation:",
        "data_type": "last",
        "split": "[",
    },
    "tuflow_checks_prior": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW CHECKs prior to simulation:",
        "data_type": "last",
        "split": "[",
    },
    "tuflow_checks_during": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW CHECKs during simulation:",
        "data_type": "last",
        "split": "[",
    },
    "tuflow_vol_start": {
        "class": FloatParser,
        "prefix": "!!TUFLOW Volume at Start (m3):",
        "data_type": "last",
    },
    "tuflow_vol_end": {
        "class": FloatParser,
        "prefix": "!!TUFLOW Volume at End (m3):",
        "data_type": "last",
    },
    "tuflow_vol_in": {
        "class": FloatParser,
        "prefix": "!!TUFLOW Total Volume In (m3):",
        "data_type": "last",
    },
    "tuflow_vol_out": {
        "class": FloatParser,
        "prefix": "!!TUFLOW Total Volume Out (m3):",
        "data_type": "last",
    },
    "tuflow_volume_error": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW Volume Error (m3):",
        "data_type": "last",
        "split": "or",
    },
    "tuflow_cumulative_me": {
        "class": FloatSplitParser,
        "prefix": "!!TUFLOW Final Cumulative ME:",
        "data_type": "last",
        "split": "%",
    },
}

lf1_steady_data_to_extract = {
    # start
    "version": {
        "class": StringParser,
        "prefix": "!!Info1 version1d",
        "data_type": "last",
    },
    "number_of_1D_river_nodes": {
        "class": FloatParser,
        "prefix": "!!output1  Number of 1D river nodes in model:",
        "data_type": "last",
    },
    # run
    "network_iteration": {
        "class": FloatSplitParser,
        "prefix": "!!output1  network iteration",
        "data_type": "all",
        "split": "c",
        "is_index": True,
    },
    "largest_change_in_split_from_last_iteration": {
        "class": FloatSplitParser,
        "prefix": "!!output1  was",
        "data_type": "all",
        "split": "%",
    },
    # end
    "successful_solution_in": {
        "class": FloatSplitParser,
        "prefix": "!!output1  successful solution in",
        "data_type": "last",
        "split": "n",
    },
}

lf2_data_to_extract = {
    # start
    "version": {
        "class": StringSplitParser,
        "prefix": "!!output2 Using Flood Modeller 2D Solver version:",
        "data_type": "last",
        "split": ",",
    },
    "simulation_initiated_at": {
        "class": DateTimeParser,
        "prefix": "!!output2  Simulation initiated at",
        "data_type": "last",
        "code": "%d/%m/%Y %H:%M:%S",
    },
    "input_control_file": {
        "class": StringParser,
        "prefix": "!!output2 Using input control file:",
        "data_type": "last",
    },
    "unit_system": {
        "class": StringParser,
        "prefix": "!!output2 Unit system:",
        "data_type": "last",
    },
    "number_of_2D_domains": {
        "class": FloatParser,
        "prefix": "!!output2 Number of 2D domains:",
        "data_type": "last",
    },
    "model_time_zero": {
        "class": DateTimeParser,
        "prefix": "!!output2     Model time zero:",
        "data_type": "last",
        "code": "%Y-%m-%d %H:%M:%S",
    },
    "model_start_time": {
        "class": DateTimeParser,
        "prefix": "!!output2     Model start time:",
        "data_type": "last",
        "code": "%Y-%m-%d %H:%M:%S",
    },
    "simulation_time": {
        "class": TimeDeltaHParser,
        "prefix": "!!output2     Simulation time:",
        "data_type": "last",
    },
    "start_time": {
        "class": TimeDeltaHParser,
        "prefix": "!!Info2 Start Time:",
        "data_type": "last",
    },
    "end_time": {
        "class": TimeDeltaHParser,
        "prefix": "!!Info2 End Time:",
        "data_type": "last",
    },
    "solution_scheme": {
        "class": StringParser,
        "prefix": "!!output2     Solution scheme:",
        "data_type": "last",
    },
    "timestep": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Model timestep\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "wetting_drying_depth": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Wetting/drying depth\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "beta": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Beta\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "number_of_iterations": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Number of iterations\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "calculation_depth": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Calculation depth\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "friction_depth": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Friction depth\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "eddy_viscosity": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Eddy Viscosity\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "velocity_head_threshold": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Velocity head threshold\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "rainfall_accumulation_depth": {
        "class": FloatParser,
        "prefix": "!!output2     Rainfall accumulation depth:",
        "data_type": "last",
    },
    "negative_depth_threshold": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Negative depth threshold\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "memory_use_estimate": {
        "class": FloatSplitParser,
        "prefix": "!!output2    Memory use estimate for this domain is",
        "data_type": "last",
        "split": "MB",
    },
    "friction_depth_threshold": {
        "class": FloatParser,
        "prefix": re.compile(r"^!!output2\s+Friction depth threshold\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
    },
    "number_of_cells": {
        "class": FloatParser,
        "prefix": "!!output2 Number of cells in model:",
        "data_type": "last",
    },
    "data_prep_completed_in": {
        "class": TimeDeltaSParser,
        "prefix": "!!output2 Data prep completed in",
        "data_type": "last",
    },
    "max_courant_number": {
        "class": FloatParser,
        "prefix": "!!output2 Maximum Courant number:",
        "data_type": "last",
    },
    "final_mass_error": {
        "class": FloatSplitParser,
        "prefix": re.compile(r"^!!output2\s+Final mass error\s*:(.*)"),
        "data_type": "last",
        "use_regex": True,
        "split": "%",
    },
    "combined_mass_error": {
        "class": FloatSplitParser,
        "prefix": "!!output2     Combined mass error (%):",
        "data_type": "last",
        "split": "%",
    },
    # run
    "simulated": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info2 Simulated",
        "data_type": "all",
        "is_index": True,
    },
    "progress": {
        "class": FloatSplitParser,
        "prefix": "!!Progress2",
        "data_type": "last",
        "split": "%",
    },
    "wet_cells": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Wet cells",
        "data_type": "all",
    },
    "boundary_inflow_2D": {
        "class": FloatParser,
        "prefix": "!!PlotG2 2D boundary inflow",
        "data_type": "all",
    },
    "boundary_outflow_2D": {
        "class": FloatParser,
        "prefix": "!!PlotG2 2D boundary outflow",
        "data_type": "all",
    },
    "link_flow_1D": {
        "class": FloatParser,
        "prefix": "!!PlotG2 1D link flow",
        "data_type": "all",
    },
    "change_in_volume": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Change in volume",
        "data_type": "all",
    },
    "volume": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Volume",
        "data_type": "all",
    },
    "inst_mass_err": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Inst. mass err",
        "data_type": "all",
    },
    "mass_error": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Mass error",
        "data_type": "all",
    },
    "largest_cr": {
        "class": FloatParser,
        "prefix": "!!PlotG2 Largest Cr",
        "data_type": "all",
    },
    "elapsed": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info2 Elapsed",
        "data_type": "all",
    },
    "EFT": {
        "class": TimeParser,
        "prefix": "!!Info2 EFT:",
        "data_type": "last",
        "code": "%H:%M:%S",
    },
    "ETR": {
        "class": TimeDeltaHMSParser,
        "prefix": "!!Info2 ETR:",
        "exclude": ["****:**:**", "****:00:**", "****:**:00"],
        "data_type": "last",
    },
}

error_2d_dict = {
    # format: Error code, 42 : Comment, "This has worked" ,
    100: "Successful completion",
    101: "Error at preprocessing stage",
    102: "Model unstable",
    103: "Model mass balance exceeds tolerance threshold",
    104: "Water reached cells at the edge of the 2D domain",
    105: "General error",
    106: "Error occurred while writing a file",
    107: "Error occurred while opening/writing to the log file",
    108: "Error occurred while opening a file",
    109: "Tried to run model with 1d and fast domains (not currently supported)",
    110: "All domains required the FAST engine",
    111: "1D engine failed",
    112: "2D timestep failed to converge",
    201: "SMS dat I/O failed",
    202: "Ctrl-C abort request",
    996: "Failed to initialise licence module",
    997: "Licence not taken/lost",
    998: "Failed to validate licence module",
}
