xml2d_template = """<?xml version="1.0" standalone="yes"?>
<ISIS2Dproject xmlns="https://www.floodmodeller.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="https://www.floodmodeller.com http://schema.floodmodeller.com/6.1/2d.xsd" name="2d_simulation_blank" description="">
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