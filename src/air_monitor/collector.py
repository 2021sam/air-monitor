import asyncio
import time

from air_monitor.sensors.bme680 import BME680Sensor
from air_monitor.settings import load_settings
from air_monitor.storage import insert_reading


class Collector:
    def __init__(self):
        self.sensor = BME680Sensor(address=0x77)
        self.latest = None
        self.started_at = time.monotonic()

    async def run(self):
        while True:
            settings = load_settings()
            poll_seconds = max(float(settings["poll_seconds"]), 0.5)
            warmup_seconds = max(float(settings["warmup_seconds"]), 0)

            reading = self.sensor.read()
            self.latest = reading

            elapsed = time.monotonic() - self.started_at

            if elapsed >= warmup_seconds:
                insert_reading(reading)

            await asyncio.sleep(poll_seconds)
