import re

version_re = re.compile(r"http(?:s)?:\/\/schema\.floodmodeller\.com\/([0-9\.]+)\/2d\.xsd")

float_re = re.compile(
    r"""
    ^[+-]?                # Optional sign
    (                     # Start of number group
        (?:\d+\.\d*)      # Digits before decimal, optional after
        |                 # OR
        (?:\.\d+)         # Decimal point with digits after
        |                 # OR
        (?:\d+)           # Integer (still valid float form)
    )
    (?:[eE][+-]?\d+)?     # Optional exponent part
    $                     # End of string
""",
    re.VERBOSE,
)

int_re = re.compile(r"^-?\d+$")
