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
    DateTime,
    Time,
    TimeDeltaHMS,
    TimeDeltaH,
    TimeDeltaS,
    Float,
    FloatSplit,
    String,
    StringSplit,
    TimeFloatMult,
)

lf1_unsteady_data_to_extract = {
    # start
    "version": {"class": String, "prefix": "!!Info1 version1d", "type": "one"},
    "number_of_1D_river_nodes": {"class": Float, "prefix": "!!output1  Number of 1D river nodes in model:", "type": "one"},
    "qtol": {"class": Float, "prefix": "!!Info1 qtol =", "type": "one"},
    "htol": {"class": Float, "prefix": "!!Info1 htol =", "type": "one"},
    "start_time": {"class": TimeDeltaH, "prefix": "!!Info1 Start Time:", "type": "one"},
    "end_time": {"class": TimeDeltaH, "prefix": "!!Info1 End Time:", "type": "one"},
    "ran_at": {"class": DateTime, "prefix": "!!Info1 Ran at", "type": "one", "code":"%H:%M:%S on %d/%m/%Y"},
    "max_itr": {"class": Float, "prefix": "!!Info1 maxitr =", "type": "one"},
    "min_itr": {"class": Float, "prefix": "!!Info1 minitr =", "type": "one"},
    # run
    "mass_error": {"class": TimeFloatMult, "prefix": "!!Info1 Mass %error =", "type": "many", "names": ["ME_simulated", "ME_mass_error"], "before_index": True},
    "progress": {"class": FloatSplit, "prefix": "!!Progress1", "type": "one", "split": "%", "before_index": True},
    "timestep": {"class": TimeDeltaS, "prefix": "!!Info1 Timestep", "type": "many", "before_index": True},
    "elapsed": {"class": TimeDeltaHMS, "prefix": "!!Info1 Elapsed", "type": "many", "index": True},
    "simulated": {"class": TimeDeltaHMS, "prefix": "!!Info1 Simulated", "type": "many"},
    "EFT": {"class": Time, "prefix": "!!Info1 EFT:", "type": "one", "exclude": ["calculating..."], "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMS, "prefix": "!!Info1 ETR:", "exclude": ["..."], "type": "one"},
    "iterations": {"class": TimeFloatMult, "prefix": "!!PlotI1", "type": "many", "names": ["PlotI1_simulated", "PlotI1_iter", "PlotI1_log(dt)"]},
    "convergence": {"class": TimeFloatMult, "prefix": "!!PlotC1", "type": "many", "names": ["PlotC1_simulated", "PlotC1_flow", "PlotC1_level"]},
    "flow": {"class": TimeFloatMult, "prefix": "!!PlotF1", "type": "many", "names": ["PlotF1_simulated", "PlotF1_inflow", "PlotF1_outflow"]},
    # end
    "simulation_time_elapsed": {"class": TimeDeltaS, "prefix": "!!output1 Simulation time elapsed (s):", "type": "one"},
    "number_of_unconverged_timesteps": {"class": Float, "prefix": "!!output1  Number of unconverged timesteps:", "type": "one"},
    "proporion_of_simulation_unconverged": {"class": FloatSplit, "prefix": "!!output1  Proportion of simulation unconverged:", "type": "one", "split": "%"},
    "mass_balance_calculated_every": {"class": TimeDeltaS, "prefix": "!!output1  Mass balance calculated every", "type": "one"},
    "initial_volume": {"class": FloatSplit, "prefix": "!!output1  Initial volume:", "type": "one", "split": "m3"},
    "final_volume": {"class": FloatSplit, "prefix": "!!output1  Final volume:", "type": "one", "split": "m3"},
    "total_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary inflow :", "type": "one", "split": "m3"},
    "total_boundary_outflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary outflow:", "type": "one", "split": "m3"},
    "total_lat_link_inflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link inflow:", "type": "one", "split": "m3"},
    "total_lat_link_outflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link outflow:", "type": "one", "split": "m3"},
    "max_system_volume": {"class": FloatSplit, "prefix": "!!output1  Max. system volume:", "type": "one", "split": "m3"},
    "max_volume_increase": {"class": FloatSplit, "prefix": "!!output1  Max. |volume| increase:", "type": "one", "split": "m3"},
    "max_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Max. boundary inflow:", "type": "one", "split": "m3"},
    "net_volume_increase": {"class": FloatSplit, "prefix": "!!output1  Net increase in volume:", "type": "one", "split": "m3"},
    "net_inflow_volume": {"class": FloatSplit, "prefix": "!!output1  Net inflow volume:", "type": "one", "split": "m3"},
    "volume_discrepancy": {"class": FloatSplit, "prefix": "!!output1  Volume discrepancy:", "type": "one", "split": "m3"},
    "mass_balance_error": {"class": FloatSplit, "prefix": "!!output1  Mass balance error:", "type": "one", "split": "%"},
    "mass_balance_error_2": {"class": FloatSplit, "prefix": "!!output1  Mass balance error [2]:", "type": "one", "split": "%"},
}

