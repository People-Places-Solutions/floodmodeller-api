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

import ctypes as ct
import logging
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any

import numpy as np
import pandas as pd

from ._base import FMFile
from .to_from_json import to_json
from .util import get_associated_file, handle_exception, is_windows

if TYPE_CHECKING:
    from collections.abc import Mapping


def get_reader() -> ct.CDLL:
    # Get zzn_dll path
    lib = "zzn_read.dll" if is_windows() else "libzzn_read.so"
    zzn_dll = Path(__file__).resolve().parent / "libs" / lib

    # Catch LD_LIBRARY_PATH error for linux
    try:
        return ct.CDLL(str(zzn_dll))
    except OSError as e:
        msg_1 = "libifport.so.5: cannot open shared object file: No such file or directory"
        if msg_1 in str(e):
            msg_2 = "Set LD_LIBRARY_PATH environment variable to be floodmodeller_api/lib"
            raise OSError(msg_2) from e
        raise


def check_errstat(routine: str, errstat: int) -> None:
    if errstat != 0:
        msg = (
            f"Errstat from {routine} routine is {errstat}."
            " See zzread_errorlog.txt for more information."
        )
        raise RuntimeError(msg)


def run_routines(
    reader: ct.CDLL,
    zzl: Path,
    zzn_or_zzx: Path,
    is_quality: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data: dict[str, Any] = {}
    meta: dict[str, Any] = {}

    zzx_or_zzn_name = "zzx_name" if is_quality else "zzn_name"
    zzx_or_zzl_name = "zzx_name" if is_quality else "zzl_name"
    meta[zzx_or_zzn_name] = ct.create_string_buffer(bytes(str(zzn_or_zzx), "utf-8"), 255)
    meta["zzl_name"] = ct.create_string_buffer(bytes(str(zzl), "utf-8"), 255)

    # process zzl
    meta["model_title"] = ct.create_string_buffer(b"", 128)
    meta["nnodes"] = ct.c_int(0)
    meta["label_length"] = ct.c_int(0)
    meta["dt"] = ct.c_float(0.0)
    meta["timestep0"] = ct.c_int(0)
    meta["ltimestep"] = ct.c_int(0)
    meta["save_int"] = ct.c_float(0.0)
    meta["is_quality"] = ct.c_bool(is_quality)
    meta["nvars"] = ct.c_int(0)
    meta["tzero"] = (ct.c_int * 5)()
    meta["errstat"] = ct.c_int(0)

    reader.process_zzl(
        ct.byref(meta[zzx_or_zzl_name]),
        ct.byref(meta["model_title"]),
        ct.byref(meta["nnodes"]),
        ct.byref(meta["label_length"]),
        ct.byref(meta["dt"]),
        ct.byref(meta["timestep0"]),
        ct.byref(meta["ltimestep"]),
        ct.byref(meta["save_int"]),
        ct.byref(meta["is_quality"]),
        ct.byref(meta["nvars"]),
        ct.byref(meta["tzero"]),
        ct.byref(meta["errstat"]),
    )
    check_errstat("process_zzl", meta["errstat"].value)

    # process labels
    if meta["label_length"].value == 0:  # means that we are probably running quality data
        meta["label_length"].value = 12  # 12 is the max expected from dll

    reader.process_labels(
        ct.byref(meta["zzl_name"]),
        ct.byref(meta["nnodes"]),
        ct.byref(meta["label_length"]),
        ct.byref(meta["errstat"]),
    )
    check_errstat("process_labels", meta["errstat"].value)

    # get zz labels
    meta["labels"] = (ct.c_char * meta["label_length"].value * meta["nnodes"].value)()
    for i in range(meta["nnodes"].value):
        reader.get_zz_label(
            ct.byref(ct.c_int(i + 1)),
            ct.byref(meta["labels"][i]),
            ct.byref(meta["errstat"]),
        )
        check_errstat("get_zz_label", meta["errstat"].value)

    # preprocess zzn
    last_hr = (meta["ltimestep"].value - meta["timestep0"].value) * meta["dt"].value / 3600
    meta["output_hrs"] = (ct.c_float * 2)(0.0, last_hr)
    meta["aitimestep"] = (ct.c_int * 2)(meta["timestep0"].value, meta["ltimestep"].value)
    meta["isavint"] = (ct.c_int * 2)()
    reader.preprocess_zzn(
        ct.byref(meta["output_hrs"]),
        ct.byref(meta["aitimestep"]),
        ct.byref(meta["dt"]),
        ct.byref(meta["timestep0"]),
        ct.byref(meta["ltimestep"]),
        ct.byref(meta["save_int"]),
        ct.byref(meta["isavint"]),
    )

    # process vars
    reader.process_vars(
        ct.byref(meta[zzx_or_zzl_name]),
        ct.byref(meta["nvars"]),
        ct.byref(meta["is_quality"]),
        ct.byref(meta["errstat"]),
    )
    check_errstat("process_vars", meta["errstat"].value)

    # get var names
    meta["variables"] = (ct.c_char * 32 * meta["nvars"].value)()
    for i in range(meta["nvars"].value):
        reader.get_zz_variable_name(
            ct.byref(ct.c_int(i + 1)),
            ct.byref(meta["variables"][i]),
            ct.byref(meta["errstat"]),
        )
        check_errstat("get_zz_variable_name", meta["errstat"].value)

    # process zzn
    meta["node_ID"] = ct.c_int(-1)
    meta["savint_skip"] = ct.c_int(1)
    meta["savint_range"] = ct.c_int(
        int((meta["isavint"][1] - meta["isavint"][0]) / meta["savint_skip"].value),
    )
    nx = meta["nnodes"].value
    ny = meta["nvars"].value
    nz = meta["savint_range"].value + 1
    data["all_results"] = (ct.c_float * nx * ny * nz)()
    data["max_results"] = (ct.c_float * nx * ny)()
    data["min_results"] = (ct.c_float * nx * ny)()
    data["max_times"] = (ct.c_int * nx * ny)()
    data["min_times"] = (ct.c_int * nx * ny)()
    reader.process_zzn(
        ct.byref(meta[zzx_or_zzn_name]),
        ct.byref(meta["node_ID"]),
        ct.byref(meta["nnodes"]),
        ct.byref(meta["is_quality"]),
        ct.byref(meta["nvars"]),
        ct.byref(meta["savint_range"]),
        ct.byref(meta["savint_skip"]),
        ct.byref(data["all_results"]),
        ct.byref(data["max_results"]),
        ct.byref(data["min_results"]),
        ct.byref(data["max_times"]),
        ct.byref(data["min_times"]),
        ct.byref(meta["errstat"]),
        ct.byref(meta["isavint"]),
    )
    check_errstat("process_zzn", meta["errstat"].value)

    return data, meta


def convert_data(data: dict[str, Any]) -> None:
    for key, value in data.items():
        data[key] = np.array(value)


def convert_meta(meta: dict[str, Any]) -> None:
    to_get_value = (
        "dt",
        "errstat",
        "is_quality",
        "label_length",
        "ltimestep",
        "nnodes",
        "node_ID",
        "nvars",
        "save_int",
        "savint_range",
        "savint_skip",
        "timestep0",
    )
    for key in to_get_value:
        meta[key] = meta[key].value

    to_get_list = ("aitimestep", "isavint", "output_hrs", "tzero", "variables")
    for key in to_get_list:
        meta[key] = list(meta[key])

    to_get_decoded_value = ("model_title", "zzl_name", "zzx_name", "zzn_name")
    for key in to_get_decoded_value:
        if key not in meta:
            continue
        meta[key] = meta[key].value.decode()

    to_get_decoded_value_list = ("labels", "variables")
    for key in to_get_decoded_value_list:
        meta[key] = [x.value.decode().strip() for x in list(meta[key])]


class _ZZ(FMFile):
    """Base class for ZZN and ZZX."""

    @handle_exception(when="read")
    def __init__(
        self,
        zzn_filepath: str | Path | None = None,
        from_json: bool = False,
    ):
        if from_json:
            return

        FMFile.__init__(self, zzn_filepath)

        reader = get_reader()
        zzl = get_associated_file(self._filepath, ".zzl")

        is_quality = self._suffix == ".zzx"

        self._data, self._meta = run_routines(reader, zzl, self._filepath, is_quality)
        convert_data(self._data)
        convert_meta(self._meta)

        self._nx = self._meta["nnodes"]
        self._ny = self._meta["nvars"]
        self._nz = self._meta["savint_range"] + 1
        self._variables = (
            self._meta["variables"]
            if is_quality
            else ["Flow", "Stage", "Froude", "Velocity", "Mode", "State"]
        )
        self._index_name = "Label" if is_quality else "Node Label"

    @property
    def meta(self) -> Mapping[str, Any]:
        return MappingProxyType(self._meta)  # because dictionaries are mutable

    def _get_all(self, variable: str, multilevel_header: bool) -> pd.DataFrame:
        is_all = variable == "all"

        variable_display_name = variable.capitalize().replace("fp", "FP")

        arr = self._data["all_results"]
        time_index = np.linspace(self._meta["output_hrs"][0], self._meta["output_hrs"][1], self._nz)

        if multilevel_header:
            result = pd.DataFrame(
                arr.reshape(self._nz, self._nx * self._ny),
                index=time_index,
                columns=pd.MultiIndex.from_product([self._variables, self._meta["labels"]]),
            )
            result.index.name = "Time (hr)"
            return result if is_all else result[variable_display_name]  # type: ignore
            # ignored because it always returns a dataframe as it's a multilevel header

        result = pd.DataFrame(
            arr.reshape(self._nz, self._nx * self._ny),
            index=time_index,
            columns=[f"{node}_{var}" for var in self._variables for node in self._meta["labels"]],
        )
        result.index.name = "Time (hr)"
        return (
            result
            if is_all
            else result[[x for x in result.columns if x.endswith(variable_display_name)]]
        )

    def _get_extremes(
        self,
        variable: str,
        result_type: str,
        include_time: bool,
    ) -> pd.Series | pd.DataFrame:
        is_all = variable == "all"

        result_type_display_name = result_type.capitalize()
        variable_display_name = variable.capitalize().replace("fp", "FP")

        combination = f"{result_type_display_name} {variable_display_name}"

        arr = self._data[f"{result_type}_results"].transpose()
        node_index = self._meta["labels"]
        col_names = [f"{result_type_display_name} {x}" for x in self._variables]
        result = pd.DataFrame(arr, index=node_index, columns=col_names)
        result.index.name = self._index_name

        if not include_time:
            # df[combination] is the only time we get a series in _ZZ.get_dataframe()
            return result if is_all else result[combination]

        times = self._data[f"{result_type}_times"].transpose()
        times = np.linspace(self._meta["output_hrs"][0], self._meta["output_hrs"][1], self._nz)[
            times - 1
        ]
        time_col_names = [name + " Time(hrs)" for name in col_names]
        time_df = pd.DataFrame(times, index=node_index, columns=time_col_names)
        time_df.index.name = self._index_name
        result = pd.concat([result, time_df], axis=1)
        new_col_order = [x for y in list(zip(col_names, time_col_names)) for x in y]
        result = result[new_col_order]
        return result if is_all else result[[combination, f"{combination} Time(hrs)"]]

    def to_dataframe(
        self,
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
        multilevel_header: bool = True,
    ) -> pd.Series | pd.DataFrame:
        result_type = result_type.lower()

        if result_type == "all":
            return self._get_all(variable, multilevel_header)

        if result_type in {"max", "min"}:
            return self._get_extremes(variable, result_type, include_time)

        msg = f"Result type '{result_type}' not recognised"
        raise ValueError(msg)

    def export_to_csv(
        self,
        save_location: str | Path = "default",
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
    ) -> None:
        if save_location == "default":
            save_location = self._filepath.with_suffix(".csv")
        else:
            save_location = (
                Path(save_location)
                if Path(save_location).is_absolute()
                else self._filepath.parent / save_location
            )

        if save_location.suffix != ".csv":  # Assumed to be pointing to a folder
            save_location = save_location / self._filepath.with_suffix(".csv").name

        save_location.parent.mkdir(parents=True, exist_ok=True)

        zz_df = self.to_dataframe(
            result_type=result_type,
            variable=variable,
            include_time=include_time,
        )
        zz_df.to_csv(save_location)
        logging.info("CSV saved to %s", save_location)

    def to_json(
        self,
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
        multilevel_header: bool = True,
    ) -> str:
        zz_df = self.to_dataframe(result_type, variable, include_time, multilevel_header)
        return to_json(zz_df)

    @classmethod
    def from_json(cls, json_string: str = ""):
        msg = f"It is not possible to build a {cls._filetype} class instance from JSON"
        raise NotImplementedError(msg)


class ZZN(_ZZ):
    """Reads and processes Flood Modeller 1D binary results format '.zzn'

    Args:
        zzn_filepath (str): Full filepath to model zzn file

    Output:
        Initiates 'ZZN' class object
    """

    _filetype: str = "ZZN"
    _suffix: str = ".zzn"

    def to_dataframe(self, *args, **kwargs) -> pd.Series | pd.DataFrame:
        """Loads ZZN results to pandas dataframe object.

        Args:
            result_type (str, optional): {'all'} | 'max' | 'min'
                Define whether to return all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Flow' | 'Stage' | 'Froude' | 'Velocity' | 'Mode' | 'State'
                Specify a single output variable (e.g 'flow' or 'stage'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.
            multilevel_header (bool, optional): If True, the returned dataframe will have multi-level column
                headers with the variable as first level and node label as second header. If False, the column
                names will be formatted "{node label}_{variable}". Defaults to True.

        Returns:
            pandas.DataFrame(): dataframe object of simulation results
        """
        return super().to_dataframe(*args, **kwargs)

    def export_to_csv(self, *args, **kwargs) -> None:
        """Exports ZZN results to CSV file.

        Args:
            save_location (str, optional): {default} | folder or file path
                Full or relative path to folder or csv file to save output csv,
                if no argument given or if set to 'default' then CSV will be saved in same location as ZZN file.
                Defaults to 'default'.
            result_type (str, optional): {all} | max | min
                Define whether to output all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Flow' | 'Stage' | 'Froude' | 'Velocity' | 'Mode' | 'State'
                Specify a single output variable (e.g 'flow' or 'stage'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.

        Raises:
            Exception: Raised if result_type set to invalid option
        """
        return super().export_to_csv(*args, **kwargs)

    def to_json(self, *args, **kwargs) -> str:
        """Loads ZZN results to JSON object.

        Args:
            result_type (str, optional): {'all'} | 'max' | 'min'
                Define whether to return all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Flow' | 'Stage' | 'Froude' | 'Velocity' | 'Mode' | 'State'
                Specify a single output variable (e.g 'flow' or 'stage'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.
            multilevel_header (bool, optional): If True, the returned dataframe will have multi-level column
                headers with the variable as first level and node label as second header. If False, the column
                names will be formatted "{node label}_{variable}". Defaults to True.

        Returns:
            str: A JSON string representing the results.
        """
        return super().to_json(*args, **kwargs)


class ZZX(_ZZ):
    """Reads and processes Flood Modeller 1D binary results format '.zzx'

    Args:
        zzx_filepath (str): Full filepath to model zzx file

    Output:
        Initiates 'ZZX' class object
    """

    _filetype: str = "ZZX"
    _suffix: str = ".zzx"

    def to_dataframe(self, *args, **kwargs) -> pd.Series | pd.DataFrame:
        """Loads ZZX results to pandas dataframe object.

        Args:
            result_type (str, optional): {'all'} | 'max' | 'min'
                Define whether to return all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Left FP h' | 'Link inflow' | 'Right FP h' | 'Right FP mode' | 'Left FP mode'
                Specify a single output variable (e.g 'link inflow'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.
            multilevel_header (bool, optional): If True, the returned dataframe will have multi-level column
                headers with the variable as first level and node label as second header. If False, the column
                names will be formatted "{node label}_{variable}". Defaults to True.

        Returns:
            pandas.DataFrame(): dataframe object of simulation results
        """
        return super().to_dataframe(*args, **kwargs)

    def export_to_csv(self, *args, **kwargs) -> None:
        """Exports ZZX results to CSV file.

        Args:
            save_location (str, optional): {default} | folder or file path
                Full or relative path to folder or csv file to save output csv,
                if no argument given or if set to 'default' then CSV will be saved in same location as ZZN file.
                Defaults to 'default'.
            result_type (str, optional): {all} | max | min
                Define whether to output all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Left FP h' | 'Link inflow' | 'Right FP h' | 'Right FP mode' | 'Left FP mode'
                Specify a single output variable (e.g 'link inflow'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.

        Raises:
            Exception: Raised if result_type set to invalid option
        """
        return super().export_to_csv(*args, **kwargs)

    def to_json(self, *args, **kwargs) -> str:
        """Loads ZZX results to JSON object.

        Args:
            result_type (str, optional): {'all'} | 'max' | 'min'
                Define whether to return all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Left FP h' | 'Link inflow' | 'Right FP h' | 'Right FP mode' | 'Left FP mode'
                Specify a single output variable (e.g 'link inflow'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.
            multilevel_header (bool, optional): If True, the returned dataframe will have multi-level column
                headers with the variable as first level and node label as second header. If False, the column
                names will be formatted "{node label}_{variable}". Defaults to True.

        Returns:
            str: A JSON string representing the results.
        """
        return super().to_json(*args, **kwargs)
