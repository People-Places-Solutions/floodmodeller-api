"""
Flood Modeller Python API
Copyright (C) 2025 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import TYPE_CHECKING

import pandas as pd

from .._base import FMFile
from ..util import handle_exception
from .lf_helpers import state_factory
from .lf_params import (
    lf1_steady_data_to_extract,
    lf1_unsteady_data_to_extract,
    lf2_data_to_extract,
)

if TYPE_CHECKING:
    from pathlib import Path


OLD_FILE = 5
LOG_TIMEOUT = 10


class LF(FMFile):
    """Reads and processes Flood Modeller log file

    Args:
        lf1_filepath (str): Full filepath to model log file
        data_to_extract (dict): Dictionary defining each line type to parse
        steady (bool): True if for a steady-state simulation

    Output:
        Initiates 'LF' class object
    """

    @handle_exception(when="read")
    def __init__(
        self,
        lf_filepath: str | Path | None,
        data_to_extract: dict[str, dict],
        steady: bool = False,
    ):
        FMFile.__init__(self, lf_filepath)

        self._data_to_extract = data_to_extract
        self._init_counters()
        self._init_parsers()
        self._state = state_factory(steady, self._extracted_data)

        self._read()

    def _read(self, force_reread: bool = False, suppress_final_step: bool = False):
        # Read LF file
        with open(self._filepath) as lf_file:
            self._raw_data = [line.rstrip("\n") for line in lf_file]

        # Force rereading from start of file
        if force_reread is True:
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
                    if parser.is_index is True:
                        self._sync_cols()
                        self._no_iters += 1

            # update counter
            self._no_lines += 1

    def _get_index(self):
        """Finds key and dataframe for variable that is the index"""

        for k, v in self._data_to_extract.items():
            if "is_index" in v:
                return k, self._extracted_data[k].data.get_value()

        msg = "No index variable found"
        raise Exception(msg)

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

    def to_dataframe(self, variable: str = "all", *, include_tuflow: bool = False) -> pd.DataFrame:
        """Collects parameter values that change throughout simulation into a dataframe

        Args:
            include_tuflow (bool): Include diagnostics for linked TUFLOW models

        Returns:
            pd.DataFrame: DataFrame of log file parameters indexed by simulation time (unsteady) or network iterations (steady)
        """

        lf_df_data = {
            k: getattr(self, k)
            for k, v in self._data_to_extract.items()
            if v["data_type"] == "all"  # with entries every iteration
            and (include_tuflow or "tuflow" not in k)  # tuflow-related only if requested
            and (variable in ("all", k, *v.get("subheaders", [])))  # if it or all are requested
        }

        if lf_df_data == {}:
            msg = f"No data extracted for variable '{variable}'"
            raise ValueError(msg)

        lf_df = pd.concat(lf_df_data, axis=1)
        lf_df.columns = lf_df.columns.droplevel()
        if variable != "all":
            lf_df = lf_df[variable]  # otherwise subheaders result in extra columns
        return lf_df.sort_index()

    def _sync_cols(self):
        """Ensures Parser values (of type "all") have an entry each iteration"""

        # loop through parser types
        for key in self._data_to_extract:
            parser = self._extracted_data[key]

            # sync parser types that are not the index
            if (
                parser.is_index is False  # if their number of values is not in sync
                and parser.data_type == "all"
                and parser.data.no_values < (self._no_iters + int(parser.before_index))
            ):
                # append nan to the list
                parser.data.update(parser._nan)

    def _print_no_lines(self):
        """Prints number of lines that have been read so far"""

        logging.info("Last line read: %s", self._no_lines)

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
        tuflow_vol (pandas.DataFrame): TUFLOW HPC Vol
        tuflow_n_wet (pandas.DataFrame): TUFLOW HPC nWet
        tuflow_dt (pandas.DataFrame): TUFLOW HPC dt
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

    def __init__(self, lf_filepath: str | Path | None, steady: bool = False):
        if steady is False:
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

    def __init__(self, lf_filepath: str | Path | None):
        data_to_extract = {
            **lf1_unsteady_data_to_extract,
            **lf2_data_to_extract,
        }

        super().__init__(lf_filepath, data_to_extract, steady=False)


def create_lf(filepath: Path, suffix: str) -> LF1 | LF2 | None:
    """Checks for a new log file, waiting for its creation if necessary"""

    def _no_log_file(reason: str) -> None:
        logging.warning("No progress bar as %s. Simulation will continue as usual.", reason)

    # ensure progress bar is supported
    if suffix not in {"lf1", "lf2"}:
        _no_log_file("log file must have suffix lf1 or lf2")
        return None

    # wait for log file to exist
    log_file_exists = False
    max_time = time.time() + LOG_TIMEOUT

    while not log_file_exists:
        time.sleep(0.1)

        log_file_exists = filepath.is_file()

        # timeout
        if (not log_file_exists) and (time.time() > max_time):
            _no_log_file("log file is expected but not detected")
            return None

    # wait for new log file
    old_log_file = True
    max_time = time.time() + LOG_TIMEOUT

    while old_log_file:
        time.sleep(0.1)

        # difference between now and when log file was last modified
        last_modified_timestamp = filepath.stat().st_mtime
        last_modified = dt.datetime.fromtimestamp(last_modified_timestamp)
        time_diff_sec = (dt.datetime.now() - last_modified).total_seconds()

        # it's old if it's over OLD_FILE seconds old
        old_log_file = time_diff_sec > OLD_FILE

        # timeout
        if old_log_file and (time.time() > max_time):
            _no_log_file("log file is from previous run")
            return None

    # create LF instance
    return LF1(filepath) if suffix == "lf1" else LF2(filepath)
