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

from .lf1_helpers import (
    DateTime,
    Time,
    TimeDeltaHMS,
    TimeDeltaH,
    TimeDeltaS,
    Float,
    Int,
    FloatSplit,
    IntSplit,
    String,
    FloatMult,
)

data_to_extract = {
    # start
    "version": {"class": String, "prefix": "!!Info1 version1d", "stage" : "start"},
    "number_of_nodes": {"class": Int, "prefix": "!!output1  Number of 1D river nodes in model:", "stage" : "start"},
    "qtol": {"class": Float, "prefix": "!!Info1 qtol =", "stage" : "start"},
    "htol": {"class": Float, "prefix": "!!Info1 htol =", "stage" : "start"},
    "start_time": {"class": TimeDeltaH, "prefix": "!!Info1 Start Time:", "stage" : "start"},
    "end_time": {"class": TimeDeltaH, "prefix": "!!Info1 End Time:", "stage" : "start"},
    "ran_at": {"class": DateTime, "prefix": "!!Info1 Ran at", "stage" : "start", "code":"%H:%M:%S on %d/%m/%Y"},
    "max_itr": {"class": Int, "prefix": "!!Info1 maxitr =", "stage" : "start"},
    "min_itr": {"class": Int, "prefix": "!!Info1 minitr =", "stage" : "start"},
    # run
    "progress": {"class": IntSplit, "prefix": "!!Progress1", "stage" : "run", "split": "%"},
    "timestep": {"class": Float, "prefix": "!!Info1 Timestep", "stage" : "run", "defines_iters": True},
    "elapsed_time": {"class": TimeDeltaHMS, "prefix": "!!Info1 Elapsed", "stage" : "run"},
    "simulated_time": {"class": TimeDeltaHMS, "prefix": "!!Info1 Simulated", "stage" : "run"},
    "estimated_finish_time": {"class": Time, "prefix": "!!Info1 EFT:", "stage" : "run", "exclude": "calculating...", "code":"%H:%M:%S"},
    "estimated_time_remaining": {"class": TimeDeltaHMS, "prefix" : "!!Info1 ETR:", "exclude":"...", "stage" : "run" },
    "iterations": {"class": FloatMult, "prefix": "!!PlotI1", "stage" : "run"},
    "convergence": {"class": FloatMult, "prefix": "!!PlotC1", "stage" : "run"},
    "flow": {"class": FloatMult, "prefix": "!!PlotF1", "stage" : "run"},
    "mass_error": {"class": FloatMult, "prefix": "!!Info1 Mass %error =", "stage" : "run"},
    # end
    "simulation_time": {"class": TimeDeltaS, "prefix" : "!!output1 Simulation time elapsed (s):", "stage": "end" },
    "no_unconverged_timesteps": {"class": Int, "prefix" : "!!output1  Number of unconverged timesteps:", "stage" : "end" },
    "prop_simulation_unconverged": {"class": FloatSplit, "prefix" : "!!output1  Proportion of simulation unconverged:", "stage" : "end", "split": "%" },
    "mass_balance_interval": {"class": TimeDeltaS, "prefix" : "!!output1  Mass balance calculated every", "stage" : "end"},
    "initial_vol": {"class": FloatSplit, "prefix" : "!!output1  Initial volume:", "stage" : "end", "split": "m3" },
    "final_vol": {"class": FloatSplit, "prefix": "!!output1  Final volume:", "stage" : "end", "split": "m3"},
    "tot_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary inflow  :", "stage" : "end", "split": "m3"},
    "tot_boundary_outflow": {"class": FloatSplit, "prefix": "!!output1  Total boundary outflow :", "stage" : "end", "split": "m3"},
    "tot_lat_link_inflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link inflow :", "stage" : "end", "split": "m3"},
    "tot_lat_link_outflow": {"class": FloatSplit, "prefix": "!!output1  Total lat. link outflow:", "stage" : "end", "split": "m3"},
    "max_system_volume": {"class": FloatSplit, "prefix": "!!output1  Max. system volume:", "stage" : "end", "split": "m3"},
    "max_vol_increase": {"class": FloatSplit, "prefix": "!!output1  Max. |volume| increase:", "stage" : "end", "split": "m3"},
    "max_boundary_inflow": {"class": FloatSplit, "prefix": "!!output1  Max. boundary inflow:", "stage" : "end", "split": "m3"},
    "net_vol_increase": {"class": FloatSplit, "prefix": "!!output1  Net increase in volume:", "stage" : "end", "split": "m3"},
    "net_inflow_vol": {"class": FloatSplit, "prefix": "!!output1  Net inflow volume:", "stage" : "end", "split": "m3"},
    "vol_discrepancy": {"class": FloatSplit, "prefix": "!!output1  Volume discrepancy:", "stage" : "end", "split": "m3"},
    "mass_balance_error": {"class": FloatSplit, "prefix": "!!output1  Mass balance error:", "stage" : "end", "split": "%"},
    "mass_balance_error_2": {"class": FloatSplit, "prefix": "!!output1  Mass balance error [2]:", "stage" : "end", "split": "%"},
}