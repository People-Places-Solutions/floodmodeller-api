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

import pandas as pd

from floodmodeller_api.validation import _validate_unit
from floodmodeller_api.validation.parameters import parameter_options

from ._base import Unit
from ._helpers import (
    NOTATION_THRESHOLD,
    join_10_char,
    join_n_char_ljust,
    split_10_char,
    split_n_char,
    to_data_list,
    to_float,
    to_str,
    validate_timeunit_data,
)


class QTBDY(Unit):
    """Class to hold and process QTBDY boundary type

    Args:
        name (str, optional): Unit name. Defaults to 'new_qtbdy'.
        comment (str, optional): Comment included in unit. Defaults to ''.
        timeoffset (float, optional): Defaults to 0.0.
        timeunit (str, optional): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options. Defaults to 'HOURS'.
        extendmethod (str, optional): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'. Defaults to 'EXTEND'.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to 'LINEAR'.
        flowmultiplier (float, optional): Multiplier applied to all flow values at runtime. Defaults to 0.0.
        minflow (float, optional): Minimum flow value applied to the boundary at runtime. Defaults to 0.0.
        data (pandas.Series, optional): Series object with variable ``'Flow'`` and index ``'Time'``. Defaults to None.
        allow_override (str): Allow event parameters to be overridden from simulation file: ''/'OVERRIDE' or 'NOOVERRIDE'. Defaults to 'OVERRIDE'.

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
        # DATES stores the date and time in separate fields, so its rows have 3 physical fields.
        data_list = (
            to_data_list(qtbdy_block[3:], num_cols=2, date_col=1)
            if self.timeunit == "DATES"
            else to_data_list(qtbdy_block[3:], num_cols=2)
        )
        if data_list == [[0]]:
            data_list = [[0, 0]]
        self.data = pd.DataFrame(data_list, columns=["Flow", "Time"])
        self.data = self.data.set_index("Time")
        self.data = self.data["Flow"]  # Convert to series

    def _write(self):
        """Function to write a valid QTBDY block"""
        validate_timeunit_data(self.timeunit, self.data, self._unit)
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
        name (str, optional): Unit name. Defaults to 'new_htbdy'.
        comment (str, optional): Comment included in unit. Defaults to ''.
        timeunit (str, optional): Unit of time, e.g. 'HOURS', 'MINUTES' or 'SECONDS'. See Flood Modeller documentation for all available options. Defaults to 'HOURS'.
        extendmethod (str, optional): Data extending method: 'EXTEND', 'NOEXTEND' or 'REPEAT'. Defaults to 'EXTEND'.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to 'LINEAR'.
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

        # DATES stores the date and time in separate fields, so its rows have 3 physical fields.
        data_list = (
            to_data_list(htbdy_block[3:], num_cols=2, date_col=1)
            if self.timeunit == "DATES"
            else to_data_list(htbdy_block[3:], num_cols=2)
        )
        if data_list == [[0]]:
            data_list = [[0, 0]]

        self.data = pd.DataFrame(data_list, columns=["Stage", "Time"])
        self.data = self.data.set_index("Time")
        self.data = self.data["Stage"]  # Convert to series

        # Fix legacy Flood Modeller bug where timeunit is present in extendmethod place
        if self.extendmethod in parameter_options["timeunit"]["options"][1]:
            self.timeunit = self.extendmethod
            self.extendmethod = "EXTEND"

    def _write(self):
        """Function to write a valid HTBDY block"""
        validate_timeunit_data(self.timeunit, self.data, self._unit)
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


class NCDBDY(Unit):
    """Normal or critical depth downstream boundary.

    Blank override settings are stored as empty strings. If the file has no override header,
    ``override_data`` is an empty Series.

    Args:
        name (str, optional): Boundary node label. Defaults to 'new_ncdbdy'.
        comment (str, optional): Comment on the unit header.
        depth_type (str, optional): 'NORMAL' or 'CRITICAL'. Defaults to 'NORMAL'.
        ds_reference_label (str, optional): Node providing section data and the downstream
            extent for automatic slope calculations.
        us_reference_label (str, optional): Upstream extent for automatic slope calculations.
        slope_method (str, optional): 'BED', 'SURFACE' or 'USER' for normal depth.
            Defaults to 'BED'. Critical depth omits the slope calculation.
        user_slope (float, optional): Positive slope for the 'USER' method.
        data (pandas.DataFrame, optional): Section data with columns ``'X'``, ``'Y'``,
            ``'Mannings n'`` and ``'Panel'``. An empty table uses an existing model section.
            Use '*' for a panel separator and an empty string for a blank field.
        override_data (pandas.Series, optional): Override stage indexed by time.
        override_method (str, optional): Override flag.
        timeunit (str or float, optional): Time unit for the override series.
        extendmethod (str, optional): Override series extension method.
        interpmethod (str, optional): Override series interpolation.
    """

    _unit = "NCDBDY"
    _section_columns = ("X", "Y", "Mannings n", "Panel")

    def _create_from_blank(  # noqa: PLR0913
        self,
        name: str = "new_ncdbdy",
        comment: str = "",
        *,
        depth_type: str = "NORMAL",
        ds_reference_label: str = "",
        us_reference_label: str = "",
        slope_method: str = "BED",
        user_slope: float | None = None,
        data: pd.DataFrame | None = None,
        override_data: pd.Series | None = None,
        override_method: str = "",
        timeunit: str | float = "",
        extendmethod: str = "",
        interpmethod: str = "",
    ) -> None:
        self._revision = 1
        self.name = name
        self.comment = comment
        self._reserved_label = ""  # Reserved second label.
        self.ds_reference_label = ds_reference_label
        self.us_reference_label = us_reference_label
        self.depth_type = depth_type.upper()
        self.slope_method = slope_method.upper() if self.depth_type == "NORMAL" else None
        self.user_slope = user_slope if self.slope_method == "USER" else None
        self.data = pd.DataFrame(columns=list(self._section_columns)) if data is None else data
        self.override_data = (
            pd.Series(dtype=float, index=pd.Index([], name="Time"), name="Stage")
            if override_data is None
            else override_data
        )
        self.timeunit = timeunit
        self.extendmethod = extendmethod
        self.override_method = override_method
        self.interpmethod = interpmethod
        self._override_extra = ""
        self._has_override_header = False

    def _read(self, block):
        self._revision, self.comment = self._get_revision_and_comment(block[0])
        labels = split_n_char(f"{block[1]:<{4 * self._label_len}}", self._label_len)
        self.name, self._reserved_label, self.ds_reference_label, self.us_reference_label = labels[
            :4
        ]
        self.depth_type = block[2].strip().upper()
        self.slope_method = None
        self.user_slope = None
        section_start = 3
        if self.depth_type == "NORMAL":
            method, value = split_10_char(f"{block[3]:<20}")[:2]
            method = method.upper()
            if method == "AUTO" and not value:
                msg = f"NCDBDY {self.name!r} requires a slope source for AUTO (BED or SURFACE)"
                raise ValueError(msg)
            self.slope_method = value.upper() if method == "AUTO" else method
            if self.slope_method == "USER":
                self.user_slope = float(value)
            section_start += 1
        elif self.depth_type != "CRITICAL":
            msg = f"Unknown NCDBDY depth type: {self.depth_type!r}"
            raise ValueError(msg)

        section_end = section_start + 1 + int(block[section_start])
        rows = []
        for line in block[section_start + 1 : section_end]:
            x, y, roughness = split_10_char(f"{line:<30}")[:3]
            mannings_n = float(roughness) if roughness else ""
            rows.append((float(x), float(y), mannings_n, line[30:].strip()))
        self.data = pd.DataFrame(rows, columns=list(self._section_columns))
        self._read_override(block[section_end:])

    def _read_override(self, block):
        self._has_override_header = bool(block and block[0].strip())
        header = block[0] if self._has_override_header else "0"
        count, unit, extend, method, extra, interp = split_10_char(f"{header:<60}")[:6]
        self.timeunit = to_str(unit.upper(), "", check_float=True)
        self.extendmethod = extend.upper()
        self.override_method = method
        self.interpmethod = interp.upper()
        self._override_extra = extra
        rows = to_data_list(
            block[1 : 1 + int(count)],
            num_cols=2,
            date_col=1 if self.timeunit == "DATES" else None,
        )
        if len(rows) != int(count):
            msg = f"NCDBDY {self.name!r} declares {count} override rows but contains {len(rows)}"
            raise ValueError(msg)
        self.override_data = (
            pd.DataFrame(rows, columns=["Stage", "Time"]).set_index("Time")["Stage"].astype(float)
        )

    def _write(self):
        _validate_unit(self, allow_blank=("timeunit", "extendmethod", "interpmethod"))
        block = [
            self._create_header(include_revision=self._revision is not None),
            join_n_char_ljust(
                self._label_len,
                self.name,
                self._reserved_label,
                self.ds_reference_label,
                self.us_reference_label,
            ).rstrip(),
            self.depth_type.upper(),
        ]
        if self.depth_type.upper() == "NORMAL":
            block.append(self._write_slope())
        elif self.depth_type.upper() != "CRITICAL":
            msg = f"Unknown NCDBDY depth type: {self.depth_type!r}"
            raise ValueError(msg)

        block.append(join_10_char(len(self.data)))
        section = self.data[list(self._section_columns)]
        for x, y, roughness, panel in section.itertuples(index=False):
            mannings_n = None if pd.isna(roughness) or roughness == "" else float(roughness)
            block.append((join_10_char(float(x), float(y), mannings_n) + str(panel)).rstrip())
        block.extend(self._write_override())
        return block

    def _write_slope(self):
        if not self.slope_method:
            msg = "NCDBDY requires a slope method (BED, SURFACE or USER) for NORMAL depth"
            raise ValueError(msg)
        method = self.slope_method.upper()
        if method in ("BED", "SURFACE"):
            return f"{'AUTO':<10}" + join_10_char(method)
        if method != "USER":
            msg = f"Unknown NCDBDY slope method: {self.slope_method!r}"
            raise ValueError(msg)
        if self.user_slope is None or not 0 < self.user_slope < float("inf"):
            msg = "NCDBDY requires a finite positive slope for the USER slope method"
            raise ValueError(msg)
        integer_width = len(str(int(self.user_slope)))
        decimal_places = max(0, NOTATION_THRESHOLD - integer_width - 1)
        slope = f"{self.user_slope:.{decimal_places}f}"
        if decimal_places:
            slope = slope.rstrip("0").rstrip(".")
        if len(slope) > NOTATION_THRESHOLD or float(slope) == 0:
            msg = (
                f"NCDBDY USER slope {self.user_slope} cannot fit in the field as a positive decimal"
            )
            raise ValueError(msg)
        return f"{'USER':<10}" + join_10_char(slope)

    def _write_override(self):
        has_settings = self.timeunit != "" or bool(
            self.extendmethod or self.override_method or self.interpmethod or self._override_extra,
        )
        if not self._has_override_header and self.override_data.empty and not has_settings:
            return []

        validate_timeunit_data(self.timeunit, self.override_data, self._unit)
        header = join_10_char(
            len(self.override_data),
            self.timeunit,
            self.extendmethod.upper(),
            self.override_method,
            self._override_extra,
        )
        interp = self.interpmethod.upper()
        block = [(header + interp).rstrip()]
        if self.timeunit == "DATES":
            block.extend(
                join_10_char(float(stage)) + time for time, stage in self.override_data.items()
            )
        else:
            block.extend(
                join_10_char(float(stage), float(time))
                for time, stage in self.override_data.items()
            )
        return block


class QHBDY(Unit):
    """Class to hold and process QHBDY boundary type

    Args:
        name (str, optional): Unit name. Defaults to 'new_qhbdy'.
        comment (str, optional): Comment included in unit. Defaults to ''.
        interpmethod (str, optional): Data interpolation method: 'LINEAR' or 'SPLINE'. Defaults to 'LINEAR'.
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
