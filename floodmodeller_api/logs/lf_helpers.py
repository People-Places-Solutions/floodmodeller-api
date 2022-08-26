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


class State(ABC):
    def __init__(self, data_to_extract: dict):
        self.data_to_extract = data_to_extract

    def _init_progress(self, extracted_data):
        pass

    @abstractmethod
    def report_progress(self):
        pass


class UnsteadyState(State):

    def _init_progress(self, extracted_data):
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


def state_factory(
    steady: bool,
    steady_data_to_extract: dict,
    unsteady_data_to_extract: dict,
) -> State:
    if steady == True:
        return SteadyState(steady_data_to_extract)
    else:
        return UnsteadyState(unsteady_data_to_extract)


class Data(ABC):
    def __init__(self, names):
        self.no_values = 0
        self._names = names

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def get_value(self):
        pass


class LastData(Data):
    def __init__(self, names):
        super().__init__(names)
        self._value = None  # single value

    def update(self, data):
        self._value = data
        self.no_values = 1

    def get_value(self):
        return self._value


class AllData(Data):
    def __init__(self, names):
        super().__init__(names)
        self._value = []  # list

    def update(self, data):
        self._value.append(data)
        self.no_values += 1

    def get_value(self) -> pd.DataFrame:
        # TODO:
        # - clean up multilevel index
        # - remove duplicated rows at start and end
        # - simulated as index

        df = pd.DataFrame(self._value)

        if self._names is not None and not df.empty:
            df.set_axis(self._names, axis=1, inplace=True)

        if "simulated_duplicate" in df.columns:
            df = df.drop("simulated_duplicate", axis=1)

        df = df.dropna()

        return df


def data_factory(data_type, names=None):
    if data_type == "last":
        return LastData(names)
    elif data_type == "all":
        return AllData(names)
    else:
        raise ValueError(f'Unexpected data "{data_type}"')


class Parser(ABC):
    """Abstract base class for processing and storing different types of line"""

    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        self.prefix = prefix
        self.is_index = is_index
        self.before_index = before_index

        self._exclude = exclude

        self.no_values = 0

        self.data_type = data_type
        self.data = data_factory(data_type)

    def process_line(self, raw_line: str):
        """self._process_line with exception handling of expected nan values"""

        try:
            processed_line = self._process_line(raw_line)

        except ValueError as e:
            if raw_line in self._exclude:
                processed_line = self._nan
            else:
                raise e

        self.data.update(processed_line)

    @abstractmethod
    def _process_line(self, raw: str) -> str:
        """Converts string to meaningful data"""
        pass


class DateTimeParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        code: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
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
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, code, exclude, is_index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string to time"""

        processed = super()._process_line(raw)

        return processed.time()


class TimeDeltaHMSParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string HH:MM:SS to timedelta"""

        h, m, s = raw.split(":")
        processed = dt.timedelta(hours=int(h), minutes=int(m), seconds=int(s))

        return processed


class TimeDeltaHParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string H (with decimal place and "hrs") to timedelta"""

        h = raw.split("hrs")[0]
        processed = dt.timedelta(hours=float(h))

        return processed


class TimeDeltaSParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._nan = pd.NaT

    def _process_line(self, raw: str) -> str:
        """Converts string S (with decimal place and "s") to timedelta"""

        s = raw.split("s")[0]  # TODO: not necessary for simulation time
        processed = dt.timedelta(seconds=float(s))

        return processed


class FloatParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._nan = float("nan")

    def _process_line(self, raw: str) -> str:
        """Converts string to float"""

        processed = float(raw)

        return processed


class FloatSplitParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        split: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._split = split
        self._nan = float("nan")

    def _process_line(self, raw: str):
        """Converts string to float, removing everything after split"""

        processed = float(raw.split(self._split)[0])

        return processed


class StringParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._nan = ""

    def _process_line(self, raw: str):
        """No conversion necessary"""

        processed = raw

        return processed


class StringSplitParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        split: str,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._split = split
        self._nan = ""

    def _process_line(self, raw: str):
        """Converts string to float, removing everything after split"""

        processed = raw.split(self._split)[0]

        return processed


class TimeFloatMultParser(Parser):
    def __init__(
        self,
        prefix: str,
        data_type: str,
        names: list,
        exclude: str = None,
        is_index: bool = False,
        before_index: bool = False,
    ):
        super().__init__(prefix, data_type, exclude, is_index, before_index)
        self._names = names

        self._nan = []
        for name in names:
            self._nan.append(float("nan"))

        self.data = data_factory(data_type, names)  # overwrite

    def _process_line(self, raw: str):
        """Converts string to list of floats"""

        processed = [float(x) for x in raw.split()]
        processed[0] = dt.timedelta(hours=float(processed[0]))

        return processed
