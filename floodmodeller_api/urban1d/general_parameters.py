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

DEFAULT_OPTIONS = {
    "flow_units": None,
    "infiltration": None,
    "flow_routing": None,
    "link_offsets": None,
    "force_main_equation": None,
    "ignore_rainfall": None,
    "ignore_snowmelt": None,
    "ignore_groundwater": None,
    "ignore_rdii": None,
    "ignore_routing": None,
    "ignore_quality": None,
    "allow_ponding": None,
    "skip_steady_state": None,
    "sys_flow_tol": None,
    "lat_flow_tol": None,
    "start_date": None,
    "start_time": None,
    "end_date": None,
    "end_time": None,
    "report_start_date": None,
    "report_start_time": None,
    "sweep_start": None,
    "sweep_end": None,
    "dry_days": None,
    "report_step": None,
    "wet_step": None,
    "dry_step": None,
    "routing_step": None,
    "lengthening_step": None,
    "variable_step": None,
    "minimum_step": None,
    "inertial_damping": None,
    "normal_flow_limited": None,
    "min_surfarea": None,
    "min_slope": None,
    "max_trials": None,
    "head_tolerance": None,
    "threads": None,
    "tempdir": None,
    "rule_step": None,
}
