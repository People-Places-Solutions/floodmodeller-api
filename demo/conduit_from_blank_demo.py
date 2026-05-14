import pandas as pd

from floodmodeller_api.units import CONDUIT

# Check blank symmetric conduit can be created (using default parameters)
blank_symmetric_conduit = CONDUIT(subtype="SECTION")
print(blank_symmetric_conduit)

# Check symmetric conduit can be created with parameters
coords = pd.DataFrame({"x": [0, 1, 2], "y": [0, 0.5, 2], "cw_friction": [1.5, 1.5, 1.5]})
symmetric_conduit = CONDUIT(subtype="SECTION", dist_to_next=5, coords=coords)
print(symmetric_conduit)
