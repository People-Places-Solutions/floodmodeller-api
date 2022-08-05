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

from concurrent.futures import process
from pathlib import Path
from typing import Optional, Union
from unicodedata import category

import pandas as pd
import datetime as dt

from ._base import FMFile

class LF1(FMFile):
    """Reads and processes Flood Modeller 1D log file '.lf1'

    Args:
        lf1_filepath (str): Full filepath to model lf1 file

    Output:
        Initiates 'LF1' class object
    """

    _filetype: str = "LF1"
    _suffix: str = ".lf1"

    def __init__(self, lf1_filepath: Optional[Union[str, Path]]):
        try:
            self._filepath = lf1_filepath
            FMFile.__init__(self)

            # to keep track of file during simulation
            self._lines_read = 0 # number of lines that have been read so far
            self._sim_stage = 0 # 1 = start, 2 = running, 3 = end

            # to process and hold data according to type         
            self.version = String("!!Info1 version1d")
            self.number_of_nodes = Int("!!output1  Number of 1D river nodes in model:")

            self.progress = IntSplit("!!Progress1", split = "%")
            self.timestep = Float("!!Info1 Timestep")
            self.elapsed_time = TimeDelta("!!Info1 Elapsed")
            self.simulated_time = TimeDelta("!!Info1 Simulated")
            self.estimated_finish_time = Time("!!Info1 EFT:")
            self.estimated_time_remaining = TimeDelta("!!Info1 ETR:")
            self.iterations = FloatMult("!!PlotI1")
            self.convergence = FloatMult("!!PlotC1")
            self.flow = FloatMult("!!PlotF1")
            self.mass_error = FloatMult("!!Info1 Mass %error =")
            
            self.no_unconverged_timesteps = Int("!!output1  Number of unconverged timesteps:")
            self.prop_simulation_unconverged = FloatSplit("!!output1  Proportion of simulation unconverged:", split = "%")
            self.initial_vol = FloatSplit("!!output1  Initial volume:", split = "m3")
            self.final_vol = FloatSplit("!!output1  Final volume:", split = "m3")
            self.tot_boundary_inflow = FloatSplit("!!output1  Total boundary inflow  :", split = "m3")
            self.tot_boundary_outflow = FloatSplit("!!output1  Total boundary outflow :", split = "m3")
            self.tot_lat_link_inflow = FloatSplit("!!output1  Total lat. link inflow :", split = "m3")
            self.tot_lat_link_outflow = FloatSplit("!!output1  Total lat. link outflow:", split = "m3")
            self.max_system_volume = FloatSplit("!!output1  Max. system volume:", split = "m3")
            self.max_vol_increase = FloatSplit("!!output1  Max. |volume| increase:", split = "m3")
            self.max_boundary_inflow = FloatSplit("!!output1  Max. boundary inflow:", split = "m3")
            self.net_vol_increase = FloatSplit("!!output1  Net increase in volume:", split = "m3")
            self.net_inflow_vol = FloatSplit("!!output1  Net inflow volume:", split = "m3")
            self.vol_discrepancy = FloatSplit("!!output1  Volume discrepancy:", split = "m3")
            self.mass_balance_error = FloatSplit("!!output1  Mass balance error:", split = "%")
            self.mass_balance_error_2 = FloatSplit("!!output1  Mass balance error [2]:", split = "%")

            self._data_to_extract = [
                self.version,
                self.number_of_nodes,
                #
                self.progress,
                self.timestep,
                self.elapsed_time,
                self.simulated_time,
                self.estimated_finish_time,
                self.estimated_time_remaining,
                self.iterations,
                self.convergence,
                self.flow,
                self.mass_error,
                #
                self.no_unconverged_timesteps,
                self.prop_simulation_unconverged,
                self.initial_vol,
                self.final_vol,
                self.tot_boundary_inflow,
                self.tot_boundary_outflow,
                self.tot_lat_link_inflow,
                self.tot_lat_link_outflow,
                self.max_system_volume,
                self.max_vol_increase,
                self.max_boundary_inflow,
                self.net_vol_increase,
                self.net_inflow_vol,
                self.vol_discrepancy,
                self.mass_balance_error,
                self.mass_balance_error_2
            ]
            
            self._read()

        except Exception as e:
            self._handle_exception(e, when="read")

    def _read(self, force_reread = False):
        # Read LF1 file
        with open(self._filepath, "r") as lf1_file:
            self._raw_data = [line.rstrip("\n") for line in lf1_file.readlines()]

        # Force rereading from start of file
        if force_reread == True:
            self._lines_read = 0

        # Process file
        self._process_lines()

    def _process_lines(self):
        """Sorts and processes raw data into lists for each prefix"""

        self._print_lines_read()

        # loop through lines that haven't already been read
        raw_lines = self._raw_data[self._lines_read:]
        for raw_line in raw_lines:

            self._update_sim_stage(raw_line)

            # loop through line types
            for line_type in self._data_to_extract:

                # lines which start with prefix
                if raw_line.startswith(line_type._prefix):

                    # add everything after prefix to list
                    end_of_line = raw_line.split(line_type._prefix)[1].lstrip()
                    line_type._store_line(end_of_line)
            
            # update counter
            self._lines_read += 1

        self._print_lines_read()

    def _print_lines_read(self):
        """Prints the number of lines that have been read so far"""

        print("Lines read: " + str(self._lines_read))

    def _update_sim_stage(self, raw_line):
        """Update what stage of simulation we are in"""

        # TODO: check classification is robust

        # start
        if self._sim_stage == 0 and raw_line == "!!output1":
            self._sim_stage = 1

        # running
        elif self._sim_stage == 1 and raw_line == "!!Progress1   0%":
            self._sim_stage = 2

        # end
        elif self._sim_stage == 2 and raw_line == "!!output1":
            self._sim_stage = 3

        elif self._sim_stage >= 4:
            raise ValueError(f"Unexpected simulation stage {self._sim_stage}")

