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

from abc import ABC, abstractmethod
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
            self._init_counters()
            self._init_data_to_extract()
            self._read()

        except Exception as e:
            self._handle_exception(e, when="read")

    def _init_counters(self):
        """To keep track of file during simulation"""

        self._no_lines = 0  # number of lines that have been read so far
        self._no_iters = 0  # number of iterations so far
        self._stage = "init"  # init, start, run, end

    def _init_data_to_extract(self):
        """To process and hold data according to type"""

        stage = "start"
        self.version = String("!!Info1 version1d", stage=stage)
        self.number_of_nodes = Int(
            "!!output1  Number of 1D river nodes in model:", stage=stage
        )
        self.qtol = Float("!!Info1 qtol =", stage=stage)
        self.htol = Float("!!Info1 htol =", stage=stage)
        self.start_time = TimeDeltaH("!!Info1 Start Time:", stage=stage)
        self.end_time = TimeDeltaH("!!Info1 End Time:", stage=stage)
        self.ran_at = DateTime(
            "!!Info1 Ran at", stage=stage, code="%H:%M:%S on %d/%m/%Y"
        )
        self.max_itr = Int("!!Info1 maxitr =", stage=stage)
        self.min_itr = Int("!!Info1 minitr =", stage=stage)

        stage = "run"
        self.progress = IntSplit("!!Progress1", stage=stage, split="%")
        self.timestep = Float("!!Info1 Timestep", stage=stage, defines_iters=True)
        self.elapsed_time = TimeDeltaHMS("!!Info1 Elapsed", stage=stage)
        self.simulated_time = TimeDeltaHMS("!!Info1 Simulated", stage=stage)
        self.estimated_finish_time = Time(
            "!!Info1 EFT:",
            stage=stage,
            exclude="calculating...",
            exclude_replace=pd.NaT,
            code="%H:%M:%S",
        )
        self.estimated_time_remaining = TimeDeltaHMS(
            "!!Info1 ETR:", exclude="...", exclude_replace=pd.NaT, stage=stage
        )
        self.iterations = FloatMult("!!PlotI1", stage=stage)
        self.convergence = FloatMult("!!PlotC1", stage=stage)
        self.flow = FloatMult("!!PlotF1", stage=stage)
        self.mass_error = FloatMult("!!Info1 Mass %error =", stage=stage)

        stage = "end"
        self.simulation_time = Int(
            "!!output1 Simulation time elapsed (s):", stage=stage
        )  # TODO: timedelta
        self.no_unconverged_timesteps = Int(
            "!!output1  Number of unconverged timesteps:", stage=stage
        )
        self.prop_simulation_unconverged = FloatSplit(
            "!!output1  Proportion of simulation unconverged:", stage=stage, split="%"
        )
        self.mass_balance_interval = FloatSplit(
            "!!output1  Mass balance calculated every", stage=stage, split="s"
        )  # TODO: timedelta
        self.initial_vol = FloatSplit(
            "!!output1  Initial volume:", stage=stage, split="m3"
        )
        self.final_vol = FloatSplit("!!output1  Final volume:", stage=stage, split="m3")
        self.tot_boundary_inflow = FloatSplit(
            "!!output1  Total boundary inflow  :", stage=stage, split="m3"
        )
        self.tot_boundary_outflow = FloatSplit(
            "!!output1  Total boundary outflow :", stage=stage, split="m3"
        )
        self.tot_lat_link_inflow = FloatSplit(
            "!!output1  Total lat. link inflow :", stage=stage, split="m3"
        )
        self.tot_lat_link_outflow = FloatSplit(
            "!!output1  Total lat. link outflow:", stage=stage, split="m3"
        )
        self.max_system_volume = FloatSplit(
            "!!output1  Max. system volume:", stage=stage, split="m3"
        )
        self.max_vol_increase = FloatSplit(
            "!!output1  Max. |volume| increase:", stage=stage, split="m3"
        )
        self.max_boundary_inflow = FloatSplit(
            "!!output1  Max. boundary inflow:", stage=stage, split="m3"
        )
        self.net_vol_increase = FloatSplit(
            "!!output1  Net increase in volume:", stage=stage, split="m3"
        )
        self.net_inflow_vol = FloatSplit(
            "!!output1  Net inflow volume:", stage=stage, split="m3"
        )
        self.vol_discrepancy = FloatSplit(
            "!!output1  Volume discrepancy:", stage=stage, split="m3"
        )
        self.mass_balance_error = FloatSplit(
            "!!output1  Mass balance error:", stage=stage, split="%"
        )
        self.mass_balance_error_2 = FloatSplit(
            "!!output1  Mass balance error [2]:", stage=stage, split="%"
        )

        self._data_to_extract = [
            # start
            self.version,
            self.number_of_nodes,
            self.qtol,
            self.htol,
            self.start_time,
            self.end_time,
            self.ran_at,
            self.max_itr,
            self.min_itr,
            # run
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
            # end
            self.simulation_time,
            self.no_unconverged_timesteps,
            self.prop_simulation_unconverged,
            self.mass_balance_interval,
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
            self.mass_balance_error_2,
        ]

    def _read(self, force_reread=False):
        # Read LF1 file
        with open(self._filepath, "r") as lf1_file:
            self._raw_data = [line.rstrip("\n") for line in lf1_file.readlines()]

        # Force rereading from start of file
        if force_reread == True:
            self._init_counters()
            self._init_data_to_extract()

        # Process file
        self._process_lines()

    def _process_lines(self):
        """Sorts and processes raw data into lists for each prefix"""

        self._print_no_lines()

        # loop through lines that haven't already been read
        raw_lines = self._raw_data[self._no_lines :]
        for raw_line in raw_lines:

            # update simulation stage (start/run/end)
            self._update_stage(raw_line)

            # loop through line types
            for line_type in self._data_to_extract:

                # lines which start with prefix
                if raw_line.startswith(line_type._prefix):

                    # store everything after prefix
                    end_of_line = raw_line.split(line_type._prefix)[1].lstrip()
                    processed_line = line_type._process_line_wrapper(end_of_line)
                    line_type._update_value_wrapper(processed_line)

                    # update number of iterations (if line type defines this)
                    self._no_iters = line_type._update_iters_wrapper(self._no_iters)

                    # no need to check other line types
                    break

            # update counter
            self._no_lines += 1

        self._print_no_lines()

    def _print_no_lines(self):
        """Prints the number of lines that have been read so far"""

        print("Lines read: " + str(self._no_lines))

    def _update_stage(self, raw):
        """Update what stage of simulation we are in"""

        # TODO: check classification is robust
        # TODO: check necessary

        # start
        if self._stage == "init" and raw == "!!output1":
            self._stage = "start"

        # running
        elif self._stage == "start" and raw == "!!Progress1   0%":
            self._stage = "run"

        # end
        elif self._stage == "run" and raw == "!!output1":
            self._stage = "end"

        elif self._stage not in ("init", "start", "run", "end"):
            raise ValueError(f'Unexpected simulation stage "{self._stage}"')


