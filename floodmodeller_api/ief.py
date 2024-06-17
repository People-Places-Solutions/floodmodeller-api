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

import os
import subprocess
import time
from pathlib import Path
from subprocess import Popen
from typing import Callable

import pandas as pd
from tqdm import trange

from ._base import FMFile
from .ief_flags import flags
from .logs import LF1, create_lf
from .util import handle_exception
from .zzn import ZZN


class IEF(FMFile):
    """Reads and write Flood Modeller event file format '.ief'

    Args:
        ief_filepath (str, optional): Full filepath to ief file. If not specified, a new IEF class will be created.. Defaults to None.

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
            self._log_path = self._get_result_filepath("lf1")
        else:
            self._create_from_blank()

    def _read(self):
        # Read IEF data
        with open(self._filepath) as ief_file:
            raw_data = [line.rstrip("\n") for line in ief_file.readlines()]
        # Clean data and add as class properties
        # Create a list to store the properties which are to be saved in IEF, so as to ignore any temp properties.
        prev_comment = None
        self._ief_properties = []
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
                    if hasattr(self, "EventData"):
                        # Append event data to list so multiple can be specified
                        self.EventData[event_data_title] = value
                    else:
                        self.EventData = {event_data_title: value}
                    self._ief_properties.append("EventData")

                else:
                    # Sets the property and value as class properties so they can be edited.
                    setattr(self, prop, value)
                    self._ief_properties.append(prop)
                prev_comment = None
            else:
                # This should add the [] bound headers
                self._ief_properties.append(line)
                prev_comment = None
        del raw_data

    @handle_exception(when="write")
    def _write(self) -> str:
        """Returns string representation of the current IEF data

        Returns:
            str: Full string representation of IEF in its most recent state (including changes not yet saved to disk)
        """
        # update _ief_properties
        self._update_ief_properties()

        ief_string = ""
        event = 0  # Used as a counter for multiple eventdata files
        for idx, prop in enumerate(self._ief_properties):
            if prop.startswith("["):
                # writes the [] bound headers to ief string
                ief_string += prop + "\n"
            elif prop.lstrip().startswith(";"):
                if self._ief_properties[idx + 1].lower() != "eventdata":
                    # Only write comment if not preceding event data
                    ief_string += prop + "\n"
            elif prop.lower() == "eventdata":
                event_data = getattr(self, prop)
                # Add multiple EventData if present
                for event_idx, key in enumerate(event_data):
                    if event_idx == event:
                        ief_string += f";{key}\n{prop}={str(event_data[key])}\n"
                        break
                event += 1

            else:
                # writes property and value to ief string
                ief_string += f"{prop}={str(getattr(self, prop))}\n"
        return ief_string

    def _create_from_blank(self):
        # No filepath specified, create new 'blank' IEF in memory
        blank_ief = [
            "[ISIS Event Header]",
            'Title=""',
            'Datafile=""',
            'Results=""',
            "[ISIS Event Details]",
            "RunType=Steady",
            "Start=0",
            "ICsFrom=1",
        ]

        # Create a list to store the properties which are to be saved in IEF, so as to ignore any temp properties.
        self._ief_properties = []
        for line in blank_ief:
            if "=" in line:
                prop, value = line.split("=")
                # Sets the property and value as class properties so they can be edited.
                setattr(self, prop, value)
                self._ief_properties.append(prop)
            else:
                # This should add the [] bound headers
                self._ief_properties.append(line)
        del blank_ief

    def _update_ief_properties(self):  # noqa: C901
        """Updates the list of properties included in the IEF file"""
        # Add new properties
        for prop, val in self.__dict__.copy().items():
            if (prop not in self._ief_properties) and (not prop.startswith("_")) and prop != "file":
                # Check if valid flag
                if prop.upper() not in flags:
                    print(
                        f"Warning: '{prop}' is not a valid IEF flag, it will be ommited from the IEF\n",
                    )
                    continue

                if prop.upper() == "EVENTDATA" and prop != "EventData":
                    # (1) This will be triggered in special case where eventdata has been added with different case, but case
                    # needs to be kept as 'EventData', to allow dealing wiht multiple IEDs
                    # (2) In case of EventData being added with correct case where it doesn't already
                    # exist, this stops it being deleted
                    # Add new values to EventData flag
                    delattr(self, prop)
                    self.EventData = val
                    prop = "EventData"

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
        if "[Flow Time Profiles]" in self._ief_properties:
            self._update_flowtimeprofile_info()

        # Ensure number of EventData entries is equal to length of EventData attribute
        if hasattr(self, "EventData"):
            self._update_eventdata_info()

    def _update_eventdata_info(self):  # noqa: C901
        if not isinstance(self.EventData, dict):
            # If attribute not a dict, adds the value as a single entry in list
            raise AttributeError(
                "The 'EventData' attribute should be a dictionary with keys defining the event"
                " names and values referencing the IED files",
            )

        # Number of 'EventData' flags in ief
        event_properties = self._ief_properties.count("EventData")
        # Number of event data specified in class
        events = len(self.EventData)
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

    def _update_flowtimeprofile_info(self):
        end_index = None
        start_index = self._ief_properties.index("[Flow Time Profiles]")
        for idx, item in enumerate(self._ief_properties[start_index:]):
            if idx != 0 and item.startswith("["):
                end_index = idx + start_index
                break
        flow_time_list = self._ief_properties[start_index:end_index]
        flow_time_list = [
            "[Flow Time Profiles]",
            "NoOfFlowTimeProfiles",
            "NoOfFlowTimeSeries",
        ] + [i for i in flow_time_list if i.lower().startswith("flowtimeprofile")]

        # sort list to ensure the flow time profiles are in order
        def flow_sort(itm):
            try:
                num = int(itm.upper().replace("FLOWTIMEPROFILE", ""))
                return (1, num)
            except ValueError:
                return (0, itm)

        flow_time_list[3:] = sorted(flow_time_list[3:], key=flow_sort)

        # Replace existing slice of ief properties with new reordered slice
        self._ief_properties[start_index:end_index] = flow_time_list

        # Update NoOfFlowTimeSeries
        self.NoOfFlowTimeProfiles = str(len(flow_time_list[3:]))

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
            raise UserWarning(
                "IEF must be saved to a specific filepath before simulate() can be called.",
            )
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
                raise Exception(
                    f"Flood Modeller non-default engine path not found! {str(_enginespath)}",
                )

        if precision.upper() == "SINGLE":
            isis32_fp = str(Path(_enginespath, "ISISf32.exe"))
        else:
            isis32_fp = str(Path(_enginespath, "ISISf32_DoubleP.exe"))

        if not Path(isis32_fp).exists():
            raise Exception(f"Flood Modeller engine not found! Expected location: {isis32_fp}")

        run_command = f'"{isis32_fp}" -sd "{self._filepath}"'

        if method.upper() == "WAIT":
            print("Executing simulation...")
            # execute simulation
            process = Popen(run_command, cwd=os.path.dirname(self._filepath))

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
            print(summary)

        elif method.upper() == "RETURN_PROCESS":
            print("Executing simulation...")
            # execute simulation
            return Popen(run_command, cwd=os.path.dirname(self._filepath))

        return None

    def _get_result_filepath(self, suffix):
        if hasattr(self, "Results") and self.Results != '""':  # because blank IEF has 'Results=""'
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
            raise FileNotFoundError("Simulation results file (zzn) not found")

        return ZZN(result_path)

    def get_log(self):
        """If log files for the simulation exist, this function returns them as a LF1 class object

        Returns:
            floodmodeller_api.LF1 class object
        """

        if not self._log_path.exists():
            raise FileNotFoundError("Log file (LF1) not found")

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
            raise FileNotFoundError("Simulation results error log (.exy) not found")

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
