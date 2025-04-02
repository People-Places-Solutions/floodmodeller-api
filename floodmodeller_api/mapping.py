from __future__ import annotations

from typing import Any

from . import DAT, IED, IEF, INP, LF1, LF2, XML2D, ZZN
from .backup import File
from .ief import FlowTimeProfile
from .units import (
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
    UNSUPPORTED,
    WEIR,
    Variables,
)
from .urban1d.conduits import CONDUIT as CONDUIT_URBAN
from .urban1d.conduits import CONDUITS as CONDUITS_URBAN
from .urban1d.junctions import JUNCTION as JUNCTION_URBAN
from .urban1d.junctions import JUNCTIONS
from .urban1d.losses import LOSS, LOSSES
from .urban1d.outfalls import OUTFALL as OUTFALL_URBAN
from .urban1d.outfalls import OUTFALLS as OUTFALLS_URBAN
from .urban1d.raingauges import RAINGAUGE, RAINGAUGES
from .urban1d.xsections import XSECTION, XSECTIONS

api_class_mapping: dict[str, Any] = {
    "floodmodeller_api.dat.DAT": DAT,
    "floodmodeller_api.ied.IED": IED,
    "floodmodeller_api.ief.IEF": IEF,
    "floodmodeller_api.ief.FlowTimeProfile": FlowTimeProfile,
    "floodmodeller_api.inp.INP": INP,
    "floodmodeller_api.lf.LF1": LF1,
    "floodmodeller_api.lf.LF2": LF2,
    "floodmodeller_api.xml2d.XML2D": XML2D,
    "floodmodeller_api.zzn.ZZN": ZZN,
    "floodmodeller_api.backup.File": File,
    "floodmodeller_api.urban1d.junctions.JUNCTIONS": JUNCTIONS,
    "floodmodeller_api.urban1d.junctions.JUNCTION": JUNCTION_URBAN,
    "floodmodeller_api.urban1d.outfalls.OUTFALLS": OUTFALLS_URBAN,
    "floodmodeller_api.urban1d.outfalls.OUTFALL": OUTFALL_URBAN,
    "floodmodeller_api.urban1d.raingauges.RAINGAUGES": RAINGAUGES,
    "floodmodeller_api.urban1d.raingauges.RAINGAUGE": RAINGAUGE,
    "floodmodeller_api.urban1d.conduits.CONDUITS": CONDUITS_URBAN,
    "floodmodeller_api.urban1d.conduits.CONDUIT": CONDUIT_URBAN,
    "floodmodeller_api.urban1d.losses.LOSSES": LOSSES,
    "floodmodeller_api.urban1d.losses.LOSS": LOSS,
    "floodmodeller_api.urban1d.xsections.XSECTIONS": XSECTIONS,
    "floodmodeller_api.urban1d.xsections.XSECTION": XSECTION,
    "floodmodeller_api.units.boundaries.HTBDY": HTBDY,
    "floodmodeller_api.units.boundaries.QHBDY": QHBDY,
    "floodmodeller_api.units.boundaries.QTBDY": QTBDY,
    "floodmodeller_api.units.boundaries.REFHBDY": REFHBDY,
    "floodmodeller_api.units.comment.COMMENT": COMMENT,
    "floodmodeller_api.units.conduits.CONDUIT": CONDUIT,
    "floodmodeller_api.units.connectors.JUNCTION": JUNCTION,
    "floodmodeller_api.units.connectors.LATERAL": LATERAL,
    "floodmodeller_api.units.controls.RESERVOIR": RESERVOIR,
    "floodmodeller_api.units.iic.IIC": IIC,
    "floodmodeller_api.units.losses.BLOCKAGE": BLOCKAGE,
    "floodmodeller_api.units.losses.CULVERT": CULVERT,
    "floodmodeller_api.units.sections.INTERPOLATE": INTERPOLATE,
    "floodmodeller_api.units.sections.REPLICATE": REPLICATE,
    "floodmodeller_api.units.sections.RIVER": RIVER,
    "floodmodeller_api.units.structures.FLOODPLAIN": FLOODPLAIN,
    "floodmodeller_api.units.structures.BRIDGE": BRIDGE,
    "floodmodeller_api.units.structures.CRUMP": CRUMP,
    "floodmodeller_api.units.structures.FLAT_V_WEIR": FLAT_V_WEIR,
    "floodmodeller_api.units.structures.ORIFICE": ORIFICE,
    "floodmodeller_api.units.structures.OUTFALL": OUTFALL,
    "floodmodeller_api.units.structures.RNWEIR": RNWEIR,
    "floodmodeller_api.units.structures.SLUICE": SLUICE,
    "floodmodeller_api.units.structures.SPILL": SPILL,
    "floodmodeller_api.units.structures.WEIR": WEIR,
    "floodmodeller_api.units.unsupported.UNSUPPORTED": UNSUPPORTED,
    "floodmodeller_api.units.variables.Variables": Variables,
}
