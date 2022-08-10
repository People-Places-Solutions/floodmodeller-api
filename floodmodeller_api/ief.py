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

import os
import subprocess
import time
from pathlib import Path
from subprocess import Popen
from typing import Optional, Union

import pandas as pd

from ._base import FMFile
from .ief_flags import flags
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

    def __init__(self, ief_filepath: Optional[Union[str, Path]] = None):
        try:
            self._filepath = ief_filepath
            if self._filepath != None:
                FMFile.__init__(self)

                self._read()

            else:
                self._create_from_blank()
        except Exception as e:
            self._handle_exception(e, when="read")

    def _read(self):
        # Read IEF data
        with open(self._filepath, "r") as ief_file:
            raw_data = [line.rstrip("\n") for line in ief_file.readlines()]
        # Clean data and add as class properties
        # Create a list to store the properties which are to be saved in IEF, so as to ignore any temp properties.
        self._ief_properties = []
        for line in raw_data:
            # Handle any comments here (prefixed with ;)
            if line.lstrip().startswith(";"):
                self._ief_properties.append(line)  # Add comment in raw state

            elif "=" in line:
                # Using strip() method to remove any leading/trailing whitespace
                prop, value = [itm.strip() for itm in line.split("=", 1)]
                # Handle 'EventData' properties so that multiple can be set
                if prop.upper() == "EVENTDATA":
                    if hasattr(self, "EventData"):
                        # Append event data to list so multiple can be specified
                        self.EventData.append(value)
                    else:
                        self.EventData = [value]
                    self._ief_properties.append("EventData")
                else:
                    # Sets the property and value as class properties so they can be edited.
                    setattr(self, prop, value)
                    self._ief_properties.append(prop)
            else:
                # This should add the [] bound headers
                self._ief_properties.append(line)
        del raw_data

    def _write(self) -> str:
        """Returns string representation of the current IEF data

        Returns:
            str: Full string representation of IEF in its most recent state (including changes not yet saved to disk)
        """
        try:
            # update _ief_properties
            self._update_ief_properties()

            ief_string = ""
            event = 0  # Used as a counter for multiple eventdata files
            for prop in self._ief_properties:
                if prop.startswith("[") or prop.lstrip().startswith(";"):
                    # writes the [] bound headers to ief string or any comment lines
                    ief_string += prop + "\n"
                elif prop == "EventData":
                    event_data = getattr(self, prop)
                    # Add multiple EventData if present
                    ief_string += f"{prop}={str(event_data[event])}\n"
                    event += 1

                else:
                    # writes property and value to ief string
                    ief_string += f"{prop}={str(getattr(self, prop))}\n"
            return ief_string

        except Exception as e:
            self._handle_exception(e, when="write")

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

    def _update_ief_properties(self):
        """Updates the list of properties included in the IEF file"""
        # Add new properties
        for prop, val in self.__dict__.copy().items():
            if (prop not in self._ief_properties) and (not prop.startswith("_")):
                # Check if valid flag
                if prop.upper() not in flags:
                    print(
                        f"Warning: '{prop}' is not a valid IEF flag, it will be ommited from the IEF\n"
                    )
                    continue

                elif prop.upper() == "EVENTDATA":
                    # This will be triggered in special case where eventdata has been added with different case, but case
                    # needs to be kept as 'EventData', to allow dealing wiht multiple IEDs
                    if (
                        not prop == "EventData"
                    ):  # In case of EventData being added with correct case where it doesn't already
                        # exist, this stops it being deleted
                        # Add new values to EventData flag
                        setattr(self, "EventData", val)
                        delattr(self, prop)

                else:
                    # Check ief group header
                    group = f"[{flags[prop.upper()]}]"
                    if group in self._ief_properties:
                        # If group already exists, add property to end of group
                        group_idx = False
                        # defaults to inserting in last place
                        insert_index = len(self._ief_properties)
                        for idx, item in enumerate(self._ief_properties):
                            if group_idx == True and item.startswith("["):
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
            if (
                line.startswith("[")
                or (line in dir(self))
                or line.lstrip().startswith(";")
            )
        ]

        # Rearrange order of Flow Time Profiles group if present * Currently assuming all relevent flags included
        if "[Flow Time Profiles]" in self._ief_properties:
            self._update_flowtimeprofile_info()

        # Ensure number of EventData entries is equal to length of EventData attribute
        if hasattr(self, "EventData"):
            self._update_eventdata_info()

    def _update_eventdata_info(self):
        if not isinstance(self.EventData, list):
            # If attribute not a list, adds the value as a single entry in list
            self.EventData = [self.EventData]

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
                if itm == "EventData" or itm == "[ISIS Event Details]":
                    insert_index = len(self._ief_properties) - idx
                    break

            for i in range(to_add):
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

    def update(self) -> None:
        """Updates the existing IEF based on any altered attributes"""
        self._update()

    def save(self, filepath: Union[str, Path]) -> None:
        """Saves the IEF to the given location, if pointing to an existing file it will be overwritten.
        Once saved, the IEF() class will continue working from the saved location, therefore any further calls to IEF.update() will update in the latest saved location
        rather than the original source IEF used to construct the class

        Args:
            filepath (string): Full filepath to new location for ief file (including '.ief' extension)
        """
        self._save(filepath)

    def simulate(
        self,
        method: Optional[str] = "WAIT",
        raise_on_failure: Optional[bool] = True,
        precision: Optional[str] = "DEFAULT",
        enginespath: Optional[str] = "",
    ) -> Optional[subprocess.Popen]:
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
        try:
            if self._filepath == None:
                raise UserWarning(
                    "IEF must be saved to a specific filepath before simulate() can be called."
                )
            if precision.upper() == "DEFAULT":
                precision = "SINGLE"  # Defaults to single...
                for attr in dir(self):
                    if (
                        attr.upper() == "LAUNCHDOUBLEPRECISIONVERSION"
                    ):  # Unless DP specified
                        if getattr(self, attr) == "1":
                            precision = "DOUBLE"
                            break

            if enginespath == "":
                _enginespath = (
                    r"C:\Program Files\Flood Modeller\bin"  # Default location
                )
            else:
                _enginespath = enginespath
                if not Path(_enginespath).exists:
                    raise Exception(
                        f"Flood Modeller non-default engine path not found! {str(_enginespath)}"
                    )

            if precision.upper() == "SINGLE":
                isis32_fp = str(Path(_enginespath, "ISISf32.exe"))
            else:
                isis32_fp = str(Path(_enginespath, "ISISf32_DoubleP.exe"))

            if not Path(isis32_fp).exists:
                raise Exception(
                    f"Flood Modeller engine not found! Expected location: {isis32_fp}"
                )

            run_command = f'"{isis32_fp}" -sd "{self._filepath}"'

            if method.upper() == "WAIT":
                # Executing simulation...
                print("Executing simulation...")
                process = Popen(
                    run_command, cwd=os.path.dirname(self._filepath)
                )  # execute simulation
                while process.poll() is None:
                    # Process still running
                    time.sleep(1)

                result, summary = self._summarise_exy()

                if result == 1 and raise_on_failure:
                    raise RuntimeError(summary)
                else:
                    print(summary)

            elif method.upper() == "RETURN_PROCESS":
                # Executing simulation...
                print("Executing simulation...")
                process = Popen(
                    run_command, cwd=os.path.dirname(self._filepath)
                )  # execute simulation
                return process

        except Exception as e:
            self._handle_exception(e, when="simulate")

    def get_results(self) -> ZZN:
        """If results for the simulation exist, this function returns them as a ZZN class object

        Returns:
            floodmodeller_api.ZND class object
        """

        # Get results location
        if hasattr(self, "Results"):
            result_path = Path(self.Results).with_suffix(".zzn")
            if not result_path.is_absolute():
                # set cwd to ief location and resolve path
                result_path = Path(self._filepath.parent, result_path).resolve()

        else:
            result_path = self._filepath.with_suffix(".zzn")

        if result_path.exists():
            return ZZN(result_path)

        else:
            raise FileNotFoundError("Simulation results file (zzn) not found")

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

        if exy_path.exists():
            exy_data = pd.read_csv(
                exy_path, names=["node", "timestep", "severity", "code", "summary"]
            )
            exy_data["type"] = exy_data["code"].apply(
                lambda x: "Error" if x < 2000 else ("Warning" if x < 3000 else "Note")
            )
            errors = len(exy_data[exy_data["type"] == "Error"])
            warnings = len(exy_data[exy_data["type"] == "Warning"])
            notes = len(exy_data[exy_data["type"] == "Note"])

            details = f"({errors} Error(s), {warnings} Warning(s), {notes} Note(s) ) - Check ZZD for more details."

            if errors > 0:
                return 1, f"Simulation Failed! - {details}"

            else:
                return 0, f"Simulation Completed! - {details}"

        else:
            raise FileNotFoundError("Simulation results error log (.exy) not found")
