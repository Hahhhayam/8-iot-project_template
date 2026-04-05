from csv import reader
from datetime import datetime
from pathlib import Path
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    _base_dir = Path(__file__).resolve().parent

    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename
        self._current_index = 0
        self._is_reading = False
        self._accelerometer_file = None
        self._gps_file = None
        self._accelerometer_reader = None
        self._gps_reader = None

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        if not self._is_reading:
            self.startReading()

        accelerometer = self._read_next_accelerometer()
        gps = self._read_next_gps()
        self._current_index += 1

        return AggregatedData(
            accelerometer,
            gps,
            datetime.now(),
            config.USER_ID,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        self.stopReading()
        self._accelerometer_file, self._accelerometer_reader = self._open_reader(
            self.accelerometer_filename
        )
        self._gps_file, self._gps_reader = self._open_reader(self.gps_filename)
        self._current_index = 0
        self._is_reading = True

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        if self._accelerometer_file is not None:
            self._accelerometer_file.close()
        if self._gps_file is not None:
            self._gps_file.close()

        self._accelerometer_file = None
        self._gps_file = None
        self._accelerometer_reader = None
        self._gps_reader = None
        self._is_reading = False

    def _open_reader(self, filename: str):
        file_path = self._base_dir / filename
        file = open(file_path, newline="", encoding="utf-8")
        csv_reader = reader(file)
        next(csv_reader, None)
        return file, csv_reader

    def _read_next_accelerometer(self) -> Accelerometer:
        try:
            x, y, z = next(self._accelerometer_reader)
        except StopIteration:
            self._accelerometer_file.close()
            self._accelerometer_file, self._accelerometer_reader = self._open_reader(
                self.accelerometer_filename
            )
            x, y, z = next(self._accelerometer_reader)
        return Accelerometer(int(x), int(y), int(z))

    def _read_next_gps(self) -> Gps:
        try:
            longitude, latitude = next(self._gps_reader)
        except StopIteration:
            self._gps_file.close()
            self._gps_file, self._gps_reader = self._open_reader(self.gps_filename)
            longitude, latitude = next(self._gps_reader)
        return Gps(float(longitude), float(latitude))
