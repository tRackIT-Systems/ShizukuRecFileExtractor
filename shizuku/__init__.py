import struct
import datetime
import typing

try:
    import pandas as pd
except ImportError:
    pd = None


class ShizukuReader():
    def __init__(self, fd: typing.BinaryIO):
        self._fd = fd
        self._preamble = self._fd.read(52)
        self._s1 = self._fd.read(20)
        self._s2 = self._fd.read(20)
        self._s3 = self._fd.read(20)
        self._s4 = self._fd.read(20)

    def __iter__(self):
        return self

    def __next__(self) -> typing.Tuple[float, float, float, float, float, float]:
        raw = self._fd.read(28)
        if raw:
            u1, u2, u3, u4, time_ms, u5, u6, u7, u8, vbus, ibus, data_plus, data_minus = struct.unpack("<ccccIccccffff", raw)

            power_w = vbus*ibus
            return (datetime.timedelta(milliseconds=time_ms).total_seconds(), vbus, ibus, data_plus, data_minus, power_w)
        raise StopIteration

    @property
    def header(self) -> typing.Tuple[str, str, str, str, str, str]:
        return ("Time (s)", "Voltage (V)", "Current (A)", "D+ (V)", "D- (V)", "Power (W)")


class ShizukuDictReader(ShizukuReader):
    def __next__(self) -> typing.Dict[str, float]:
        return dict(zip(self.header, ShizukuReader.__next__(self)))


class ShizukuRec():
    def __init__(self, fd: typing.BinaryIO):
        reader = ShizukuReader(fd)
        self._data = []

        time_s = 0.0
        for row in reader:
            # compute timedelta
            timedelta_s = row[0] - time_s
            time_s = row[0]

            # derive energy used in the block
            energy_wh = row[5] * (timedelta_s / 60 / 60)
            capacity_ah = row[2] * (timedelta_s / 60 / 60)

            # append row
            self._data.append((*row, timedelta_s, energy_wh, capacity_ah))

        self._header = (*reader.header, "Timedelta (s)", "Energy (Wh)", "Capacity (Ah)")

    @property
    def samples(self) -> int:
        return len(self.data)

    @property
    def duration(self) -> float:
        return self._data[-1][0]

    @property
    def sampling_rate(self) -> float:
        return self.samples / self.duration

    @property
    def data(self) -> typing.List[typing.Tuple[float, float, float, float, float, float, float, float]]:
        return self._data

    @property
    def header(self) -> typing.Tuple[str, str, str, str, str, str, str, str]:
        return self._header

    @property
    def voltage(self):
        return [row[1] for row in self._data]

    @property
    def current(self):
        return [row[2] for row in self._data]

    @property
    def power(self):
        return [row[5] for row in self._data]

    @property
    def energy(self):
        return [row[7] for row in self._data]

    @property
    def capacity(self):
        return [row[8] for row in self._data]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} samples={self.samples} duration={self.duration} rate={self.sampling_rate}>"

    @property
    def dataframe(self):
        if pd is None:
            raise ValueError("Install pandas to access the dataframe")

        df = pd.DataFrame(self.data, columns=self.header)
        df["Time"] = pd.to_timedelta(df["Time (s)"], unit="s")
        df = df.set_index("Time")
        return df
