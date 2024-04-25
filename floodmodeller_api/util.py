"""
Flood Modeller Python API
Copyright (C) 2024 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from __future__ import annotations

import sys
import webbrowser
from functools import wraps
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable

    from ._base import FMFile


def open_docs():
    webbrowser.open_new_tab("https://api.floodmodeller.com/api/")


def read_file(filepath: str | Path) -> FMFile:
    """Helper function to create an instance of an API class based on the provided filepath.

    This function maps file suffixes to specific classes and returns an instance of the
    corresponding class for handling the file.

    Args:
        filepath (Union[str, Path]): The path to the file to be read, as a string or Path object.

    Returns:
        FMFile: An instance of the class corresponding to the file type identified by the file suffix.

    Raises:
        ValueError: If the file suffix does not correspond to any supported file type.

    Example:
        .. code-block:: python

            from floodmodeller_api import read_file

            ief = read_file("/path/to/file.ief")


    """
    from . import DAT, IED, IEF, INP, LF1, LF2, XML2D, ZZN

    suffix_to_class = {
        ".ief": IEF,
        ".dat": DAT,
        ".ied": IED,
        ".xml": XML2D,
        ".zzn": ZZN,
        ".inp": INP,
        ".lf1": LF1,
        ".lf2": LF2,
    }
    filepath = Path(filepath)
    api_class = suffix_to_class.get(filepath.suffix.lower())
    if api_class:
        return api_class(filepath)

    raise ValueError(f"Unsupported file type: {filepath.suffix}")


def is_windows() -> bool:
    return sys.platform.startswith("win")


def handle_exception(when: str) -> Callable:
    """Decorator factory to wrap a method with exception handling."""
    def decorator(method: Callable) -> Callable:
        @wraps(method)
        def wrapped_method(self: FMFile, *args, **kwargs):
            try:
                return method(self, *args, **kwargs)
            except Exception as e:
                self._handle_exception(e, when)
        return wrapped_method
    return decorator
