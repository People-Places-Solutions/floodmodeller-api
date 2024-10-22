"""
Flood Modeller Python API
Copyright (C) 2024 Jacobs U.K. Limited

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
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from ._base import FMFile
from .to_from_json import to_json
from .util import handle_exception, is_windows


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


def get_associated_file(original_file: Path, new_suffix: str) -> Path:
    new_file = original_file.with_suffix(new_suffix)
    if not new_file.exists():
        msg = (
            f"Error: Could not find associated {new_suffix} file."
            f" Ensure that the {original_file.suffix} results"
            f" have an associated {new_suffix} file with matching name."
        )
        raise FileNotFoundError(msg)
    return new_file


def check_errstat(routine: str, errstat: int) -> None:
    if errstat != 0:
        msg = (
            f"Errstat from {routine} routine is {errstat}."
            " See zzread_errorlog.txt for more information."
        )
        raise RuntimeError(msg)


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

    to_get_decoded_value = ("model_title", "zzl_name", "zzn_or_zzx_name")
    for key in to_get_decoded_value:
        meta[key] = meta[key].value.decode()

    to_get_decoded_value_list = ("labels", "variables")
    for key in to_get_decoded_value_list:
        meta[key] = [x.value.decode().strip() for x in list(meta[key])]


def convert_data(data: dict[str, Any]) -> None:
    for key in data:
        data[key] = np.array(data[key])


def check_if_quality(zzn_or_zzx: Path) -> bool:
    if zzn_or_zzx.suffix not in {".zzn", ".zzx"}:
        msg = f"File '{zzn_or_zzx}' does not have suffix '.zzn' or '.zzx.'"
        raise ValueError(msg)
    return zzn_or_zzx.suffix == ".zzx"


def run_routines(
    reader: ct.CDLL,
    zzl: Path,
    zzn_or_zzx: Path,
    zzl_or_zzx: str,
    *,
    is_quality: bool,
) -> tuple[dict[str, Any], dict[str, Any]]:
    data: dict[str, Any] = {}
    meta: dict[str, Any] = {}

    meta["zzn_or_zzx_name"] = ct.create_string_buffer(bytes(str(zzn_or_zzx), "utf-8"), 255)
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
        ct.byref(meta[zzl_or_zzx]),
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
        ct.byref(meta[zzl_or_zzx]),
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
        ct.byref(meta["zzn_or_zzx_name"]),
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


def process_zzn_or_zzx(zzn_or_zzx: Path) -> tuple[dict[str, Any], dict[str, Any], list[str]]:
    reader = get_reader()
    zzl = get_associated_file(zzn_or_zzx, ".zzl")

    is_quality = check_if_quality(zzn_or_zzx)
    zzl_or_zzx = "zzn_or_zzx_name" if is_quality else "zzl_name"

    data, meta = run_routines(reader, zzl, zzn_or_zzx, zzl_or_zzx, is_quality=is_quality)
    convert_data(data)
    convert_meta(meta)

    variables = (
        meta["variables"]
        if is_quality
        else ["Flow", "Stage", "Froude", "Velocity", "Mode", "State"]
    )

    return data, meta, variables


def get_dimensions(meta: dict[str, Any]) -> tuple[int, int, int]:
    nx = meta["nnodes"]
    ny = meta["nvars"]
    nz = meta["savint_range"] + 1
    return nx, ny, nz


def get_all(
    data: dict[str, Any],
    meta: dict[str, Any],
    variables: list,
    variable: str,
    multilevel_header: bool,
) -> pd.DataFrame:
    nx, ny, nz = get_dimensions(meta)

    arr = data["all_results"]
    time_index = np.linspace(meta["output_hrs"][0], meta["output_hrs"][1], nz)

    if multilevel_header:
        col_names = [variables, meta["labels"]]
        df = pd.DataFrame(
            arr.reshape(nz, nx * ny),
            index=time_index,
            columns=pd.MultiIndex.from_product(col_names),
        )
        df.index.name = "Time (hr)"
        if variable != "all":
            return df[variable.capitalize()]

    else:
        col_names = [f"{node}_{var}" for var in variables for node in meta["labels"]]
        df = pd.DataFrame(arr.reshape(nz, nx * ny), index=time_index, columns=col_names)
        df.index.name = "Time (hr)"
        if variable != "all":
            use_cols = [col for col in df.columns if col.endswith(variable.capitalize())]
            return df[use_cols]

    return df


def get_extremes(
    data: dict[str, Any],
    meta: dict[str, Any],
    result_type: str,
    variable: str,
    include_time: bool,
) -> pd.DataFrame:
    _, _, nz = get_dimensions(meta)

    arr = data[f"{result_type}_results"].transpose()
    node_index = meta["labels"]
    col_names = [
        result_type.capitalize() + lbl
        for lbl in [
            " Flow",
            " Stage",
            " Froude",
            " Velocity",
            " Mode",
            " State",
        ]
    ]
    df = pd.DataFrame(arr, index=node_index, columns=col_names)
    df.index.name = "Node Label"

    if include_time:
        times = data[f"{result_type}_times"].transpose()
        times = np.linspace(meta["output_hrs"][0], meta["output_hrs"][1], nz)[times - 1]
        time_col_names = [name + " Time(hrs)" for name in col_names]
        time_df = pd.DataFrame(times, index=node_index, columns=time_col_names)
        time_df.index.name = "Node Label"
        df = pd.concat([df, time_df], axis=1)
        new_col_order = [x for y in list(zip(col_names, time_col_names)) for x in y]
        df = df[new_col_order]
        if variable != "all":
            return df[
                [
                    f"{result_type.capitalize()} {variable.capitalize()}",
                    f"{result_type.capitalize()} {variable.capitalize()} Time(hrs)",
                ]
            ]
        return df

    if variable != "all":
        return df[f"{result_type.capitalize()} {variable.capitalize()}"]

    return df


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

        self._data, self._meta, self._variables = process_zzn_or_zzx(self._filepath)

    def to_dataframe(
        self,
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
        multilevel_header: bool = True,
    ) -> pd.Series | pd.DataFrame:
        """Loads results to pandas dataframe object.

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
        result_type = result_type.lower()

        if result_type == "all":
            return get_all(self._data, self._meta, self._variables, variable, multilevel_header)

        if result_type in ("max", "min"):
            return get_extremes(self._data, self._meta, result_type, variable, include_time)

        msg = f'Result type: "{result_type}" not recognised'
        raise ValueError(msg)

    def export_to_csv(
        self,
        save_location: str | Path = "default",
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
    ) -> None:
        """Exports results to CSV file.

        Args:
            save_location (str, optional): {default} | folder or file path
                Full or relative path to folder or csv file to save output csv, if no argument given or if set to 'default' then CSV will be saved in same location as ZZN file. Defaults to 'default'.
            result_type (str, optional): {all} | max | min
                Define whether to output all timesteps or just max/min results. Defaults to 'all'.
            variable (str, optional): {'all'} | 'Flow' | 'Stage' | 'Froude' | 'Velocity' | 'Mode' | 'State'
                Specify a single output variable (e.g 'flow' or 'stage'). Defaults to 'all'.
            include_time (bool, optional):
                Whether to include the time of max or min results. Defaults to False.

        Raises:
            Exception: Raised if result_type set to invalid option
        """
        if save_location == "default":
            save_location = Path(self._meta["zzn_name"]).with_suffix(".csv")  # FIXME
        else:
            save_location = Path(save_location)
            if not save_location.is_absolute():
                # for if relative folder path given
                save_location = Path(Path(self._meta["zzn_name"]).parent, save_location)  # FIXME

        if save_location.suffix != ".csv":  # Assumed to be pointing to a folder
            # Check if the folder exists, if not create it
            if not save_location.exists():
                Path.mkdir(save_location)
            save_location = Path(
                save_location,
                Path(self._meta["zzn_name"]).with_suffix(".csv").name,  # FIXME
            )

        elif not save_location.parent.exists():
            Path.mkdir(save_location.parent)

        result_type = result_type.lower()

        if result_type.lower() not in ["all", "max", "min"]:
            msg = f" '{result_type}' is not a valid result type. Valid arguments are: 'all', 'max' or 'min' "
            raise Exception(msg)

        df = self.to_dataframe(
            result_type=result_type,
            variable=variable,
            include_time=include_time,
        )
        df.to_csv(save_location)
        print(f"CSV saved to {save_location}")

    def to_json(
        self,
        result_type: str = "all",
        variable: str = "all",
        include_time: bool = False,
        multilevel_header: bool = True,
    ) -> str:
        """Loads results to JSON object.

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
        df = self.to_dataframe(result_type, variable, include_time, multilevel_header)
        return to_json(df)

    @classmethod
    def from_json(cls, json_string: str = ""):
        # Not possible
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


class ZZX(_ZZ):
    """Reads and processes Flood Modeller 1D binary results format '.zzx'

    Args:
        zzx_filepath (str): Full filepath to model zzx file

    Output:
        Initiates 'ZZX' class object
    """

    _filetype: str = "ZZX"
    _suffix: str = ".zzx"
