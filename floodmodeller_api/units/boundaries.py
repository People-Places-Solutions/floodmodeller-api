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

import pandas as pd

from floodmodeller_api.validation import _validate_unit
from floodmodeller_api.validation.parameters import parameter_options

from ._base import Unit
from ._helpers import (
    join_10_char,
    join_n_char_ljust,
    split_10_char,
    to_data_list,
    to_float,
    to_str,
)


class QTBDY(Unit):
    """Class to hold and process QTBDY boundary type

    Args:
        name (str, optional): Unit name. Defaults to None.
        comment (str, optional): Comment included in unit. Defaults to None.
        timeoffset (float, optional): Defaults to None.
        timeunit (str, optional): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options. Defaults to None.
        extendmethod (str, optional): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'. Defaults to None.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to None.
        flowmultiplier (float, optional): Multiplier applied to all flow values at runtime. Defaults to None.
        minflow (Float, optional): Minimum flow value applied to the boundary at runtime. Defaults to None.
        data (pandas.Series, optional): Series object with variable ``'Flow'`` and index ``'Time'``. Defaults to None.
        allow_override (str): Allow event parameters to be overridden from simulation file: ''/'OVERRIDE' or 'NOOVERRIDE'

    Returns:
        QTBDY: Flood Modeller QTBDY Unit class object
    """

    _unit = "QTBDY"

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_qtbdy",
        comment="",
        timeoffset=0.0,
        timeunit="HOURS",
        extendmethod="EXTEND",
        interpmethod="LINEAR",
        flowmultiplier=0.0,
        minflow=0.0,
        allow_override="OVERRIDE",
        _something=0.0,
        data=None,
    ):
        # Initiate new QTBDY

        for param, val in {
            "name": name,
            "comment": comment,
            "timeunit": timeunit,
            "extendmethod": extendmethod,
            "interpmethod": interpmethod,
            "timeoffset": timeoffset,
            "flowmultiplier": flowmultiplier,
            "minflow": minflow,
            "allow_override": allow_override,
            "_something": _something,
        }.items():
            setattr(self, param, val)

        self.data = (
            data
            if isinstance(data, pd.Series)
            else pd.Series([0.0, 0.0], index=[0.0, 0.1], name="Flow")
        )

    def _read(self, qtbdy_block):
        """Function to read a given QTBDY block and store data as class attributes"""
        self.name = qtbdy_block[1][: self._label_len].strip()
        self.comment = self._remove_unit_name(qtbdy_block[0])
        qtbdy_params = split_10_char(f"{qtbdy_block[2]:<90}")
        self.nrows = int(qtbdy_params[0])
        self.timeoffset = to_float(qtbdy_params[1])
        self._something = to_float(qtbdy_params[2])
        self.timeunit = to_str(qtbdy_params[3], "HOURS", check_float=True)
        self.extendmethod = to_str(qtbdy_params[4], "EXTEND")
        self.interpmethod = to_str(qtbdy_params[5], "LINEAR")
        self.flowmultiplier = to_float(qtbdy_params[6])
        self.minflow = to_float(qtbdy_params[7])
        self.allow_override = to_str(qtbdy_params[8], "OVERRIDE")  # ''/OVERRIDE or NOOVERRIDE
        data_list = (
            to_data_list(qtbdy_block[3:], date_col=1)
            if self.timeunit == "DATES"
            else to_data_list(qtbdy_block[3:])
        )

        self.data = pd.DataFrame(data_list, columns=["Flow", "Time"])
        self.data = self.data.set_index("Time")
        self.data = self.data["Flow"]  # Convert to series

    def _write(self):
        """Function to write a valid QTBDY block"""
        _validate_unit(self)  # Function to check the params are valid for QTBDY
        header = self._create_header()
        name = self.name[: self._label_len]
        self.nrows = len(self.data)

        qtbdy_params = join_10_char(
            self.nrows,
            float(self.timeoffset),
            float(self._something),
            self.timeunit,
            self.extendmethod,
            self.interpmethod,
            float(self.flowmultiplier),
            float(self.minflow),
            self.allow_override,
        )

        if self.timeunit == "DATES":
            qtbdy_data = [join_10_char(q) + t for t, q in self.data.items()]
        else:
            qtbdy_data = [join_10_char(q, t) for t, q in self.data.items()]
        qtbdy_block = [header, name, qtbdy_params]
        qtbdy_block.extend(qtbdy_data)

        return qtbdy_block