lf1_steady_data_to_extract = {
    # start
    "version": {"class": String, "prefix": "!!Info1 version1d", "type": "one"},
    "number_of_1D_river_nodes": {"class": Float, "prefix": "!!output1  Number of 1D river nodes in model:", "type": "one"},
    # run
    "network_iteration": {"class": FloatSplit, "prefix": "!!output1  network iteration", "type": "many", "split": "c", "index": True},
    "largest_change_in_split_from_last_iteration": {"class": FloatSplit, "prefix": "!!output1  was", "type": "many", "split": "%"},
    # end
    "successful_solution_in": {"class": FloatSplit, "prefix": "!!output1  successful solution in", "type": "one", "split": "n"}
}

lf2_data_to_extract = {
    # start
    "version": {"class": StringSplit, "prefix": "!!output2 Using Flood Modeller 2D version:", "type": "one", "split": ","},
    "simulation_initiated_at": {"class": DateTime, "prefix": "!!output2  Simulation initiated at", "type": "one", "code": "%d/%m/%Y %H:%M:%S"},
    "input_control_file": {"class": String, "prefix": "!!output2 Using input control file:", "type": "one"},
    "unit_system": {"class": String, "prefix": "!!output2 Unit system:", "type": "one"},
    "number_of_2D_domains": {"class": Float, "prefix": "!!output2 Number of 2D domains:", "type": "one"},
    "model_time_zero": {"class": DateTime, "prefix": "!!output2     Model time zero:", "type": "one", "code": "%Y-%m-%d %H:%M:%S"},
    "model_start_time": {"class": DateTime, "prefix": "!!output2     Model start time:", "type": "one", "code": "%Y-%m-%d %H:%M:%S"},
    "simulation_time": {"class": TimeDeltaH, "prefix": "!!output2     Simulation time:", "type": "one"},
    "start_time": {"class": TimeDeltaH, "prefix": "!!Info2 Start Time:", "type": "one"},
    "end_time": {"class": TimeDeltaH, "prefix": "!!Info2 End Time:", "type": "one"},
    "solution_scheme": {"class": String, "prefix": "!!output2     Solution scheme:", "type": "one"},
    "timestep": {"class": Float, "prefix": "!!output2     Model timestep             :", "type": "one"},
    "wetting_drying_depth": {"class": Float, "prefix": "!!output2     Wetting/drying depth       :", "type": "one"},
    "beta": {"class": Float, "prefix": "!!output2     Beta                       :", "type": "one"},
    "number_of_iterations": {"class": Float, "prefix": "!!output2     Number of iterations       :", "type": "one"},
    "calculation_depth": {"class": Float, "prefix": "!!output2     Calculation depth          :", "type": "one"},
    "friction_depth": {"class": Float, "prefix": "!!output2     Friction depth             :", "type": "one"},
    "eddy_viscosity": {"class": Float, "prefix": "!!output2     Eddy Viscosity             :", "type": "one"},
    "velocity_head_threshold": {"class": Float, "prefix": "!!output2     Velocity head threshold    :", "type": "one"},
    "rainfall_accumulation_depth": {"class": Float, "prefix": "!!output2     Rainfall accumulation depth:", "type": "one"},
    "negative_depth_threshold": {"class": Float, "prefix": "!!output2     Negative depth threshold   :", "type": "one"},
    "friction_depth_threshold": {"class": Float, "prefix": "!!output2     Friction depth threshold   :", "type": "one"},
    "number_of_cells": {"class": Float, "prefix": "!!output2 Number of cells in model:", "type": "one"},
    "data_prep_completed_in": {"class": TimeDeltaS, "prefix": "!!output2 Data prep completed in", "type": "one"},
    # run
    "simulated": {"class": TimeDeltaHMS, "prefix": "!!Info2 Simulated", "type": "many", "index": True}, # one entry each iteration
    "progress": {"class": FloatSplit, "prefix": "!!Progress2", "type": "one", "split": "%"}, 
    "wet_cells": {"class": Float, "prefix": "!!PlotG2 Wet cells", "type": "many"},
    "2D_boundary_inflow": {"class": Float, "prefix": "!!PlotG2 2D boundary inflow", "type": "many"},
    "2D_boundary_outflow": {"class": Float, "prefix": "!!PlotG2 2D boundary outflow", "type": "many"},
    "1D_link_flow": {"class": Float, "prefix": "!!PlotG2 1D link flow", "type": "many"},
    "change_in_volume": {"class": Float, "prefix": "!!PlotG2 Change in volume", "type": "many"},
    "volume": {"class": Float, "prefix": "!!PlotG2 Volume", "type": "many"},
    "inst_mass_err": {"class": Float, "prefix": "!!PlotG2 Inst. mass err", "type": "many"},
    "inst_mass_err": {"class": Float, "prefix": "!!PlotG2 Inst. mass err", "type": "many"},
    "mass_error": {"class": Float, "prefix": "!!PlotG2 Mass error", "type": "many"},
    "largest_cr": {"class": Float, "prefix": "!!PlotG2 Largest Cr", "type": "many"},
    "elapsed": {"class": TimeDeltaHMS, "prefix": "!!Info2 Elapsed", "type": "many"},  
    "EFT": {"class": Time, "prefix": "!!Info2 EFT:", "type": "one", "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMS, "prefix": "!!Info2 ETR:", "exclude": ["****:**:**", "****:00:**", "****:**:00"], "type": "one"},
}