class LineType(ABC):
    """Abstract base class for processing and storing different types of line"""

    def __init__(
        self, prefix, stage, exclude=None, exclude_replace=None, defines_iters=False
    ):
        self._prefix = prefix
        self._exclude = exclude
        self._exclude_replace = exclude_replace

        if defines_iters == True:
            self._update_iters_wrapper = self._increment
        else:
            self._update_iters_wrapper = self._do_not_increment

        if stage == "run":
            self.value = []  # list
            self._update_value_wrapper = self._append_to_value
        elif stage in ("start", "end"):
            self.value = None  # single value
            self._update_value_wrapper = self._replace_value
        else:
            raise ValueError(f'Unexpected simulation stage "{stage}"')

    def __repr__(self):
        return str(self.value)

    def _append_to_value(self, processed_line):
        self.value.append(processed_line)

    def _replace_value(self, processed_line):
        self.value = processed_line

    def _process_line_wrapper(self, raw_line):
        """self._process_line but with exception handling e.g. of nans"""

        try:
            processed_line = self._process_line(raw_line)

        except ValueError as e:
            if raw_line == self._exclude:
                processed_line = self._exclude_replace
            else:
                raise e

        return processed_line

    @staticmethod
    def _increment(iters):
        iters += 1
        return iters

    @staticmethod
    def _do_not_increment(iters):
        return iters

    @abstractmethod
    def _process_line(self):
        pass


class DateTime(LineType):
    def __init__(
        self,
        prefix,
        stage,
        code,
        exclude=None,
        exclude_replace=None,
        defines_iters=False,
    ):
        super().__init__(prefix, stage, exclude, exclude_replace, defines_iters)
        self._code = code

    def _process_line(self, raw):
        """Converts string to datetime"""

        processed = dt.datetime.strptime(raw, self._code)

        return processed


class Time(DateTime):
    def _process_line(self, raw):
        """Converts string to time"""

        processed = super()._process_line(raw)

        return processed.time()


class TimeDeltaHMS(LineType):
    def _process_line(self, raw):
        """Converts string HH:MM:SS to timedelta"""

        h, m, s = raw.split(":")
        processed = dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

        return processed


class TimeDeltaH(LineType):
    def _process_line(self, raw):
        """Converts string H (with decimal place) to timedelta"""

        h = raw.split("hrs")[0]
        processed = dt.timedelta(hours=float(h))
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
    def __init__(
        self,
        prefix,
        stage,
        split,
        exclude=None,
        exclude_replace=None,
        defines_iters=False,
    ):
        super().__init__(prefix, stage, exclude, exclude_replace, defines_iters)
        self._split = split

    def _process_line(self, raw):
        """Converts string to float, removing everything after split"""

        processed = float(raw.split(self._split)[0])

        return processed


class IntSplit(LineType):
    def __init__(
        self,
        prefix,
        stage,
        split,
        exclude=None,
        exclude_replace=None,
        defines_iters=False,
    ):
        super().__init__(prefix, stage, exclude, exclude_replace, defines_iters)
        self._split = split

    def _process_line(self, raw):
        """Converts string to integer, removing everything after split"""

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
