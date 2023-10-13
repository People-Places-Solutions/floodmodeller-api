"""
Flood Modeller Python API
Copyright (C) 2023 Jacobs U.K. Limited

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License
as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty
of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see https://www.gnu.org/licenses/.

If you have any query about this program or this License, please contact us at support@floodmodeller.com or write to the following
address: Jacobs UK Limited, Flood Modeller, Cottons Centre, Cottons Lane, London, SE1 2QG, United Kingdom.
"""

import datetime as dt
from abc import ABC, abstractmethod
from typing import List, Optional, Union

import pandas as pd


class Data(ABC):
    def __init__(self, header: str, subheaders: Optional[list]):
        self.header = header
        self.no_values = 0
        self._subheaders = subheaders

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_value(self):
        pass


class LastData(Data):
    def __init__(self, header: str, subheaders: Optional[list]):
        super().__init__(header, subheaders)
        self._value = None  # single value

    def update(self, data):
        self._value = data
        self.no_values = 1

    def get_value(self, index_key=None, index_df=None):
        return self._value


class AllData(Data):
    def __init__(self, header: str, subheaders: Optional[list]):
        super().__init__(header, subheaders)
        self._value: List[object] = []  # list

    def update(self, data):
        self._value.append(data)
        self.no_values += 1

    def get_value(
        self, index_key: Optional[str] = None, index_df: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        df = pd.DataFrame(self._value)

        # do nothing to empty dataframes
        if df.empty:
            return df

        # overall header
        if self._subheaders is None:
            df.rename(columns={df.columns[0]: self.header}, inplace=True)

        elif index_key is not None:
            # subheaders
            df = df.set_axis(self._subheaders, axis=1)

            # remove duplicate of index
            # sometimes it includes extra values
            # it also has different precision
            index_duplicate = index_key + "_duplicate"
            if index_duplicate in df.columns:
                index_df = df[index_duplicate].dt.round("1s")

                df.drop(index_duplicate, axis=1, inplace=True)
                # self._subheaders.remove(index_duplicate)

        # there is no index because *this* is the index
        if index_key is None:
            return df

        # made lf index the dataframe index
        df[index_key] = index_df
        df.dropna(inplace=True)
        df.drop_duplicates(subset=index_key, keep="last", inplace=True)
        df.set_index(index_key, inplace=True)

        return df


def data_factory(data_type: str, header: str, subheaders: Optional[list] = None):
    if data_type == "last":
        return LastData(header, subheaders)
    if data_type == "all":
        return AllData(header, subheaders)
    raise ValueError(f'Unexpected data "{data_type}"')


class State(ABC):
    def __init__(self, extracted_data):
        pass

    @abstractmethod
    def report_progress(self):
        pass


class UnsteadyState(State):
    def __init__(self, extracted_data):
        self._progress_data = extracted_data["progress"].data

    def report_progress(self) -> float:
        """Returns last progress percentage"""

        progress = self._progress_data.get_value()

        if progress is None:
            return 0

        return progress


class SteadyState(State):
    def report_progress(self):
        raise NotImplementedError("No progress reporting for steady simulations")


def state_factory(steady: bool, extracted_data: Data) -> State:
    if steady is True:
        return SteadyState(extracted_data)
    return UnsteadyState(extracted_data)


class Parser(ABC):
    """Abstract base class for processing and storing different types of line

    Args:
        name
        prefix
        data_type
        exclude
        is_index
        before_index
    """

    _nan: object

    def __init__(
        self,
        name: str,
        prefix: str,
        data_type: str,
        exclude: Optional[str] = None,
        is_index: Optional[bool] = False,
        before_index: Optional[bool] = False,
    ):
        self._name = name

        self.prefix = prefix
        self.is_index = is_index
        self.before_index = before_index

        self._exclude = exclude

        self.no_values = 0

        self.data_type = data_type
        self.data = data_factory(data_type, name)

    def process_line(self, raw_line: str) -> None:
        """self._process_line with exception handling of expected nan values"""

        try:
            processed_line = self._process_line(raw_line)

        except ValueError as e:
            if self._exclude and raw_line in self._exclude:
                processed_line = self._nan
            else:
                raise e

        self.data.update(processed_line)

    @abstractmethod
    def _process_line(self, raw: str) -> object:
        """Converts string to meaningful data"""
        pass


class DateTimeParser(Parser):
    """Extra argument from superclass    code: str"""

    def __init__(self, *args, **kwargs):
        self._code = kwargs.pop("code")
        super().__init__(*args, **kwargs)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> dt.datetime:
        """Converts string to datetime"""

        processed = dt.datetime.strptime(raw, self._code)

        return processed


class TimeParser(Parser):
    """Extra argument from superclass    code: str"""

    def __init__(self, *args, **kwargs):
        self._code = kwargs.pop("code")
        super().__init__(*args, **kwargs)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> dt.time:
        """Converts string to time"""

        raw, _, _ = raw.partition(" ")  # Temp fix to ignore '(+n d)' in EFT
        processed = dt.datetime.strptime(raw, self._code).time()

        return processed


class TimeDeltaHMSParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> dt.timedelta:
        """Converts string HH:MM:SS to timedelta"""

        h, m, s = raw.split(":")
        processed = dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

        return processed


class TimeDeltaHParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> dt.timedelta:
        """Converts string H (with decimal place and "hrs") to timedelta"""

        h = raw.split("hrs")[0]
        processed = dt.timedelta(hours=float(h))

        return processed


class TimeDeltaSParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> dt.timedelta:
        """Converts string S (with decimal place and "s") to timedelta"""

        s = raw.split("s")[0]  # TODO: not necessary for simulation time
        processed = dt.timedelta(seconds=float(s))

        return processed


class FloatParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nan = float("nan")

    def _process_line(self, raw: str) -> float:
        """Converts string to float"""

        processed = float(raw)

        return processed


class FloatSplitParser(Parser):
    """Extra argument from superclass    split: list"""

    def __init__(self, *args, **kwargs):
        self._split = kwargs.pop("split")
        super().__init__(*args, **kwargs)
        self._nan = float("nan")

    def _process_line(self, raw: str) -> float:
        """Converts string to float, removing everything after split"""

        processed = float(raw.split(self._split)[0])

        return processed


class StringParser(Parser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._nan = ""

    def _process_line(self, raw: str) -> str:
        """No conversion necessary"""

        processed = raw

        return processed


class StringSplitParser(Parser):
    """Extra argument from superclass    split: str"""

    def __init__(self, *args, **kwargs):
        self._split = kwargs.pop("split")
        super().__init__(*args, **kwargs)
        self._nan = ""

    def _process_line(self, raw: str) -> str:
        """Removes everything after split"""

        processed = raw.split(self._split)[0]

        return processed


class TimeFloatMultParser(Parser):
    """Extra argument from superclass    names: list"""

    def __init__(self, *args, **kwargs):
        self._subheaders = kwargs.pop("subheaders")
        super().__init__(*args, **kwargs)

        self._nan = []
        for header in self._subheaders:
            self._nan.append(float("nan"))

        self.data = data_factory(self.data_type, self._name, self._subheaders)  # overwrite

    def _process_line(self, raw: str) -> List[Union[dt.timedelta, float]]:
        """Converts string to list of one timedelta and then floats"""

        as_float = [float(x) for x in raw.split()]
        first_as_timedelta = dt.timedelta(hours=float(as_float[0]))
        processed = [first_as_timedelta] + as_float[1:]

        return processed
