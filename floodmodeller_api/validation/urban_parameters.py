urban_parameter_options = {
        'elevation': {
        'type': 'type-match',
        'options': (float, int)
    },
    'max_depth': {
         'type': 'type-match',
        'options': (float, int)
    },
    'initial_depth': {
        'type': 'type-match',
        'options': (float, int)
    },
    'surface_depth': {
        'type': 'type-match',
        'options': (float, int)
    },
    'area_ponded': {
        'type': 'type-match',
        'options': (float, int)
    },
    'format': {
         'type': 'value-match',
        'options': ['INTENSITY', 'VOLUME', 'CUMULATIVE']
    },
    'interval': {    # TODO: UPDATE TO CONSIDER - decimal hours or hours:minutes format (e.g., 0:15 for 15-minute readings). search for presence of ';' during _read maybe?
    #try turing to float else keep as string
        'type': 'type-match',
        'options': (float, int, str) # TODO: add new a type of match called RegEx match for example '[0-9]:[0-9]'
    },
    'snow_catch_factor': {
        'type': 'type-match',
        'options': (float, int)
    },
    'data_option': {
         'type': 'value-match',
        'options': ['TIMESERIES', 'FILE']
    },
    'timeseries': {
        'type': 'type-match',
        'options': (str)
    },
    'filename': {
        'type': 'type-match',
        'options': (str)
    },
    'station': {
        'type': 'type-match',
        'options': (str)
    },
    'units': {
         'type': 'value-match',
        'options': ['IN', 'MM']
    }
}