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

xml2d_template = """<?xml version="1.0" standalone="yes"?>
<ISIS2Dproject xmlns="https://www.floodmodeller.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.floodmodeller.com http://schema.floodmodeller.com/6.2/2d.xsd" name="2d_simulation_blank" description="">
    <domain domain_id="Domain 1">
        <topography>0</topography>
    <time>
        <timezero_datetime use_real_dates="false">00:00:00 01/01/2000</timezero_datetime>
        <start_offset unit="hour">0</start_offset>
        <total unit="hour">0.00</total>
    </time>
    <run_data>
        <time_step>1</time_step>
        <scheme>ADI</scheme>
    </run_data>
    <output_results>
        <output expand="0" format="ASCII">
            <variables> </variables>
            <frequency>0</frequency>
        </output>
    </output_results>
    </domain>
</ISIS2Dproject>"""
