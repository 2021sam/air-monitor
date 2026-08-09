from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

import board
import busio
import adafruit_bme680


@dataclass(frozen=True)
class BME680Reading:
    timestamp: datetime
    temperature_c: float
    humidity_percent: float
    pressure_hpa: float
    gas_resistance_ohms: float

    @property
    def gas_resistance_kohms(self) -> float:
        return self.gas_resistance_ohms / 1000.0


class BME680Sensor:
    def __init__(self, address: int = 0x77) -> None:
        self.address = address

        i2c = busio.I2C(board.SCL, board.SDA)

        self._sensor = adafruit_bme680.Adafruit_BME680_I2C(
            i2c,
            address=self.address,
        )

    def read(self) -> BME680Reading:
        return BME680Reading(
            timestamp=datetime.now(timezone.utc),
            temperature_c=float(self._sensor.temperature),
            humidity_percent=float(self._sensor.relative_humidity),
            pressure_hpa=float(self._sensor.pressure),
            gas_resistance_ohms=float(self._sensor.gas),
        )
