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

import csv
import logging
import re
import subprocess
import time
from io import StringIO
from pathlib import Path
from subprocess import Popen
from typing import Callable

import pandas as pd
from tqdm import trange

from ._base import FMFile
from .diff import check_item_with_dataframe_equal
from .ief_flags import flags
from .logs import LF1, create_lf
from .to_from_json import Jsonable
from .util import handle_exception, is_windows
from .zz import ZZN


def try_converting(value: str) -> str | int | float:
    """Attempt to parse value as float or int if valid, else return the original string"""
    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if not is_windows() and "\\" in value:
        # backslashes aren't valid in paths
        logging.info("Changing '\\' in '%s' to '/' to be valid in Linux.", value)
        return value.replace("\\", "/")

    return value


class IEF(FMFile):
    """Reads and write Flood Modeller event file format '.ief'

    Args:
        ief_filepath (str, optional): Full filepath to ief file. If not specified, a new IEF class
            will be created.. Defaults to None.

    Raises:
        TypeError: Raised if ief_filepath not pointing to valide IEF file
        FileNotFoundError: Raised if ief_filepath points to a non-existent location

    Output:
        Initiates 'IEF' class object
    """

    _filetype: str = "IEF"
    _suffix: str = ".ief"
    ERROR_MAX = 2000
    WARNING_MAX = 3000

    @handle_exception(when="read")
    def __init__(self, ief_filepath: str | Path | None = None, from_json: bool = False):
        if from_json:
            return
        if ief_filepath is not None:
            FMFile.__init__(self, ief_filepath)
            self._read()
            self._log_path = self._filepath.with_suffix(".lf1")
        else:
            self._create_from_blank()

    def _read(self):
        # Read IEF data
        with open(self._filepath, encoding=self.ENCODING) as ief_file:
            raw_data = [line.rstrip("\n") for line in ief_file]
        # Clean data and add as class properties
        # Create a list to store the properties which are to be saved in IEF, so as to ignore any temp properties.
        prev_comment = None
        self._ief_properties: list[str] = []
        self.EventData: dict[str, str] = {}
        self.flowtimeprofiles: list[FlowTimeProfile] = []

        raw_eventdata: list[tuple[str, str]] = []
        for line in raw_data:
            # Handle any comments here (prefixed with ;)
            if line.lstrip().startswith(";"):
                self._ief_properties.append(line)  # Add comment in raw state
                prev_comment = line.strip(";")

            elif "=" in line:
                # Using strip() method to remove any leading/trailing whitespace
                prop, value = (itm.strip() for itm in line.split("=", 1))
                # Handle 'EventData' properties so that multiple can be set
                if prop.upper() == "EVENTDATA":
                    if prev_comment is None:
                        try:
                            event_data_title = Path(value).stem
                        except Exception:
                            event_data_title = value
                    else:
                        event_data_title = prev_comment
                    raw_eventdata.append((event_data_title, value))
                    self._ief_properties.append("EventData")

                elif prop.upper().startswith("FLOWTIMEPROFILE"):
                    self.flowtimeprofiles.append(
                        FlowTimeProfile(value, ief_filepath=self._filepath),
                    )
                    self._ief_properties.append(prop)
                else:
                    # Sets the property and value as class properties so they can be edited.
                    setattr(self, prop, try_converting(value))
                    self._ief_properties.append(prop)
                prev_comment = None
            else:
                # This should add the [] bound headers
                self._ief_properties.append(line)
                prev_comment = None

        self._eventdata_read_helper(raw_eventdata)
        self._check_formatting(raw_data)
        self._update_ief_properties()  # call this here to ensure ief properties is correct

    def _check_formatting(self, raw_data: list[str]) -> None:
        """Check to see if ief formatted with line breaks between groups and spaces around '='."""
        self._format_group_line_breaks = False
        self._format_equals_spaced = False
        if "" in raw_data[:-1]:
            self._format_group_line_breaks = True
        if any(" = " in line for line in raw_data):
            self._format_equals_spaced = True

    @handle_exception(when="write")
    def _write(self) -> str:
        """Returns string representation of the current IEF data

        Returns:
            str: Full string representation of IEF in its most recent state (including changes not yet saved to disk)
        """
        # update _ief_properties
        self._update_ief_properties()

        ief_string = ""
        event_index = 0  # Used as a counter for multiple eventdata files
        ftp_index = 0  # Counter for flowtimeprofiles
        eq = " = " if self._format_equals_spaced else "="
        section_newline = "\n" if self._format_group_line_breaks else ""
        for idx, prop in enumerate(self._ief_properties):
            if prop.startswith("["):
                # writes the [] bound headers to ief string
                if idx > 0:
                    ief_string += section_newline + prop + "\n"
                else:
                    ief_string += prop + "\n"

            elif prop.lstrip().startswith(";"):
                if self._ief_properties[idx + 1].lower() != "eventdata":
                    # Only write comment if not preceding event data
                    ief_string += prop + "\n"

            elif prop.lower() == "eventdata":
                event_data = getattr(self, prop)
                # Add multiple EventData if present
                for idx, key in enumerate(event_data):
                    if idx == event_index:
                        # we enter this block if we're ready to write the event data
                        # scrub off any extra bits we've added as part of the make-unique bit of reading.
                        title = re.sub(r"<\d>$", "", key)
                        ief_string += f";{title}\nEventData{eq}{event_data[key]!s}\n"
                        break
                event_index += 1

            elif prop.lower().startswith("flowtimeprofile"):
                flowtimeprofile = self.flowtimeprofiles[ftp_index]
                ief_string += f"{prop}{eq}{flowtimeprofile}\n"
                ftp_index += 1

            else:
                # writes property and value to ief string
                ief_string += f"{prop}{eq}{getattr(self, prop)!s}\n"

        return ief_string

    def _create_from_blank(self):
        # No filepath specified, create new 'blank' IEF in memory
        blank_ief = [
            "[ISIS Event Header]",
            "Title=",
            "Datafile=",
            "Results=",
            "[ISIS Event Details]",
            "RunType=Steady",
            "Start=0",
            "ICsFrom=1",
        ]

        # Create a list to store the properties which are to be saved in IEF, so as to ignore any temp properties.
        self._filepath = None
        self._ief_properties = []
        self._format_group_line_breaks = False
        self._format_equals_spaced = False
        self.EventData: dict[str, str] = {}
        self.flowtimeprofiles: list[FlowTimeProfile] = []
        for line in blank_ief:
            if "=" in line:
                prop, value = line.split("=")
                # Sets the property and value as class properties so they can be edited.
                setattr(self, prop, try_converting(value))
                self._ief_properties.append(prop)
            else:
                # This should add the [] bound headers
                self._ief_properties.append(line)
        del blank_ief

    def _update_ief_properties(self):
        """Updates the list of properties included in the IEF file"""
        # Add new properties
        for prop, val in self.__dict__.copy().items():
            if (
                (prop not in self._ief_properties)
                and (not prop.startswith("_"))
                and prop not in ["file", "flowtimeprofiles"]
            ):
                # Check if valid flag
                if prop.upper() not in flags:
                    logging.warning(
                        "'%s' is not a valid IEF flag, it will be ommited from the IEF\n",
                        prop,
                    )
                    continue

                if prop.upper() == "EVENTDATA" and prop != "EventData":
                    # (1) This will be triggered in special case where eventdata has been added with different case, but case
                    # needs to be kept as 'EventData', to allow dealing wiht multiple IEDs
                    # (2) In case of EventData being added with correct case where it doesn't already
                    # exist, this stops it being deleted
                    # Add new values to EventData flag
                    delattr(self, prop)
                    self.eventdata = val
                    prop = "eventdata"

                # Check ief group header
                group = f"[{flags[prop.upper()]}]"
                if group in self._ief_properties:
                    # If group already exists, add property to end of group
                    group_idx = False
                    # defaults to inserting in last place
                    insert_index = len(self._ief_properties)
                    for idx, item in enumerate(self._ief_properties):
                        if group_idx is True and item.startswith("["):
                            insert_index = idx
                            break
                        if item == group:
                            group_idx = True

                    self._ief_properties.insert(insert_index, prop)
                else:
                    # Add group header to the end of list
                    self._ief_properties.append(group)
                    # Add property to end of list
                    self._ief_properties.append(prop)

        # Remove any deleted properties
        self._ief_properties = [
            line
            for line in self._ief_properties
            if (line.startswith("[") or (line in dir(self)) or line.lstrip().startswith(";"))
        ]

        # Rearrange order of Flow Time Profiles group if present * Currently assuming all relevent flags included
        self._update_flowtimeprofile_info()

        # Ensure number of EventData entries is equal to length of EventData attribute
        self._update_eventdata_info()

    def _update_eventdata_info(self):  # noqa: C901
        if not isinstance(self.eventdata, dict):
            # If attribute not a dict, adds the value as a single entry in list
            msg = (
                "The 'EventData' attribute should be a dictionary with keys defining the event"
                " names and values referencing the IED files"
            )
            raise AttributeError(msg)

        # Number of 'EventData' flags in ief
        event_properties = self._ief_properties.count("EventData")
        # Number of event data specified in class
        events = len(self.eventdata)
        if event_properties < events:
            # Need to add additional event properties to IEF to match number of events specified
            to_add = events - event_properties
            # Used for if no existing eventdata exists
            insert_index = len(self._ief_properties)
            for idx, itm in enumerate(reversed(self._ief_properties)):
                if itm in ("EventData", "[ISIS Event Details]"):
                    insert_index = len(self._ief_properties) - idx
                    break

            for _ in range(to_add):
                # Add in required number of extra EventData after last one.
                self._ief_properties.insert(insert_index, "EventData")

        elif event_properties > events:
            # Need to remove some event properties from IEF to match number of events specified
            to_remove = event_properties - events
            removed = 0  # Counter for number removed
            num_props = len(self._ief_properties)
            for idx, itm in enumerate(reversed(self._ief_properties)):
                if itm == "EventData":
                    del self._ief_properties[num_props - 1 - idx]
                    # Also remove event data title comment if present
                    if self._ief_properties[num_props - 2 - idx].lstrip().startswith(";"):
                        del self._ief_properties[num_props - 2 - idx]
                    removed += 1
                    if removed == to_remove:
                        break

    def _eventdata_read_helper(self, raw_eventdata: list[tuple[str, str]]) -> None:
        # now we deal with the event data, and convert it into the dict-based .eventdata
        for title, ied_path in raw_eventdata:
            n = 0
            new_title = title or "<0>"  # set empty string to placeholder
            while new_title in self.eventdata:
                new_title = f"{title}<{n}>"
                n += 1
            self.eventdata[new_title] = ied_path

    def _update_flowtimeprofile_info(self) -> None:
        """Update the flowtimeprofile data stored in ief properties"""
        if not hasattr(self, "flowtimeprofiles") or len(self.flowtimeprofiles) == 0:
            self._remove_flowtimeprofile_info()
            return

        # Update properties
        self.NoOfFlowTimeProfiles = len(self.flowtimeprofiles)
        try:
            self.NoOfFlowTimeSeries = sum([ftp.count_series() for ftp in self.flowtimeprofiles])
        except FileNotFoundError as err:
            msg = (
                "Failed to read csv referenced in flowtimeprofile, file either does not exist or is"
                "unable to be found due to relative path from IEF file. NoOfFlowTimeSeries has not"
                "been updated."
            )
            raise UserWarning(msg) from err

        end_index = None
        start_index = (
            self._ief_properties.index("[Flow Time Profiles]")
            if "[Flow Time Profiles]" in self._ief_properties
            else len(self._ief_properties)
        )
        for idx, item in enumerate(self._ief_properties[start_index:]):
            if idx != 0 and item.startswith("["):
                end_index = idx + start_index
                break

        flowtimeprofile_list = [
            "[Flow Time Profiles]",
            "NoOfFlowTimeProfiles",
            "NoOfFlowTimeSeries",
        ]
        for idx, _ in enumerate(self.flowtimeprofiles):
            flowtimeprofile_list.append(f"FlowTimeProfile{idx}")

        # Replace existing slice of ief properties with new slice
        self._ief_properties[start_index:end_index] = flowtimeprofile_list

    def _remove_flowtimeprofile_info(self) -> None:
        """Delete flowtimeprofile data from ief properties and any attributes present"""
        # Remove flowtimeprofile info from IEF properties
        self._ief_properties = [
            line
            for line in self._ief_properties
            if (
                line.lower()
                not in [
                    "[flow time profiles]",
                    "noofflowtimeprofiles",
                    "noofflowtimeseries",
                ]
            )
            and (not line.lower().startswith("flowtimeprofile"))
        ]
        if hasattr(self, "noofflowtimeprofiles"):
            del self.NoOfFlowTimeProfiles
        if hasattr(self, "noofflowtimeseries"):
            del self.NoOfFlowTimeSeries

        self.flowtimeprofiles = []

    def __getattr__(self, name):
        for attr in self.__dict__.copy():
            if name.lower() == attr.lower():
                return self.__dict__[attr]
        return self.__getattribute__(name)

    def __setattr__(self, name, value):
        existing_attr_updated = False
        for attr in self.__dict__.copy():
            if name.lower() == attr.lower():
                self.__dict__[attr] = value
                existing_attr_updated = True

        if not existing_attr_updated:
            self.__dict__[name] = value

    def __delattr__(self, name):
        existing_attr_deleted = False
        for attr in self.__dict__.copy():
            if name.lower() == attr.lower():
                super().__delattr__(attr)
                existing_attr_deleted = True

        if not existing_attr_deleted:
            super().__delattr__(name)

    def diff(self, other: IEF, force_print: bool = False) -> None:
        """Compares the IEF class against another IEF class to check whether they are
        equivalent, or if not, what the differences are. Two instances of an IEF class are
        deemed equivalent if all of their attributes are equal except for the filepath and
        raw data.

        The result is printed to the console. If you need to access the returned data, use
        the method ``IEF._get_diff()``

        Args:
            other (floodmodeller_api.IEF): Other instance of an IEF class
            force_print (bool): Forces the API to print every difference found, rather than
                just the first 25 differences. Defaults to False.
        """
        self._diff(other, force_print=force_print)

    def update(self) -> None:
        """Updates the existing IEF based on any altered attributes"""
        self._update()

    def save(self, filepath: str | Path) -> None:
        """Saves the IEF to the given location, if pointing to an existing file it will be overwritten.
        Once saved, the IEF() class will continue working from the saved location, therefore any further calls to IEF.update() will update in the latest saved location
        rather than the original source IEF used to construct the class

        Args:
            filepath (string): Full filepath to new location for ief file (including '.ief' extension)
        """
        self._save(filepath)
        self._log_path = self._filepath.with_suffix(".lf1")

    @handle_exception(when="simulate")
    def simulate(  # noqa: C901, PLR0912, PLR0913
        self,
        method: str = "WAIT",
        raise_on_failure: bool = True,
        precision: str = "DEFAULT",
        enginespath: str = "",
        range_function: Callable = trange,
        range_settings: dict | None = None,
    ) -> subprocess.Popen | None:
        """Simulate the IEF file directly as a subprocess

        Args:
            method (str, optional): {'WAIT'} | 'RETURN_PROCESS'
                'WAIT' - The function waits for the simulation to complete before continuing (This is default)
                'RETURN_PROCESS' - The function sets the simulation running in background and immediately continues, whilst returning the process object.
                Defaults to 'WAIT'.
            raise_on_failure (bool, optional): If True, an exception will be raised if the simulation fails to complete without errors.
                If set to False, then the script will continue to run even if the simulation fails. If 'method' is set to 'RETURN_PROCESS'
                then this argument is ignored. Defaults to True.
            precision (str, optional): {'DEFAULT'} | 'SINGLE' | 'DOUBLE'
                Define which engine to use for simulation, if set to 'DEFAULT' it will use the precision specified in the IEF. Alternatively,
                this can be overwritten using 'SINGLE' or 'DOUBLE'.
            enginespath (str, optional): {''} | '/absolute/path/to/engine/executables'
                Define where the engine executables are located. This replaces the default location (usual installation folder) if set to
                anything other than ''.

        Raises:
            UserWarning: Raised if ief filepath not already specified

        Returns:
            subprocess.Popen(): If method == 'RETURN_PROCESS', the Popen() instance of the process is returned.
        """
        self._range_function = range_function
        self._range_settings = range_settings if range_settings else {}
        if self._filepath is None:
            msg = "IEF must be saved to a specific filepath before simulate() can be called."
            raise UserWarning(msg)
        if precision.upper() == "DEFAULT":
            precision = "SINGLE"  # Defaults to single...
            for attr in dir(self):
                if (
                    attr.upper() == "LAUNCHDOUBLEPRECISIONVERSION"  # Unless DP specified
                    and int(getattr(self, attr)) == 1
                ):
                    precision = "DOUBLE"
                    break

        if enginespath == "":
            _enginespath = r"C:\Program Files\Flood Modeller\bin"  # Default location
        else:
            _enginespath = enginespath
            if not Path(_enginespath).exists():
                msg = f"Flood Modeller non-default engine path not found! {_enginespath!s}"
                raise Exception(msg)

        if precision.upper() == "SINGLE":
            isis32_fp = str(Path(_enginespath, "ISISf32.exe"))
        else:
            isis32_fp = str(Path(_enginespath, "ISISf32_DoubleP.exe"))

        if not Path(isis32_fp).exists():
            msg = f"Flood Modeller engine not found! Expected location: {isis32_fp}"
            raise Exception(msg)

        run_command = f'"{isis32_fp}" -sd "{self._filepath.resolve()}"'

        if method.upper() == "WAIT":
            logging.info("Executing simulation...")
            # execute simulation
            process = Popen(run_command, cwd=Path(self._filepath).parent)

            # progress bar based on log files
            steady = self.RunType == "Steady"
            self._lf = create_lf(self._log_path, "lf1") if not steady else None
            self._update_progress_bar(process)

            while process.poll() is None:
                # Process still running
                time.sleep(1)

            result, summary = self._summarise_exy()

            if result == 1 and raise_on_failure:
                raise RuntimeError(summary)
            logging.info(summary)

        elif method.upper() == "RETURN_PROCESS":
            logging.info("Executing simulation...")
            # execute simulation
            return Popen(run_command, cwd=Path(self._filepath).parent)

        return None

    def _get_result_filepath(self, suffix):
        if hasattr(self, "Results") and self.Results != "":
            path = Path(self.Results).with_suffix("." + suffix)
            if not path.is_absolute():
                # set cwd to ief location and resolve path
                path = Path(self._filepath.parent, path).resolve()

        else:
            path = self._filepath.with_suffix("." + suffix)

        return path

    def get_results(self) -> ZZN:
        """If results for the simulation exist, this function returns them as a ZZN class object

        Returns:
            floodmodeller_api.ZZN class object
        """

        # Get zzn location
        result_path = self._get_result_filepath(suffix="zzn")

        if not result_path.exists():
            msg = "Simulation results file (zzn) not found"
            raise FileNotFoundError(msg)

        return ZZN(result_path)

    def get_log(self) -> LF1:
        """If log files for the simulation exist, this function returns them as a LF1 class object

        Returns:
            floodmodeller_api.LF1 class object
        """

        if not self._log_path.exists():
            msg = "Log file (LF1) not found"
            raise FileNotFoundError(msg)

        steady = self.RunType == "Steady"
        return LF1(self._log_path, steady)

    def _update_progress_bar(self, process: Popen):
        """Updates progress bar based on log file"""

        # only if there is a log file
        if self._lf is None:
            return

        # tqdm progress bar
        for i in self._range_function(100, **self._range_settings):
            # Process still running
            while process.poll() is None:
                time.sleep(0.1)

                # Find progress
                self._lf.read(suppress_final_step=True)
                progress = self._lf.report_progress()

                # Reached i% progress => move onto waiting for (i+1)%
                if progress > i:
                    break

            # Process stopped
            if process.poll() is not None:
                # Find final progress
                self._lf.read(suppress_final_step=True)
                progress = self._lf.report_progress()

                if progress > i:
                    pass  # stopped because it completed
                else:
                    break  # stopped for another reason

    def _summarise_exy(self):
        """Reads and summarises associated exy file if available"""

        # Get results location
        if hasattr(self, "Results"):
            exy_path = Path(self.Results).with_suffix(".exy")
            if not exy_path.is_absolute():
                # set cwd to ief location and resolve path
                exy_path = Path(self._filepath.parent, exy_path).resolve()

        else:
            exy_path = self._filepath.with_suffix(".exy")

        if not exy_path.exists():
            msg = "Simulation results error log (.exy) not found"
            raise FileNotFoundError(msg)

        exy_data = pd.read_csv(exy_path, names=["node", "timestep", "severity", "code", "summary"])
        exy_data["type"] = exy_data["code"].apply(
            lambda x: (
                "Error" if x < self.ERROR_MAX else ("Warning" if x < self.WARNING_MAX else "Note")
            ),
        )
        errors = len(exy_data[exy_data["type"] == "Error"])
        warnings = len(exy_data[exy_data["type"] == "Warning"])
        notes = len(exy_data[exy_data["type"] == "Note"])

        details = f"({errors} Error(s), {warnings} Warning(s), {notes} Note(s) ) - Check ZZD for more details."

        if errors > 0:
            return 1, f"Simulation Failed! - {details}"

        return 0, f"Simulation Completed! - {details}"


