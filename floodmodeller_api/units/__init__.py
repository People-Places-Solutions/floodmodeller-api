from typing import TypeAlias

from .boundaries import HTBDY, QHBDY, QTBDY, REFHBDY
from .comment import COMMENT
from .conduits import CONDUIT
from .connectors import JUNCTION, LATERAL
from .controls import RESERVOIR
from .iic import IIC
from .losses import BLOCKAGE, CULVERT
from .sections import INTERPOLATE, REPLICATE, RIVER
from .structures import (
    BRIDGE,
    CRUMP,
    FLAT_V_WEIR,
    FLOODPLAIN,
    ORIFICE,
    OUTFALL,
    RNWEIR,
    SLUICE,
    SPILL,
    WEIR,
)
from .units import ALL_UNIT_TYPES, SUPPORTED_UNIT_TYPES, UNSUPPORTED_UNIT_TYPES
from .unsupported import UNSUPPORTED
from .variables import Variables

TBoundaries: TypeAlias = HTBDY | QHBDY | QTBDY | REFHBDY
TSections: TypeAlias = INTERPOLATE | REPLICATE | RIVER
TConduits: TypeAlias = CONDUIT
TConnectors: TypeAlias = JUNCTION | LATERAL
TControls: TypeAlias = RESERVOIR
TLosses: TypeAlias = BLOCKAGE | CULVERT
TStructures: TypeAlias = (
    BRIDGE | CRUMP | FLAT_V_WEIR | ORIFICE | OUTFALL | RNWEIR | SLUICE | SPILL | WEIR | FLOODPLAIN
)
TUnsupported: TypeAlias = UNSUPPORTED
