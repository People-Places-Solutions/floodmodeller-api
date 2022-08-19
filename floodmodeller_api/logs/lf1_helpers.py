"""
Flood Modeller Python API
Copyright (C) 2022 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License 
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty 
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. 

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following 
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

from abc import ABC, abstractmethod
import datetime as dt
import pandas as pd


class LineType(ABC):
    """Abstract base class for processing and storing different types of line"""

    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        self.prefix = prefix
        self.stage = stage
        self.defines_iters = defines_iters
        self.before_defines_iters = before_defines_iters

        self._exclude = exclude

        self.no_values = 0

        if stage == "run":
            self.value = []  # list
            self.update_value_wrapper = self._append_to_value

        elif stage in ("start", "end"):
            self.value = None  # single value
            self.update_value_wrapper = self._replace_value

        else:
            raise ValueError(f'Unexpected simulation stage "{stage}"')

    def _append_to_value(self, processed_line: str):
        self.value.append(processed_line)
        self.no_values += 1

    def _replace_value(self, processed_line: str):
        self.value = processed_line
        self.no_values = 1

    def process_line_wrapper(self, raw_line: str) -> str:
        """self._process_line but with exception handling e.g. of nans"""

        try:
            processed_line = self._process_line(raw_line)

        except ValueError as e:
            if raw_line == self._exclude:
                processed_line = self._nan
            else:
                raise e

        return processed_line

    @abstractmethod
    def _process_line(self):
        pass


class DateTime(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        code: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._code = code
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string to datetime"""

        processed = dt.datetime.strptime(raw, self._code)

        return processed


class Time(DateTime):
    def __init__(
        self,
        prefix: str,
        stage: str,
        code: str,
        exclude: bool = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(
            prefix, stage, code, exclude, defines_iters, before_defines_iters
        )
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string to time"""

        processed = super()._process_line(raw)

        return processed.time()


class TimeDeltaHMS(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string HH:MM:SS to timedelta"""

        h, m, s = raw.split(":")
        processed = dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

        return processed


class TimeDeltaH(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string H (with decimal place) to timedelta"""

        h = raw.split("hrs")[0]
        processed = dt.timedelta(hours=float(h))

        return processed


class TimeDeltaS(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string S (with decimal place) to timedelta"""

        s = raw.split("s")[0]  # TODO: not necessary for simulation time
        processed = dt.timedelta(seconds=float(s))

        return processed


class Float(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = float("nan")

    def _process_line(self, raw: str) -> str:
        """Converts string to float"""

        processed = float(raw)

        return processed


class Int(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = -99999

    def _process_line(self, raw: str):
        """Converts string to integer"""

        processed = int(raw)

        return processed


class FloatSplit(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        split: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._split = split
        self._nan = float("nan")

    def _process_line(self, raw: str):
        """Converts string to float, removing everything after split"""

        processed = float(raw.split(self._split)[0])

        return processed


class String(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._nan = ""

    def _process_line(self, raw: str):
        """No conversion necessary"""

        processed = raw

        return processed


class TimeFloatMult(LineType):
    def __init__(
        self,
        prefix: str,
        stage: str,
        names: list,
        exclude: str = None,
        defines_iters: bool = False,
        before_defines_iters: bool = False,
    ):
        super().__init__(prefix, stage, exclude, defines_iters, before_defines_iters)
        self._names = names

        self._nan = []
        for name in names:
            self._nan.append(float("nan"))

    def _process_line(self, raw: str):
        """Converts string to list of floats"""

        processed = [float(x) for x in raw.split()]
        processed[0] = dt.timedelta(hours=float(processed[0]))

        return processed
