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
from abc import abstractmethod

import pandas as pd

from .._base import FMFile
from .lf_params import (
    lf1_unsteady_data_to_extract,
    lf1_steady_data_to_extract,
    lf2_data_to_extract,
)


class LF(FMFile):
    def __init__(self, lf_filepath: Optional[Union[str, Path]]):
        try:
            self._filepath = lf_filepath
            FMFile.__init__(self)
            self._init_counters()
            self._init_params_and_progress()
            self._init_parsers()
            self._read()

        except Exception as e:
            self._handle_exception(e, when="read")

    def _read(self, force_reread: bool = False, suppress_final_step: bool = False):
        # Read LF file
        with open(self._filepath, "r") as lf1_file:
            self._raw_data = [line.rstrip("\n") for line in lf1_file.readlines()]

        # Force rereading from start of file
        if force_reread == True:
            self._del_attributes()
            self._init_counters()
            self._init_parsers()

        # Process file
        self._update_data()

        if not suppress_final_step:
            self._set_attributes()

    def read(self, force_reread: bool = False, suppress_final_step: bool = False):
        """Reads LF file, starting from where it stopped reading last time"""

        self._read(force_reread, suppress_final_step)

    def _init_counters(self):
        """Initialises counters that keep track of file during simulation"""

        self._no_lines = 0  # number of lines that have been read so far
        self._no_iters = 0  # number of iterations so far

    def _init_parsers(self):
        """Creates dictionary of Parser objects for each entry in data_to_extract"""

        self._extracted_data = {}

        for key in self._data_to_extract:
            subdictionary = self._data_to_extract[key]
            subdictionary_class = subdictionary["class"]
            subdictionary_no_class = {
                k: v for k, v in subdictionary.items() if k != "class"
            }

            self._extracted_data[key] = subdictionary_class(**subdictionary_no_class)

    def _update_data(self):
        """Updates value of each Parser object based on raw data"""

        # self._print_no_lines()

        # loop through lines that haven't already been read
        raw_lines = self._raw_data[self._no_lines :]
        for raw_line in raw_lines:

            # loop through parser types
            for key in self._data_to_extract:

                parser = self._extracted_data[key]

                # lines which start with prefix
                if raw_line.startswith(parser.prefix):

                    # store everything after prefix
                    end_of_line = raw_line.split(parser.prefix)[1].lstrip()
                    parser.process_line(end_of_line)

                    # index marks the end of an iteration
                    if parser.is_index == True:
                        self._sync_cols()
                        self._no_iters += 1

            # update counter
            self._no_lines += 1

        # self._print_no_lines()

    def _set_attributes(self):
        """Makes each Parser value an attribute; "last" values in dictionary"""

        info = {}

        for key in self._data_to_extract:

            data_type = self._data_to_extract[key]["data_type"]
            value = self._extracted_data[key].data.get_value()

            if data_type == "all":
                setattr(self, key, value)
            elif data_type == "last" and value is not None:
                info[key] = value

        self.info = info

    def _del_attributes(self):
        """Deletes each Parser value direct attribute of LF"""

        for key in self._data_to_extract:
            data_type = self._data_to_extract[key]["data_type"]
            if data_type == "all":
                delattr(self, key)

        delattr(self, "info")

    def to_dataframe(self):
        """Collects Parser values (of type "all") into pandas dataframe"""

        # TODO: make more like ZZN.to_dataframe

        data_type_all = {
            k: getattr(self, k)
            for k, v in self._data_to_extract.items()
            if v["data_type"] == "all"
        }

        df = pd.concat(data_type_all, axis=1)

        return df

    def _sync_cols(self):
        """Ensures Parser values (of type "all") have an entry each iteration"""

        # loop through parser types
        for key in self._data_to_extract:

            parser = self._extracted_data[key]

            # sync parser types that are not the index
            if parser.is_index == False:

                # if their number of values is not in sync
                if parser.data_type == "all" and parser.data.no_values < (
                    self._no_iters + int(parser.before_index)
                ):
                    # append nan to the list
                    parser.data.update(parser._nan)

    def _print_no_lines(self):
        """Prints number of lines that have been read so far"""

        print("Last line read: " + str(self._no_lines))

    def _report_progress(self) -> float:
        """Returns last progress percentage"""

        progress = self._extracted_data["progress"].data.get_value()

        if progress is None:
            return 0

        return progress

    def _no_report_progress(self):
        raise NotImplementedError

    @abstractmethod
    def _init_params_and_progress(self):
        pass


class LF1(LF):
    """Reads and processes Flood Modeller 1D log file '.lf1'

    Args:
        lf1_filepath (str): Full filepath to model lf1 file

    Output:
        Initiates 'LF1' class object
    """

    _filetype: str = "LF1"
    _suffix: str = ".lf1"

    def __init__(self, lf_filepath: Optional[Union[str, Path]], steady: bool = False):
        self._steady = steady
        super().__init__(lf_filepath)

    def _init_params_and_progress(self):
        """Uses dictionary from lf1_params.py to define data to extract"""
        # TODO: make steady/unsteady a class
        if self._steady:
            self._data_to_extract = lf1_steady_data_to_extract
            self.report_progress = self._no_report_progress
        else:
            self._data_to_extract = lf1_unsteady_data_to_extract
            self.report_progress = self._report_progress


class LF2(LF):
    """Reads and processes Flood Modeller 1D log file '.lf2'

    Args:
        lf2_filepath (str): Full filepath to model lf2 file

    Output:
        Initiates 'LF2' class object
    """

    _filetype: str = "LF2"
    _suffix: str = ".lf2"

    def _init_params_and_progress(self):
        """Uses dictionary from lf2_params.py to define data to extract"""
        self._data_to_extract = lf2_data_to_extract
        self.report_progress = self._report_progress


def lf_factory(filepath: str, suffix: str, steady: bool) -> LF:
    if suffix == "lf1" and not steady:
        return LF1(filepath)
    elif suffix == "lf1" and steady:
        return LF1(filepath, steady=True)
    elif suffix == "lf2" and steady:
        return LF2(filepath)
    else:
        flow_type = "steady" if steady else "unsteady"
        raise ValueError(f"Unexpected log file type {suffix} for {flow_type} flow")
