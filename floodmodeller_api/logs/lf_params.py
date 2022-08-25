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

from .lf_helpers import (
    DateTimeParser,
    TimeParser,
    TimeDeltaHMSParser,
    TimeDeltaHParser,
    TimeDeltaSParser,
    FloatParser,
    FloatSplitParser,
    StringParser,
    StringSplitParser,
    TimeFloatMultParser,
)

lf1_unsteady_data_to_extract = {
    # start
    "version": {"class": StringParser, "prefix": "!!Info1 version1d", "data_type": "last"},
    "number_of_1D_river_nodes": {"class": FloatParser, "prefix": "!!output1  Number of 1D river nodes in model:", "data_type": "last"},
    "qtol": {"class": FloatParser, "prefix": "!!Info1 qtol =", "data_type": "last"},
    "htol": {"class": FloatParser, "prefix": "!!Info1 htol =", "data_type": "last"},
    "start_time": {"class": TimeDeltaHParser, "prefix": "!!Info1 Start Time:", "data_type": "last"},
    "end_time": {"class": TimeDeltaHParser, "prefix": "!!Info1 End Time:", "data_type": "last"},
    "ran_at": {"class": DateTimeParser, "prefix": "!!Info1 Ran at", "data_type": "last", "code":"%H:%M:%S on %d/%m/%Y"},
    "max_itr": {"class": FloatParser, "prefix": "!!Info1 maxitr =", "data_type": "last"},
    "min_itr": {"class": FloatParser, "prefix": "!!Info1 minitr =", "data_type": "last"},
    # run
    "mass_error": {"class": TimeFloatMultParser, "prefix": "!!Info1 Mass %error =", "data_type": "all", "names": ["simulated", "mass_error"], "before_index": True},
    "progress": {"class": FloatSplitParser, "prefix": "!!Progress1", "data_type": "last", "split": "%", "before_index": True},
    "timestep": {"class": TimeDeltaSParser, "prefix": "!!Info1 Timestep", "data_type": "all", "before_index": True},
    "elapsed": {"class": TimeDeltaHMSParser, "prefix": "!!Info1 Elapsed", "data_type": "all", "before_index": True},
    "simulated": {"class": TimeDeltaHMSParser, "prefix": "!!Info1 Simulated", "data_type": "all", "is_index": True},
    "EFT": {"class": TimeParser, "prefix": "!!Info1 EFT:", "data_type": "last", "exclude": ["calculating..."], "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMSParser, "prefix": "!!Info1 ETR:", "exclude": ["..."], "data_type": "last"},
    "iterations": {"class": TimeFloatMultParser, "prefix": "!!PlotI1", "data_type": "all", "names": ["simulated", "iter", "log(dt)"]},
    "convergence": {"class": TimeFloatMultParser, "prefix": "!!PlotC1", "data_type": "all", "names": ["simulated", "flow", "level"]},
    "flow": {"class": TimeFloatMultParser, "prefix": "!!PlotF1", "data_type": "all", "names": ["simulated", "inflow", "outflow"]},
    # end
    "simulation_time_elapsed": {"class": TimeDeltaSParser, "prefix": "!!output1 Simulation time elapsed (s):", "data_type": "last"},
    "number_of_unconverged_timesteps": {"class": FloatParser, "prefix": "!!output1  Number of unconverged timesteps:", "data_type": "last"},
    "proporion_of_simulation_unconverged": {"class": FloatSplitParser, "prefix": "!!output1  Proportion of simulation unconverged:", "data_type": "last", "split": "%"},
    "mass_balance_calculated_every": {"class": TimeDeltaSParser, "prefix": "!!output1  Mass balance calculated every", "data_type": "last"},
    "initial_volume": {"class": FloatSplitParser, "prefix": "!!output1  Initial volume:", "data_type": "last", "split": "m3"},
    "final_volume": {"class": FloatSplitParser, "prefix": "!!output1  Final volume:", "data_type": "last", "split": "m3"},
    "total_boundary_inflow": {"class": FloatSplitParser, "prefix": "!!output1  Total boundary inflow :", "data_type": "last", "split": "m3"},
    "total_boundary_outflow": {"class": FloatSplitParser, "prefix": "!!output1  Total boundary outflow:", "data_type": "last", "split": "m3"},
    "total_lat_link_inflow": {"class": FloatSplitParser, "prefix": "!!output1  Total lat. link inflow:", "data_type": "last", "split": "m3"},
    "total_lat_link_outflow": {"class": FloatSplitParser, "prefix": "!!output1  Total lat. link outflow:", "data_type": "last", "split": "m3"},
    "max_system_volume": {"class": FloatSplitParser, "prefix": "!!output1  Max. system volume:", "data_type": "last", "split": "m3"},
    "max_volume_increase": {"class": FloatSplitParser, "prefix": "!!output1  Max. |volume| increase:", "data_type": "last", "split": "m3"},
    "max_boundary_inflow": {"class": FloatSplitParser, "prefix": "!!output1  Max. boundary inflow:", "data_type": "last", "split": "m3"},
    "net_volume_increase": {"class": FloatSplitParser, "prefix": "!!output1  Net increase in volume:", "data_type": "last", "split": "m3"},
    "net_inflow_volume": {"class": FloatSplitParser, "prefix": "!!output1  Net inflow volume:", "data_type": "last", "split": "m3"},
    "volume_discrepancy": {"class": FloatSplitParser, "prefix": "!!output1  Volume discrepancy:", "data_type": "last", "split": "m3"},
    "mass_balance_error": {"class": FloatSplitParser, "prefix": "!!output1  Mass balance error:", "data_type": "last", "split": "%"},
    "mass_balance_error_2": {"class": FloatSplitParser, "prefix": "!!output1  Mass balance error [2]:", "data_type": "last", "split": "%"},
}

lf1_steady_data_to_extract = {
    # start
    "version": {"class": StringParser, "prefix": "!!Info1 version1d", "data_type": "last"},
    "number_of_1D_river_nodes": {"class": FloatParser, "prefix": "!!output1  Number of 1D river nodes in model:", "data_type": "last"},
    # run
    "network_iteration": {"class": FloatSplitParser, "prefix": "!!output1  network iteration", "data_type": "all", "split": "c", "is_index": True},
    "largest_change_in_split_from_last_iteration": {"class": FloatSplitParser, "prefix": "!!output1  was", "data_type": "all", "split": "%"},
    # end
    "successful_solution_in": {"class": FloatSplitParser, "prefix": "!!output1  successful solution in", "data_type": "last", "split": "n"}
}

# TODO: LF2 is not in sync

lf2_data_to_extract = {
    # start
    "version": {"class": StringSplitParser, "prefix": "!!output2 Using Flood Modeller 2D version:", "data_type": "last", "split": ","},
    "simulation_initiated_at": {"class": DateTimeParser, "prefix": "!!output2  Simulation initiated at", "data_type": "last", "code": "%d/%m/%Y %H:%M:%S"},
    "input_control_file": {"class": StringParser, "prefix": "!!output2 Using input control file:", "data_type": "last"},
    "unit_system": {"class": StringParser, "prefix": "!!output2 Unit system:", "data_type": "last"},
    "number_of_2D_domains": {"class": FloatParser, "prefix": "!!output2 Number of 2D domains:", "data_type": "last"},
    "model_time_zero": {"class": DateTimeParser, "prefix": "!!output2     Model time zero:", "data_type": "last", "code": "%Y-%m-%d %H:%M:%S"},
    "model_start_time": {"class": DateTimeParser, "prefix": "!!output2     Model start time:", "data_type": "last", "code": "%Y-%m-%d %H:%M:%S"},
    "simulation_time": {"class": TimeDeltaHParser, "prefix": "!!output2     Simulation time:", "data_type": "last"},
    "start_time": {"class": TimeDeltaHParser, "prefix": "!!Info2 Start Time:", "data_type": "last"},
    "end_time": {"class": TimeDeltaHParser, "prefix": "!!Info2 End Time:", "data_type": "last"},
    "solution_scheme": {"class": StringParser, "prefix": "!!output2     Solution scheme:", "data_type": "last"},
    "timestep": {"class": FloatParser, "prefix": "!!output2     Model timestep             :", "data_type": "last"},
    "wetting_drying_depth": {"class": FloatParser, "prefix": "!!output2     Wetting/drying depth       :", "data_type": "last"},
    "beta": {"class": FloatParser, "prefix": "!!output2     Beta                       :", "data_type": "last"},
    "number_of_iterations": {"class": FloatParser, "prefix": "!!output2     Number of iterations       :", "data_type": "last"},
    "calculation_depth": {"class": FloatParser, "prefix": "!!output2     Calculation depth          :", "data_type": "last"},
    "friction_depth": {"class": FloatParser, "prefix": "!!output2     Friction depth             :", "data_type": "last"},
    "eddy_viscosity": {"class": FloatParser, "prefix": "!!output2     Eddy Viscosity             :", "data_type": "last"},
    "velocity_head_threshold": {"class": FloatParser, "prefix": "!!output2     Velocity head threshold    :", "data_type": "last"},
    "rainfall_accumulation_depth": {"class": FloatParser, "prefix": "!!output2     Rainfall accumulation depth:", "data_type": "last"},
    "negative_depth_threshold": {"class": FloatParser, "prefix": "!!output2     Negative depth threshold   :", "data_type": "last"},
    "friction_depth_threshold": {"class": FloatParser, "prefix": "!!output2     Friction depth threshold   :", "data_type": "last"},
    "number_of_cells": {"class": FloatParser, "prefix": "!!output2 Number of cells in model:", "data_type": "last"},
    "data_prep_completed_in": {"class": TimeDeltaSParser, "prefix": "!!output2 Data prep completed in", "data_type": "last"},
    # run
    "simulated": {"class": TimeDeltaHMSParser, "prefix": "!!Info2 Simulated", "data_type": "all", "is_index": True},
    "progress": {"class": FloatSplitParser, "prefix": "!!Progress2", "data_type": "last", "split": "%"}, 
    "wet_cells": {"class": FloatParser, "prefix": "!!PlotG2 Wet cells", "data_type": "all"},
    "2D_boundary_inflow": {"class": FloatParser, "prefix": "!!PlotG2 2D boundary inflow", "data_type": "all"},
    "2D_boundary_outflow": {"class": FloatParser, "prefix": "!!PlotG2 2D boundary outflow", "data_type": "all"},
    "1D_link_flow": {"class": FloatParser, "prefix": "!!PlotG2 1D link flow", "data_type": "all"},
    "change_in_volume": {"class": FloatParser, "prefix": "!!PlotG2 Change in volume", "data_type": "all"},
    "volume": {"class": FloatParser, "prefix": "!!PlotG2 Volume", "data_type": "all"},
    "inst_mass_err": {"class": FloatParser, "prefix": "!!PlotG2 Inst. mass err", "data_type": "all"},
    "inst_mass_err": {"class": FloatParser, "prefix": "!!PlotG2 Inst. mass err", "data_type": "all"},
    "mass_error": {"class": FloatParser, "prefix": "!!PlotG2 Mass error", "data_type": "all"},
    "largest_cr": {"class": FloatParser, "prefix": "!!PlotG2 Largest Cr", "data_type": "all"},
    "elapsed": {"class": TimeDeltaHMSParser, "prefix": "!!Info2 Elapsed", "data_type": "all"},  
    "EFT": {"class": TimeParser, "prefix": "!!Info2 EFT:", "data_type": "last", "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMSParser, "prefix": "!!Info2 ETR:", "exclude": ["****:**:**", "****:00:**", "****:**:00"], "data_type": "last"},
}