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

    _ultimate_prefix = "!!"
    _prefixes_dict = {
            # start
            "Version": "Info1 version1d",
            "Number of nodes": "output1  Number of 1D river nodes in model:",
            # running
            "Timestep": "Info1 Timestep",
            "Elapsed time": "Info1 Elapsed",
            "Simulated time": "Info1 Simulated",
            "Estimated finish time": "Info1 EFT:",
            "Estimated time remaining": "Info1 ETR:",
            "Iterations": "PlotI1",
            "Convergence": "PlotC1",
            "Flow": "PlotF1",
            "Mass error": "Info1 Mass %error =",
            "Progress": "Progress1",
            # end
            "Initial volume": "output1  Initial volume:",
            "Final volume": "output1  Final volume:",
        }

    def __init__(self, lf1_filepath: Optional[Union[str, Path]]):
        try:
            self._filepath = lf1_filepath
            FMFile.__init__(self)

            # counter to keep track of file during simulation
            self._lines_read = 0 

            # dictionary to hold processed data according to type
            self._processed_lines_dict = {key: [] for key in self._prefixes_dict.keys()}

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
            
            # categorise lines according to prefix
            for key in self._prefixes_dict.keys():

                # lines which start with prefix
                start_of_line = self._ultimate_prefix + self._prefixes_dict[key]
                if raw_line.startswith(start_of_line):

                    # list to append to
                    processed_lines = self._processed_lines_dict[key]

                    # add everything after prefix to list
                    end_of_line = raw_line.split(start_of_line)[1].lstrip()
                    processed_lines.append(self._str_to_data(end_of_line, key))
            
            # update counter
            self._lines_read += 1

        self._print_lines_read()

    def _print_lines_read(self):
        """Prints the number of lines that have been read so far"""

        print("Lines read: " + str(self._lines_read))

    def _str_to_data(self, data_str, key):
        """Processes string into meaningful data"""

        # one float
        if key == "Timestep":
            processed_data = float(data_str)

        # one integer
        elif key == "Number of nodes":
            processed_data = int(data_str)

        # multiple floats
        elif key in ("Iterations", "Convergence", "Flow", "Mass error"):
            processed_data = [float(x) for x in data_str.split()]

        # volume (m3)
        elif key in ("Initial volume", "Final volume"):
            processed_data = float(data_str.split("m3")[0])

        # percentage (%)
        elif key == "Progress":
            processed_data = float(data_str.split("%")[0])/100

        # time
        elif key == "Estimated finish time":
            processed_data = self._str_to_time(data_str)

        # timedelta
        elif key in ("Elapsed time", "Simulated time", "Estimated time remaining"):
            processed_data = self._str_to_timedelta(data_str)

        # string
        elif key == "Version":
            processed_data = data_str

        else:
            raise ValueError(f"{key} is not a valid prefix")

        return(processed_data)

    def _str_to_time(self, data_str):
        """Converts string HH:MM:SS to time"""
        
        try:
            data_time = dt.datetime.strptime(data_str, "%H:%M:%S").time()

        except ValueError as e:
            if data_str == "calculating...": #at start of simulation
                data_time = pd.NaT
            else:
                raise e
        
        return(data_time)

    def _str_to_timedelta(self, data_str):
        """Converts string HH:MM:SS to timedelta"""

        try:
            h,m,s = data_str.split(":")
            data_timedelta = dt.timedelta(
                hours = int(h),
                minutes = int(m),
                seconds = int(s)
                )

        except ValueError as e:
            if data_str == "...": #at start of simulation
                data_timedelta = pd.NaT
            else:
                raise e

        return(data_timedelta)