class HTBDY(Unit):
    """Class to hold and process HTBDY boundary type

    Args:
        name (str, optional): Unit name. Defaults to None.
        comment (str, optional): Comment included in unit. Defaults to None.
        timeunit (str, optional): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options. Defaults to None.
        extendmethod (str, optional): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'. Defaults to None.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to None.
        data (pandas.Series, optional): Series object with columns ``'Time'`` and ``'Stage'``. Defaults to None.

    Returns:
        HTBDY: Flood Modeller HTBDY Unit class object
    """

    _unit = "HTBDY"

    def _create_from_blank(  # noqa: PLR0913
        self,
        name="new_htbdy",
        comment="",
        timeunit="HOURS",
        extendmethod="EXTEND",
        interpmethod="LINEAR",
        data=None,
    ):
        # Initiate new HTBDY

        for param, val in {
            "name": name,
            "comment": comment,
            "timeunit": timeunit,
            "extendmethod": extendmethod,
            "interpmethod": interpmethod,
            "_something": "",
        }.items():
            setattr(self, param, val)

        self.data = (
            data
            if isinstance(data, pd.Series)
            else pd.Series([0.0, 0.0], index=[0.0, 0.1], name="Stage")
        )

    def _read(self, htbdy_block):
        """Function to read a given HTBDY block and store data as class attributes"""
        self.name = htbdy_block[1][: self._label_len].strip()
        self.comment = self._remove_unit_name(htbdy_block[0])
        htbdy_params = split_10_char(f"{htbdy_block[2]:<50}")
        self.nrows = int(htbdy_params[0])
        self._something = to_str(htbdy_params[1], "")
        self.timeunit = to_str(htbdy_params[2], "HOURS", check_float=True)
        self.extendmethod = to_str(htbdy_params[3], "EXTEND")
        self.interpmethod = to_str(htbdy_params[4], "LINEAR")

        data_list = (
            to_data_list(htbdy_block[3:], date_col=1)
            if self.timeunit == "DATES"
            else to_data_list(htbdy_block[3:])
        )

        self.data = pd.DataFrame(data_list, columns=["Stage", "Time"])
        self.data = self.data.set_index("Time")
        self.data = self.data["Stage"]  # Convert to series

        # Fix legacy Flood Modeller bug where timeunit is present in extendmethod place
        if self.extendmethod in parameter_options["timeunit"]["options"][1]:
            self.timeunit = self.extendmethod
            self.extendmethod = "EXTEND"

    def _write(self):
        """Function to write a valid HTBDY block"""
        _validate_unit(self)  # Function to check the params are valid for HTBDY
        header = self._create_header()
        name = self.name
        self.nrows = len(self.data)

        htbdy_params = join_10_char(
            self.nrows,
            self._something,
            self.timeunit,
            self.extendmethod,
            self.interpmethod,
        )
        if self.timeunit == "DATES":
            htbdy_data = [join_10_char(h) + t for t, h in self.data.items()]
        else:
            htbdy_data = [join_10_char(h, t) for t, h in self.data.items()]
        htbdy_block = [header, name, htbdy_params]
        htbdy_block.extend(htbdy_data)

        return htbdy_block


class QHBDY(Unit):
    """Class to hold and process QHBDY boundary type

    Args:
        name (str, optional): Unit name. Defaults to None.
        comment (str, optional): Comment included in unit. Defaults to None.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to None.
        data (pandas.Series, optional): Series object with columns ``'Flow'`` and ``'Stage'``. Defaults to None.
    Returns:
        QHBDY: Flood Modeller QHBDY Unit class object
    """

    _unit = "QHBDY"

    def _create_from_blank(self, name="new_qhbdy", comment="", interpmethod="LINEAR", data=None):
        # Initiate new QHBDY
        for param, val in {
            "name": name,
            "comment": comment,
            "interpmethod": interpmethod,
        }.items():
            setattr(self, param, val)
        self.data = (
            data
            if isinstance(data, pd.Series)
            else pd.Series([0.0, 0.0], index=[0.0, 0.1], name="Stage")
        )

    def _read(self, qhbdy_block):
        """Function to read a given QHBDY block and store data as class attributes"""
        self.name = qhbdy_block[1][: self._label_len].strip()
        self.comment = self._remove_unit_name(qhbdy_block[0])
        qhbdy_params = split_10_char(f"{qhbdy_block[2]:<30}")
        self.nrows = int(qhbdy_params[0])
        self.interpmethod = to_str(qhbdy_params[2], "LINEAR")

        data_list = to_data_list(qhbdy_block[3:])

        self.data = pd.DataFrame(data_list, columns=["Flow", "Stage"])
        self.data = self.data.set_index("Stage")
        self.data = self.data["Flow"]  # Convert to series

    def _write(self):
        """Function to write a valid QHBDY block"""
        _validate_unit(self)  # Function to check the params are valid for QHBDY
        header = self._create_header()
        name = self.name
        self.nrows = len(self.data)

        qhbdy_params = join_10_char(self.nrows, 0.000, self.interpmethod)
        qhbdy_data = [f"{q:>10.3f}{h:>10.3f}" for h, q in self.data.items()]
        qhbdy_block = [header, name, qhbdy_params]
        qhbdy_block.extend(qhbdy_data)

        return qhbdy_block


