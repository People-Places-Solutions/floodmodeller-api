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

from .._base import FMFile
from .lf1_params import data_to_extract


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

        self._data_to_extract = data_to_extract

        for key in self._data_to_extract:
            subdictionary = self._data_to_extract[key]
            subdictionary_class = subdictionary["class"]
            subdictionary_noclass = {k: v for k, v in subdictionary.items() if k != "class"}
            subdictionary["object"] = subdictionary_class(**subdictionary_noclass)

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
            for key in self._data_to_extract:

                line_type = self._data_to_extract[key]["object"]

                # lines which start with prefix
                if raw_line.startswith(line_type.prefix):

                    self._match_rows(line_type)

                    # store everything after prefix
                    end_of_line = raw_line.split(line_type.prefix)[1].lstrip()
                    processed_line = line_type.process_line_wrapper(end_of_line)
                    line_type.update_value_wrapper(processed_line)

                    # no need to check other line types
                    break

            # update counter
            self._no_lines += 1

        self._print_no_lines()

    def _match_rows(self, line_type):
        """Matches up rows of dataframe according to iterations"""

        # increment iters
        if line_type.defines_iters == True:
            self._no_iters += 1

        # if it's the first one of its type
        elif (
            line_type.stage == "run"
            and len(line_type.value) == 0
            and self._no_iters >= 1
        ):
            # fill in previous iterations with nan
            for i in range(self._no_iters):
                line_type.value.append("missing")  # TODO: actual nan
    
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


