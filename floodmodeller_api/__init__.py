import logging
import sys

from .dat import DAT
from .ied import IED
from .ief import IEF
from .inp import INP
from .logs import LF1, LF2
from .util import read_file
from .version import __version__
from .xml2d import XML2D
from .zz import ZZN, ZZX

logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
)
