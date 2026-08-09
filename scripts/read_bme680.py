import time

from air_monitor.sensors.bme680 import BME680Sensor


def main() -> None:
    sensor = BME680Sensor(address=0x77)

    print("BME680 online at 0x77")

    while True:
        reading = sensor.read()

        print(
            f"{reading.timestamp.isoformat()} | "
            f"Temp: {reading.temperature_c:.2f} C | "
            f"Humidity: {reading.humidity_percent:.2f}% | "
            f"Pressure: {reading.pressure_hpa:.2f} hPa | "
            f"Gas: {reading.gas_resistance_kohms:.2f} kOhm"
        )

        time.sleep(2)


if __name__ == "__main__":
    main()
