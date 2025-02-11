from typing import TypeAlias

from .boundaries import HTBDY, QHBDY, QTBDY, REFHBDY
from .comment import COMMENT
from .conduits import CONDUIT
from .iic import IIC
from .losses import BLOCKAGE, CULVERT
from .sections import INTERPOLATE, REPLICATE, RIVER
from .structures import (
    BRIDGE,
    CRUMP,
    FLAT_V_WEIR,
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

TSection: TypeAlias = INTERPOLATE | REPLICATE | RIVER
TBoundary: TypeAlias = HTBDY | QHBDY | QTBDY | REFHBDY
TStructure: TypeAlias = (
    BRIDGE | CRUMP | FLAT_V_WEIR | ORIFICE | OUTFALL | RNWEIR | SLUICE | SPILL | WEIR
)
TConduit: TypeAlias = CONDUIT
TLoss: TypeAlias = BLOCKAGE | CULVERT
TUnsupported: TypeAlias = UNSUPPORTED
