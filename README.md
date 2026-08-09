# Air Monitor

Raspberry Pi air-quality monitoring and environmental sensing platform.

## Hardware

- Raspberry Pi 4
- Bosch BME680 over I2C
- BME680 address: 0x77

## Measurements

- Temperature
- Relative humidity
- Atmospheric pressure
- Gas resistance

## Planned

- Sensor abstraction layer
- Rolling air-quality baseline
- Gas-resistance anomaly detection
- PM2.5 particulate sensing
- SQLite historical logging
- Home Assistant integration
- MQTT publishing
- Configurable alerts
- systemd service
- Health monitoring