class LineType:

    def __init__(self, prefix):
        self._prefix = prefix
        self._init_value()

    def __str__(self):
        return str(self.value)

    def _init_value(self):
        self.value = []

    def _store_line(self, raw_line):
        processed_line = self._process_line(raw_line)
        self.value.append(processed_line)

    def _process_line(self):
        raise NotImplementedError

class Time(LineType):

    def _process_line(self, raw):
        """Converts string HH:MM:SS to time"""
        
        try:
            processed = dt.datetime.strptime(raw, "%H:%M:%S").time()

        except ValueError as e:
            if raw == "calculating...": #at start of simulation
                processed = pd.NaT
            else:
                raise e
        
        return processed

class TimeDelta(LineType):

    def _process_line(self, raw):
        """Converts string HH:MM:SS to timedelta"""

        try:
            h,m,s = raw.split(":")
            processed = dt.timedelta(
                hours = int(h),
                minutes = int(m),
                seconds = int(s)
                )

        except ValueError as e:
            if raw == "...": #at start of simulation
                processed = pd.NaT
            else:
                raise e

        return processed

class Float(LineType):

    def _process_line(self, raw):
        """Converts string to float"""

        processed = float(raw)

        return processed

class Int(LineType):

    def _process_line(self, raw):
        """Converts string to integer"""

        processed = int(raw)

        return processed

class FloatSplit(LineType):

    def __init__(self, prefix, split):
        super().__init__(prefix)
        self._split = split

    def _process_line(self, raw):
        """Converts string to float, removing m3 units"""

        processed = float(raw.split(self._split)[0])

        return processed

class IntSplit(LineType):

    def __init__(self, prefix, split):
        super().__init__(prefix)
        self._split = split

    def _process_line(self, raw):
        """Converts string to integer, removing % sign"""

        processed = int(raw.split(self._split)[0])

        return processed

class String(LineType):

    def _process_line(self, raw):
        """No conversion necessary"""

        processed = raw

        return processed

class FloatMult(LineType):

    def _process_line(self, raw):
        """Converts string to list of floats"""

        processed = [float(x) for x in raw.split()]

        return processed