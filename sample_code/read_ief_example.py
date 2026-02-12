"""This sample script shows how to read an IEF and obtain its properties"""

# Import modules
import sys

try:
    from floodmodeller_api import IEF
except ImportError:
    print(
        "Import failed - Please ensure you have correctly installed floodmodeller_api to your active environment",
    )
    sys.exit()


# Read in the .ief file
ief = IEF("floodmodeller_api/test/test_data/modified_parameters.ief")

# We can access a single parameter like this:
print(ief.Theta)

# Or iterate across/access via string with getattr()
for parameter in ("Theta", "Alpha", "minitr", "maxitr"):
    value = getattr(ief, parameter)
    print(f"{parameter} : {value}")

ief2 = IEF("sample_code/sample_data/ex3.ief")

# Note that a .ief file might not have a parameter defined (left as default value)
# This is reflected in the `IEF` class as the attribute won't exist if not in the .ief file
# This can be handled by checking with `hasattr()`, wrapping with try-except, or the default-argument of getattr():

if hasattr(ief2, "Theta"):
    print("ief2 has the Theta attribute")
    theta = ief.Theta
else:
    print("ief2 does not have the Theta attribute")
    theta = 0.7

try:
    alpha = ief2.Alpha
except AttributeError:
    # ief2.Alpha raises an error so we will set the value as default
    alpha = 0.7

maxitr = getattr(ief2, "maxitr", 11)

print("ief2 parameters:")
print(f"Theta: {theta}")
print(f"Alpha: {alpha}")
print(f"maxitr: {maxitr}")
