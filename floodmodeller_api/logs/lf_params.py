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

# TODO: EFT, ETR, progress as individual values
# LF2 is not in sync

lf1_unsteady_data_to_extract = {
    # start
    "version": {"class": String, "prefix": "!!Info1 version1d", "stage": "start"},
    "number_of_1D_river_nodes": {"class": Float, "prefix": "!!output1  Number of 1D river nodes in model:", "stage": "start"},
    "qtol": {"class": Float, "prefix": "!!Info1 qtol =", "stage": "start"},
    "htol": {"class": Float, "prefix": "!!Info1 htol =", "stage": "start"},
    "start_time": {"class": TimeDeltaH, "prefix": "!!Info1 Start Time:", "stage": "start"},
    "end_time": {"class": TimeDeltaH, "prefix": "!!Info1 End Time:", "stage": "start"},
    "ran_at": {"class": DateTime, "prefix": "!!Info1 Ran at", "stage": "start", "code":"%H:%M:%S on %d/%m/%Y"},
    "max_itr": {"class": Float, "prefix": "!!Info1 maxitr =", "stage": "start"},
    "min_itr": {"class": Float, "prefix": "!!Info1 minitr =", "stage": "start"},
    # run
    "mass_error": {"class": TimeFloatMult, "prefix": "!!Info1 Mass %error =", "stage": "run", "names": ["ME_simulated", "ME_mass_error"], "before_index": True},
    "progress": {"class": FloatSplit, "prefix": "!!Progress1", "stage": "run", "split": "%", "before_index": True},
    "timestep": {"class": TimeDeltaS, "prefix": "!!Info1 Timestep", "stage": "run", "before_index": True},
    "elapsed": {"class": TimeDeltaHMS, "prefix": "!!Info1 Elapsed", "stage": "run", "index": True},  # one entry each iteration
    "simulated": {"class": TimeDeltaHMS, "prefix": "!!Info1 Simulated", "stage": "run"},
    "EFT": {"class": Time, "prefix": "!!Info1 EFT:", "stage": "run", "exclude": ["calculating..."], "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMS, "prefix": "!!Info1 ETR:", "exclude": ["..."], "stage": "run"},
    "iterations": {"class": TimeFloatMult, "prefix": "!!PlotI1", "stage": "run", "names": ["PlotI1_simulated", "PlotI1_iter", "PlotI1_log(dt)"]},
    "convergence": {"class": TimeFloatMult, "prefix": "!!PlotC1", "stage": "run", "names": ["PlotC1_simulated", "PlotC1_flow", "PlotC1_level"]},
    "flow": {"class": TimeFloatMult, "prefix": "!!PlotF1", "stage": "run", "names": ["PlotF1_simulated", "PlotF1_inflow", "PlotF1_outflow"]},
    # end
    "simulation_time_elapsed": {"class": TimeDeltaS, "prefix": "!!output1 Simulation time elapsed (s):", "stage": "end"},
    "number_of_unconverged_timesteps": {"class": Float, "prefix": "!!output1  Number of unconverged timesteps:", "stage": "end"},
    "proporion_of_simulation_unconverged": {"class": FloatSplit, "prefix": "!!output1  Proportion of simulation unconverged:", "stage": "end", "split": "%"},
    "mass_balance_calculated_every": {"class": TimeDeltaS, "prefix": "!!output1  Mass balance calculated every", "stage": "end"},
    "initial_volume": {"class": FloatSplit, "prefix": "!!output1  Initial volume:", "stage": "end", "split": "m3"},
    "final_volume": {"class": FloatSplit, "prefix": "!!output1  Final volume:", "stage": "end", "split": "m3"},
    "total_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary inflow :", "stage": "end", "split": "m3"},
    "total_boundary_outflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary outflow:", "stage": "end", "split": "m3"},
    "total_lat_link_inflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link inflow:", "stage": "end", "split": "m3"},
    "total_lat_link_outflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link outflow:", "stage": "end", "split": "m3"},
    "max_system_volume": {"class": FloatSplit, "prefix": "!!output1  Max. system volume:", "stage": "end", "split": "m3"},
    "max_volume_increase": {"class": FloatSplit, "prefix": "!!output1  Max. |volume| increase:", "stage": "end", "split": "m3"},
    "max_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Max. boundary inflow:", "stage": "end", "split": "m3"},
    "net_volume_increase": {"class": FloatSplit, "prefix": "!!output1  Net increase in volume:", "stage": "end", "split": "m3"},
    "net_inflow_volume": {"class": FloatSplit, "prefix": "!!output1  Net inflow volume:", "stage": "end", "split": "m3"},
    "volume_discrepancy": {"class": FloatSplit, "prefix": "!!output1  Volume discrepancy:", "stage": "end", "split": "m3"},
    "mass_balance_error": {"class": FloatSplit, "prefix": "!!output1  Mass balance error:", "stage": "end", "split": "%"},
    "mass_balance_error_2": {"class": FloatSplit, "prefix": "!!output1  Mass balance error [2]:", "stage": "end", "split": "%"},
}

