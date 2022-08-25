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


class LineData(ABC):
    def __init__(self):
        self.no_values = 0

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_value(self):
        pass


class LastData(LineData):
    def __init__(self):
        super().__init__()
        self._value = None  # single value

    def update(self, data):
        self._value = data
        self.no_values = 1

    def get_value(self):
        return self._value


class AllData(LineData):
    def __init__(self):
        super().__init__()
        self._value = []  # list

    def update(self, data):
        self._value.append(data)
        self.no_values += 1

    def _to_dataframe(self):
        # TODO: make into dataframe!!
        return self._value

    def get_value(self):
        return self._to_dataframe()


def data_factory(data_type):
    if data_type == "last":
        return LastData()
    elif data_type == "all":
        return AllData()
    else:
        raise ValueError(f'Unexpected simulation type "{data_type}"')


class LineParser(ABC):
    """Abstract base class for processing and storing different types of line"""

    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        self.prefix = prefix
        self.index = index
        self.before_index = before_index

        self._exclude = exclude

        self.no_values = 0

        self.data_type = data_type
        self.data = data_factory(data_type)

    def process_line(self, raw_line: str) -> str:
        """self._process_line with exception handling of expected nan values"""

        try:
            processed_line = self._process_line(raw_line)

        except ValueError as e:
            if raw_line in self._exclude:
                processed_line = self._nan
            else:
                raise e

        return processed_line

    @abstractmethod
    def _process_line(self, raw: str) -> str:
        """Converts string to meaningful data"""
        pass


class DateTimeParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        code: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._code = code
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string to datetime"""

        processed = dt.datetime.strptime(raw, self._code)

        return processed


class TimeParser(DateTimeParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        code: str,
        exclude: bool = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, code, exclude, index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string to time"""

        processed = super()._process_line(raw)

        return processed.time()


class TimeDeltaHMSParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string HH:MM:SS to timedelta"""

        h, m, s = raw.split(":")
        processed = dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

        return processed


class TimeDeltaHParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string H (with decimal place and "hrs") to timedelta"""

        h = raw.split("hrs")[0]
        processed = dt.timedelta(hours=float(h))

        return processed


class TimeDeltaSParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string S (with decimal place and "s") to timedelta"""

        s = raw.split("s")[0]  # TODO: not necessary for simulation time
        processed = dt.timedelta(seconds=float(s))

        return processed


class FloatParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._nan = float("nan")

    def _process_line(self, raw: str) -> str:
        """Converts string to float"""

        processed = float(raw)

        return processed


class FloatSplitParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        split: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._split = split
        self._nan = float("nan")

    def _process_line(self, raw: str):
        """Converts string to float, removing everything after split"""

        processed = float(raw.split(self._split)[0])

        return processed


class StringParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._nan = ""

    def _process_line(self, raw: str):
        """No conversion necessary"""

        processed = raw

        return processed


class StringSplitParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        split: str,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._split = split
        self._nan = ""

    def _process_line(self, raw: str):
        """Converts string to float, removing everything after split"""

        processed = raw.split(self._split)[0]

        return processed


class TimeFloatMultParser(LineParser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        names: list,
        exclude: str = None,
        index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, index, before_index)
        self._names = names

        self._nan = []
        for name in names:
            self._nan.append(float("nan"))

    def _process_line(self, raw: str):
        """Converts string to list of floats"""

        processed = [float(x) for x in raw.split()]
        processed[0] = dt.timedelta(hours=float(processed[0]))

        return processed
