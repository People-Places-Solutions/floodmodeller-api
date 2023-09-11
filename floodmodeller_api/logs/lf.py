"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

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

import pandas as pd

from .._base import FMFile
from .lf_params import (
    lf1_unsteady_data_to_extract,
    lf1_steady_data_to_extract,
    lf2_data_to_extract,
)
from .lf_helpers import state_factory


class LF(FMFile):
    """Reads and processes Flood Modeller log file

    Args:
        lf1_filepath (str): Full filepath to model log file
        data_to_extract (dict): Dictionary defining each line type to parse
        steady (bool): True if for a steady-state simulation

    Output:
        Initiates 'LF' class object
    """

    def __init__(
        self,
        lf_filepath: Optional[Union[str, Path]],
        data_to_extract: dict,
        steady: bool = False,
    ):
        try:
            self._filepath = lf_filepath
            FMFile.__init__(self)

            self._data_to_extract = data_to_extract
            self._init_counters()
            self._init_parsers()
            self._state = state_factory(steady, self._extracted_data)

            self._read()

        except Exception as e:
            self._handle_exception(e, when="read")

    def _read(self, force_reread: bool = False, suppress_final_step: bool = False):
        # Read LF file
        with open(self._filepath, "r") as lf_file:
            self._raw_data = [line.rstrip("\n") for line in lf_file.readlines()]

        # Force rereading from start of file
        if force_reread == True:
            self._del_attributes()
            self._init_counters()
            self._init_parsers()

        # Process file
        self._update_data()

        if not suppress_final_step:
            self._set_attributes()

    def read(self, force_reread: bool = False, suppress_final_step: bool = False) -> None:
        """Reads log file

        Args:
            force_reread (bool): If False, starts reading from where it stopped last time. If True, starts reading from the start of the file.
            suppress_final_step (bool): If False, dataframes and dictionary are not created as attributes.

        """

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
            subdictionary_kwargs = {k: v for k, v in subdictionary.items() if k != "class"}
            subdictionary_kwargs["name"] = key
            self._extracted_data[key] = subdictionary_class(**subdictionary_kwargs)

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

    def _get_index(self):
        """Finds key and dataframe for variable that is the index"""

        for key in self._data_to_extract:
            try:
                self._data_to_extract[key]["is_index"]
                index_key = key
                index_df = self._extracted_data[key].data.get_value()
                return index_key, index_df

            except KeyError:
                pass

        raise Exception("No index variable found")

    def _set_attributes(self):
        """Makes each Parser value an attribute; "last" values in dictionary"""

        index_key, index_df = self._get_index()

        info = {}

        for key in self._data_to_extract:
            data_type = self._data_to_extract[key]["data_type"]
            value = self._extracted_data[key].data.get_value(index_key, index_df)

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

    def to_dataframe(self) -> pd.DataFrame:
        """Collects parameter values that change throughout simulation into a dataframe

        Returns:
            pd.DataFrame: DataFrame of log file parameters indexed by simulation time (unsteady) or network iterations (steady)
        """

        # TODO: make more like ZZN.to_dataframe

        data_type_all = {
            k: getattr(self, k) for k, v in self._data_to_extract.items() if v["data_type"] == "all"
        }

        df = pd.concat(data_type_all, axis=1)
        df.columns = df.columns.droplevel()

        df.sort_index(inplace=True)

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

    def report_progress(self) -> float:
        """Returns progress for unsteady simulations

        Returns:
            float: Last progress percentage recorded in log file
        """

        return self._state.report_progress()


class LF1(LF):
    """Reads and processes Flood Modeller 1D log file '.lf1'

    Args:
        lf1_filepath (str): Full filepath to model lf1 file
        steady (bool): True for steady-state simulations

    **Attributes (unsteady)**

    Args:
        info (dict): Parameters with one value per simulation
        mass_error (pandas.DataFrame): Mass error
        timestep (pandas.DataFrame): Timestep
        elapsed (pandas.DataFrame): Elapsed
        simulated (pandas.DataFrame): Simulated
        iterations (pandas.DataFrame): PlotI1
        convergence (pandas.DataFrame): PlotC1
        flow (pandas.DataFrame): PlotF1

    **Attributes (steady)**

    Args:
        info (dict): Parameters with one value per simulation
        network_iteration (pandas.DataFrame): Network iteration
        largest_change_in_split_from_last_iteration (pandas.DataFrame): Largest change in split from last iteration

    Output:
        Initiates 'LF1' class object
    """

    _filetype: str = "LF1"
    _suffix: str = ".lf1"

    def __init__(self, lf_filepath: Optional[Union[str, Path]], steady: bool = False):
        if steady == False:
            data_to_extract = lf1_unsteady_data_to_extract
        else:
            data_to_extract = lf1_steady_data_to_extract

        super().__init__(lf_filepath, data_to_extract, steady)


class LF2(LF):
    """Reads and processes Flood Modeller 1D log file '.lf2'

    Args:
        lf2_filepath (str): Full filepath to model lf2 file

    **Attributes**

    Args:
        info (dict): Parameters with one value per simulation
        simulated (pandas.DataFrame): Simulated
        wet_cells (pandas.DataFrame): Wet cells
        2D_boundary_inflow (pandas.DataFrame): 2D boundary inflow
        2D_boundary_outflow (pandas.DataFrame): 2D boundary outflow
        1D_link_flow (pandas.DataFrame): 1D link flow
        change_in_volume (pandas.DataFrame): Change in volume
        volume (pandas.DataFrame): Volume
        inst_mass_err (pandas.DataFrame): Inst mass error
        mass_error (pandas.DataFrame): Mass error
        largest_cr (pandas.DataFrame): Largest Cr
        elapsed (pandas.DataFrame): Elapsed

    Output:
        Initiates 'LF2' class object
    """

    _filetype: str = "LF2"
    _suffix: str = ".lf2"

    def __init__(self, lf_filepath: Optional[Union[str, Path]]):
        data_to_extract = {
            **lf1_unsteady_data_to_extract,
            **lf2_data_to_extract,
        }

        super().__init__(lf_filepath, data_to_extract, steady=False)


def lf_factory(filepath: str, suffix: str, steady: bool) -> LF:
    if suffix == "lf1":
        return LF1(filepath, steady)
    elif suffix == "lf2":
        return LF2(filepath)
    else:
        flow_type = "steady" if steady else "unsteady"
        raise ValueError(f"Unexpected log file type {suffix} for {flow_type} flow")
