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

from pathlib import Path
from typing import Optional, Union
from unicodedata import category

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
            #"Timestep": "Info1 Timestep",
            "Elapsed time": "Info1 Elapsed",
            "Simulated time": "Info1 Simulated",
            #"Estimated finish time": "Info1 EFT:",
            "Estimated time remaining": "Info1 ETR:",
            #"Iterations": "PlotI1",
            #"Convergence": "PlotC1",
            #"Flow": "PlotF1",
        }

    def __init__(self, lf1_filepath: Optional[Union[str, Path]]):
        try:
            self._filepath = lf1_filepath
            FMFile.__init__(self)

            # counter to keep track of file during simulation
            self._lines_read = 0 

            # dictionary to hold sorted lines according to type (for use during development)
            self._sorted_lines_dict = {key: [] for key in self._prefixes_dict.keys()}

            # dictionary to hold processed data according to type
            self._processed_data_dict = {key: [] for key in self._prefixes_dict.keys()}

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
        self._sort_lines()

    def _sort_lines(self):
        """Sorts raw data into lists for each prefix"""

        self._print_lines_read()

        # loop through lines that haven't already been read
        raw_lines = self._raw_data[self._lines_read:]

        for raw_line in raw_lines:
            
            # categorise lines according to prefix
            for key in self._prefixes_dict.keys():

                # lists to append to
                sorted_lines = self._sorted_lines_dict[key]
                processed_data = self._processed_data_dict[key]

                # lines which start with prefix
                start_of_line = self._ultimate_prefix + self._prefixes_dict[key]

                # add everything after prefix to the lists
                if raw_line.startswith(start_of_line):
                    end_of_line = raw_line.split(start_of_line)[1].lstrip()
                    sorted_lines.append(end_of_line)
                    processed_data.append(self._process_data(end_of_line))
            
            # update counter
            self._lines_read += 1

        self._print_lines_read()

    def _print_lines_read(self):
        """Prints the number of lines that have been read so far"""
        print("Lines read: " + str(self._lines_read))

    def _process_data(self, data_str):
        """Processes string into meaningful data"""
        if data_str == "...":
            processed_data = float("nan")     
        else:
            processed_data = self._str_to_sec(data_str)
        return(processed_data)

    def _str_to_sec(self, time_str):
        """Converts time string HH:MM:SS to seconds"""
        h,m,s = time_str.split(":")
        time_sec = 3600*int(h) + 60*int(m) + int(s) 
        return(time_sec)