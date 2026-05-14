import pprint

from floodmodeller_api.units import (
    BLOCKAGE,
    BRIDGE,
    COMMENT,
    CONDUIT,
    CRUMP,
    CULVERT,
    FLAT_V_WEIR,
    FLOODPLAIN,
    HTBDY,
    IIC,
    INTERPOLATE,
    JUNCTION,
    LATERAL,
    ORIFICE,
    OUTFALL,
    QHBDY,
    QTBDY,
    REFHBDY,
    REPLICATE,
    RESERVOIR,
    RIVER,
    RNWEIR,
    SLUICE,
    SPILL,
    WEIR,
    Variables,
)

unit_classes = {
    QTBDY: {"group": "boundaries", "has_subtype": False},
    HTBDY: {"group": "boundaries", "has_subtype": False},
    QHBDY: {"group": "boundaries", "has_subtype": False},
    REFHBDY: {"group": "boundaries", "has_subtype": False},
    RIVER: {"group": "sections", "has_subtype": True},
    BRIDGE: {"group": "structures", "has_subtype": True},
    CONDUIT: {"group": "conduits", "has_subtype": True},
    SLUICE: {"group": "structures", "has_subtype": True},
    ORIFICE: {"group": "structures", "has_subtype": True},
    SPILL: {"group": "structures", "has_subtype": False},
    IIC: {"group": "other", "has_subtype": False},
    Variables: {"group": "other", "has_subtype": False},
    BLOCKAGE: {"group": "losses", "has_subtype": False},
    CULVERT: {"group": "losses", "has_subtype": True},
    RNWEIR: {"group": "structures", "has_subtype": False},
    WEIR: {"group": "structures", "has_subtype": False},  # general weir
    CRUMP: {"group": "structures", "has_subtype": False},
    FLAT_V_WEIR: {"group": "structures", "has_subtype": False},
    INTERPOLATE: {"group": "sections", "has_subtype": False},
    REPLICATE: {"group": "sections", "has_subtype": False},
    OUTFALL: {"group": "structures", "has_subtype": True},
    COMMENT: {"group": "comments", "has_subtype": False},
    JUNCTION: {"group": "connectors", "has_subtype": True},
    LATERAL: {"group": "connectors", "has_subtype": False},
    RESERVOIR: {"group": "controls", "has_subtype": False},
    FLOODPLAIN: {"group": "structures", "has_subtype": True}
    }

subtype_units = {
    CONDUIT: ["CIRCULAR", "RECTANGULAR", "SPRUNG", "SPRUNGARCH", "SECTION"],
    RIVER: ["SECTION"],
    BRIDGE: ["ARCH", "USBPR1978", "PIERLOSS", "INTEGRATED"],
    SLUICE: ["RADIAL", "VERTICAL"],
    ORIFICE: ["FLAPPED", "OPEN"], # Seems to have different functioning where flapped: (True or False) is used instead of subtype
    CULVERT: ["INLET", "OUTLET"],
    OUTFALL: ["FLAPPED", "OPEN"], # Seems to have different functioning where flapped: (True or False) is used instead of subtype
    JUNCTION: ["OPEN"], # Unclear whether other subtypes are available
    FLOODPLAIN: ["SECTION"], # Unclear whether other subtypes are available ("hardcoding" noted)
}

errors_unit = {}
errors_subtypes = {}
not_implemented = []
for unit_class in unit_classes:
    try:
        unit_class()._write()
    except NotImplementedError as e:  # noqa: PERF203
        errors_unit[unit_class.__name__] = e
        not_implemented.append(unit_class)
    except Exception as e:
        errors_unit[unit_class.__name__] = e

for unit_class, subtypes in subtype_units.items():

    if unit_class in not_implemented:
        continue

    for subtype in subtypes:
        try:
            unit_class(subtype=subtype)._write()
            errors_subtypes[f"{unit_class.__name__} {subtype}"] = None
        except Exception as e:  # noqa: PERF203
            errors_subtypes[f"{unit_class.__name__} {subtype}"] = e

pprint.pprint(errors_unit)
print("")
pprint.pprint(errors_subtypes)