class FlowTimeProfile(Jsonable):
    """Handles defining and formatting flow time profiles in IEF files

    Args:
        raw_string (Optional[str]): A raw CSV-formatted string to initialize the profile attributes.

    Keyword Args:
        labels (list[str]): A list of string labels for the profile headers.
        columns (list[int]): A list of integers (1-indexed) for the column indices of the profile.
        start_row (int): The starting row index (1-indexed) for reading data from the CSV.
        csv_filepath (str): The file path to the CSV file containing flow data.
        file_type (str): The type of the file format, e.g. fm1, fm2, hplus, refh2.
        profile (str): A description or identifier for the profile.
        comment (str): An optional comment or note related to the profile.
        ief_filepath (str): The base directory path for resolving the CSV file.

    Raises:
        ValueError: If neither a `raw_string` nor keyword arguments are provided.
    """

    labels: list[str]
    columns: list[int]
    start_row: int
    csv_filepath: str
    file_type: str
    profile: str
    comment: str

    def __init__(self, raw_string: str | None = None, **kwargs) -> None:
        """Initializes the FlowTimeProfile instance from either a raw string or keyword arguments."""
        if raw_string is not None:
            self._parse_raw_string(raw_string)

        elif kwargs:
            self.labels = kwargs.get("labels", [])
            self.columns = kwargs.get("columns", [])
            self.start_row = kwargs.get("start_row", 0)
            self.csv_filepath = kwargs.get("csv_filepath", "")
            self.file_type = kwargs.get("file_type", "")
            self.profile = kwargs.get("profile", "")
            self.comment = kwargs.get("comment", "")
        else:
            msg = "You must provide either a single raw string argument or keyword arguments."
            raise ValueError(msg)

        base_path = Path(kwargs.get("ief_filepath", ""))
        self._csvfile = (base_path / self.csv_filepath.strip('"')).resolve()

        for attr in ["csv_filepath", "comment"]:
            value = getattr(self, attr)
            if "," in value:
                # Ensure string wrapped in quotes if containing comma
                setattr(self, attr, f'"{value}"'.replace('""', '"'))

    def _parse_raw_string(self, raw_string: str) -> None:
        """Parses a raw string of comma separated values and stores as attributes"""
        csv_reader = csv.reader(StringIO(raw_string), skipinitialspace=True, quotechar='"')
        parts = next(csv_reader)  # Read the first (and only) line as a list of fields
        self.labels = [label for label in parts[0].split(" ") if label != ""]
        self.columns = [int(col) for col in parts[1].split(" ") if col != ""]
        self.start_row = int(parts[2])
        self.csv_filepath = parts[3]
        self.file_type = parts[4]
        self.profile, self.comment = (parts[5:] + ["", ""])[:2]

    def __str__(self) -> str:
        """Converts the flow time profile into a valid comma separated ief string"""
        return (
            f"{' '.join(self.labels)},{' '.join(map(str, self.columns))},{self.start_row},"
            f"{self.csv_filepath},{self.file_type},{self.profile},{self.comment}"
        )

    def __repr__(self) -> str:
        return (
            f"<floodmodeller_api FlowTimeProfile(\n\tlabels={self.labels},\n\t"
            f"columns={self.columns},\n\tstart_row={self.start_row},\n\t"
            f"csv_filepath={self.csv_filepath},\n\tfile_type={self.file_type},\n\t"
            f"profile={self.profile},\n\tcomment={self.comment}\n)>"
        )

    def __eq__(self, other, return_diff=False):
        result = True
        diff = []
        result, diff = check_item_with_dataframe_equal(
            {key: value for key, value in self.__dict__.items() if key != "_csvfile"},
            {key: value for key, value in other.__dict__.items() if key != "_csvfile"},
            name="FlowTimeProfile",
            diff=diff,
        )
        return (result, diff) if return_diff else result

    def count_series(self) -> int:
        if self.file_type.lower() == "fm1":
            # read csv and count series
            return len(pd.read_csv(self._csvfile, skiprows=self.start_row - 1, index_col=0).columns)

        return len(self.columns)