lf1_steady_data_to_extract = {
    # start
    "version": {"class": String, "prefix": "!!Info1 version1d", "stage": "start"},
    "number_of_1D_river_nodes": {"class": Float, "prefix": "!!output1  Number of 1D river nodes in model:", "stage": "start"},
    # run
    "network_iteration": {"class": FloatSplit, "prefix": "!!output1  network iteration", "stage": "run", "split": "c", "index": True},  # one entry each iteration
    "largest_change_in_split_from_last_iteration": {"class": FloatSplit, "prefix": "!!output1  was", "stage": "run", "split": "%"},
    # end
    "successful_solution_in": {"class": FloatSplit, "prefix": "!!output1  successful solution in", "stage": "end", "split": "n"}
}

lf2_data_to_extract = {
    # start
    "version": {"class": StringSplit, "prefix": "!!output2 Using Flood Modeller 2D version:", "stage": "start", "split": ","},
    "simulation_initiated_at": {"class": DateTime, "prefix": "!!output2  Simulation initiated at", "stage": "start", "code": "%d/%m/%Y %H:%M:%S"},
    "input_control_file": {"class": String, "prefix": "!!output2 Using input control file:", "stage": "start"},
    "unit_system": {"class": String, "prefix": "!!output2 Unit system:", "stage": "start"},
    "number_of_2D_domains": {"class": Float, "prefix": "!!output2 Number of 2D domains:", "stage": "start"},
    "model_time_zero": {"class": DateTime, "prefix": "!!output2     Model time zero:", "stage": "start", "code": "%Y-%m-%d %H:%M:%S"},
    "model_start_time": {"class": DateTime, "prefix": "!!output2     Model start time:", "stage": "start", "code": "%Y-%m-%d %H:%M:%S"},
    "simulation_time": {"class": TimeDeltaH, "prefix": "!!output2     Simulation time:", "stage": "start"},
    "start_time": {"class": TimeDeltaH, "prefix": "!!Info2 Start Time:", "stage": "start"},
    "end_time": {"class": TimeDeltaH, "prefix": "!!Info2 End Time:", "stage": "start"},
    "solution_scheme": {"class": String, "prefix": "!!output2     Solution scheme:", "stage": "start"},
    "timestep": {"class": Float, "prefix": "!!output2     Model timestep             :", "stage": "start"},
    "wetting_drying_depth": {"class": Float, "prefix": "!!output2     Wetting/drying depth       :", "stage": "start"},
    "beta": {"class": Float, "prefix": "!!output2     Beta                       :", "stage": "start"},
    "number_of_iterations": {"class": Float, "prefix": "!!output2     Number of iterations       :", "stage": "start"},
    "calculation_depth": {"class": Float, "prefix": "!!output2     Calculation depth          :", "stage": "start"},
    "friction_depth": {"class": Float, "prefix": "!!output2     Friction depth             :", "stage": "start"},
    "eddy_viscosity": {"class": Float, "prefix": "!!output2     Eddy Viscosity             :", "stage": "start"},
    "velocity_head_threshold": {"class": Float, "prefix": "!!output2     Velocity head threshold    :", "stage": "start"},
    "rainfall_accumulation_depth": {"class": Float, "prefix": "!!output2     Rainfall accumulation depth:", "stage": "start"},
    "negative_depth_threshold": {"class": Float, "prefix": "!!output2     Negative depth threshold   :", "stage": "start"},
    "friction_depth_threshold": {"class": Float, "prefix": "!!output2     Friction depth threshold   :", "stage": "start"},
    "number_of_cells": {"class": Float, "prefix": "!!output2 Number of cells in model:", "stage": "start"},
    "data_prep_completed_in": {"class": TimeDeltaS, "prefix": "!!output2 Data prep completed in", "stage": "start"},
    # run
    "simulated": {"class": TimeDeltaHMS, "prefix": "!!Info2 Simulated", "stage": "run", "index": True}, # one entry each iteration
    "progress": {"class": FloatSplit, "prefix": "!!Progress2", "stage": "run", "split": "%"}, 
    "wet_cells": {"class": Float, "prefix": "!!PlotG2 Wet cells", "stage": "run"},
    "2D_boundary_inflow": {"class": Float, "prefix": "!!PlotG2 2D boundary inflow", "stage": "run"},
    "2D_boundary_outflow": {"class": Float, "prefix": "!!PlotG2 2D boundary outflow", "stage": "run"},
    "1D_link_flow": {"class": Float, "prefix": "!!PlotG2 1D link flow", "stage": "run"},
    "change_in_volume": {"class": Float, "prefix": "!!PlotG2 Change in volume", "stage": "run"},
    "volume": {"class": Float, "prefix": "!!PlotG2 Volume", "stage": "run"},
    "inst_mass_err": {"class": Float, "prefix": "!!PlotG2 Inst. mass err", "stage": "run"},
    "inst_mass_err": {"class": Float, "prefix": "!!PlotG2 Inst. mass err", "stage": "run"},
    "mass_error": {"class": Float, "prefix": "!!PlotG2 Mass error", "stage": "run"},
    "largest_cr": {"class": Float, "prefix": "!!PlotG2 Largest Cr", "stage": "run"},
    "elapsed": {"class": TimeDeltaHMS, "prefix": "!!Info2 Elapsed", "stage": "run"},  
    "EFT": {"class": Time, "prefix": "!!Info2 EFT:", "stage": "run", "code":"%H:%M:%S"},
    "ETR": {"class": TimeDeltaHMS, "prefix": "!!Info2 ETR:", "exclude": ["****:**:**", "****:00:**", "****:**:00"], "stage": "run"},
}