class REFHBDY(Unit):
    """Class to hold and process REFHBDY boundary type

    Currently REFHBDY Units are read/edit only and cannot be created from scratch, therefore the
    parameters below are only accessible upon instantiating a REFHBDY object from an existing
    unit.

    Args:
        name (str): Unit name.
        comment (str): Comment included in unit.
        easting (int): Easting (m)
        northing (int): Northing (m)
        return_period(float): Flood return period (yrs)
        time_delay (float): Time delay before start of hydrograph (hrs)
        timestep (float): Time interval for unit hydrograph and rainfall profile
        sim_type (str): Simulation Type required: 'FULL' (full hydrograph), 'PFONLY' (peak flow) or 'BFONLY' (baseflow)
        scale_method (str): Hydrograph scaling method: 'PEAKVALUE' or 'SCALEFACT'
        scale_value (float): Scaling value
        boundary_type (str): Boundary type: 'HYDROGRAPH' or 'HYETOGRAPH'
        scale_type (str): Full generated hydrograph or quick runnof component only: 'FULL' or 'RUNOFF'
        minflow (float): Minimum flow value
        allow_override (str): Allow event parameters to be overridden from simulation file: ''/'OVERRIDE' or 'NOOVERRIDE'
        area (float): Catchment area (sq km)
        saar (int): Seasonal average annual rainfall (mm)
        urbext (float): Fraction of urbanised catchment area
        season (str): Season for design rainfall profile: 'DEFAULT', 'SUMMER' or 'WINTER'
        calc_source (str): ReFH calculation source: 'DLL' (recommended) or 'REPORT'
        storm_area (float): Rainfall storm area (sq km)
        storm_duration (float): Rainfall storm duration (hrs)
        rainfall_comment (str): Comment added to rainfall section of unit
        arf_method (str): Method for defining ARF: 'USER' or 'DESIGN'
        arf (float): Areal reduction factor (only used if ``arf_method`` set to 'USER')
        ddf_c (float): DDF Parameter c
        ddf_d1 (float): DDF Parameter d1
        ddf_d2 (float): DDF Parameter d2
        ddf_d3 (float): DDF Parameter d3
        ddf_e (float): DDF Parameter e
        ddf_f (float): DDF Parameter f

    Returns:
        REFHBDY: Flood Modeller REFHBDY Unit class object
    """

    _unit = "REFHBDY"

    def _read(self, refhbdy_block):  # noqa: PLR0915
        """Function to read a given REFHBDY block and store data as class attributes"""
        # line 1 & 2
        # Extract comment and revision number
        self._revision, self.comment = self._get_revision_and_comment(refhbdy_block[0])
        self.name = refhbdy_block[1][: self._label_len].strip()

        # line 3
        refhbdy_params1 = split_10_char(refhbdy_block[2])
        self._unknown_param_1 = to_float(refhbdy_params1[0])
        self.easting = int(float(refhbdy_params1[1]))
        self.northing = int(float(refhbdy_params1[2]))

        # line 4
        refhbdy_opts = split_10_char(f"{refhbdy_block[3]:<90}")
        self.time_delay = to_float(refhbdy_opts[0])
        # SD / timestep must be odd interval
        self.timestep = to_float(refhbdy_opts[1])
        # '' : Full hydrograph, 'pfonly' : peak flow, 'bfonly' : baseflow only
        self.sim_type = refhbdy_opts[2]
        self.scale_method = to_str(refhbdy_opts[3], "SCALEFACT")  # PEAKVALUE or SCALEFACT
        self.scale_value = to_float(refhbdy_opts[4], 1.0)
        self.boundary_type = to_str(refhbdy_opts[5], "HYDROGRAPH")  # HYDROGRAPH or HYETOGRAPH
        self.scale_type = to_str(refhbdy_opts[6], "FULL")  # FULL or RUNOFF
        self.minflow = to_float(refhbdy_opts[7])
        self.allow_override = refhbdy_opts[8]  # ''/OVERRIDE or NOOVERRIDE

        # line 5
        refhbdy_params2 = split_10_char(f"{refhbdy_block[4]:<60}")
        self.area = to_float(refhbdy_params2[0])
        try:
            # Maintain SAAR as integer if already is, else use float
            self.saar = int(refhbdy_params2[1])
        except ValueError:
            self.saar = float(refhbdy_params2[1])
        self.urbext = to_float(refhbdy_params2[2])
        self.season = to_str(refhbdy_params2[3], "DEFAULT")  # DEFAULT, SUMMER or WINTER
        self.calc_source = to_str(refhbdy_params2[4], "DLL")  # DLL or REPORT
        self.use_urban_subdivisions = refhbdy_params2[5] != ""
        if self.use_urban_subdivisions:
            # Just keeping this raw for now as unlikely to be used.
            self._urban_refh_data = refhbdy_block[5:8]
            rainfall_params1, rainfall_params2, rainfall_params3 = refhbdy_block[8:11]
            # Keeping rest raw for now to reduce dev time
            self._raw_extra_lines = refhbdy_block[11:]
        else:
            rainfall_params1, rainfall_params2, rainfall_params3 = refhbdy_block[5:8]
            # Keeping rest raw for now to reduce dev time
            self._raw_extra_lines = refhbdy_block[8:]

        # line 6
        rainfall_params1 = split_10_char(rainfall_params1)
        self.storm_area = to_float(rainfall_params1[0])
        self.storm_duration = to_float(rainfall_params1[1])
        self._unknown_param_2 = to_float(rainfall_params1[2])

        # line 7
        self.rainfall_comment = rainfall_params2[20:]
        rainfall_params2 = split_10_char(rainfall_params2[:20])
        self.arf_method = rainfall_params2[1]
        self._unknown_param_3 = rainfall_params2[0]

        # line 8
        rainfall_params3 = split_10_char(rainfall_params3)
        self.observed_rainfall_depth = to_float(rainfall_params3[0])
        self.return_period = to_float(rainfall_params3[1])
        self.arf = to_float(rainfall_params3[2])
        self.ddf_c = to_float(rainfall_params3[3])
        self.ddf_d1 = to_float(rainfall_params3[4])
        self.ddf_d2 = to_float(rainfall_params3[5])
        self.ddf_d3 = to_float(rainfall_params3[6])
        self.ddf_e = to_float(rainfall_params3[7])
        self.ddf_f = to_float(rainfall_params3[8])

    def _write(self):
        """Function to write a valid REFHBDY block"""
        _validate_unit(self)  # Function to check the params are valid for QTBDY
        header = self._create_header(include_revision=True)
        name = self.name[: self._label_len]

        refhbdy_block = [header, name]
        line3 = join_10_char(self._unknown_param_1, self.easting, self.northing)
        self.sim_type = (
            "" if self.sim_type.upper() == "FULL" else self.sim_type
        )  # Allow 'full' as an option
        line4 = (
            join_10_char(self.time_delay, self.timestep)
            + join_n_char_ljust(10, self.sim_type, self.scale_method)
            + join_10_char(self.scale_value)
            + join_n_char_ljust(10, self.boundary_type)
            + join_10_char(self.scale_type, self.minflow, self.allow_override)
        )
        use_urban_subdivisions = "" if not self.use_urban_subdivisions else "URBANREFH"
        line5 = join_10_char(
            self.area,
            self.saar,
            f"{self.urbext:.4f}",
            self.season,
            self.calc_source,
            use_urban_subdivisions,
        )
        refhbdy_block.extend([line3, line4, line5])

        if self.use_urban_subdivisions:
            refhbdy_block.extend(self._urban_refh_data)

        line6 = join_10_char(self.storm_area, self.storm_duration, self._unknown_param_2)
        line7 = join_10_char(self._unknown_param_3, self.arf_method) + self.rainfall_comment
        line8 = join_10_char(
            self.observed_rainfall_depth,
            self.return_period,
            self.arf,
            f"{self.ddf_c:.4f}",
            f"{self.ddf_d1:.5f}",
            f"{self.ddf_d2:.5f}",
            f"{self.ddf_d3:.5f}",
            f"{self.ddf_e:.5f}",
            f"{self.ddf_f:.5f}",
        )

        refhbdy_block.extend([line6, line7, line8])
        refhbdy_block.extend(self._raw_extra_lines)
        return refhbdy_block
