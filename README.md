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

## Start Air Monitor

After the Raspberry Pi is rebooted, powered off, or moved, start Air Monitor with:

    cd /home/x/apps/air-monitor
    source .venv/bin/activate
    PYTHONPATH=src uvicorn air_monitor.web:app --host 0.0.0.0 --port 8100

Or as one command:

    cd /home/x/apps/air-monitor && source .venv/bin/activate && PYTHONPATH=src uvicorn air_monitor.web:app --host 0.0.0.0 --port 8100

The dashboard listens on port 8100.

## Verify BME680

The sensor should appear at address 0x77:

    sudo i2cdetect -y 1

## Check Whether Air Monitor Is Running

    ps aux | grep -Ei 'air.monitor|air_monitor|uvicorn' | grep -v grep

## Planned

- Rolling air-quality baseline
- Gas-resistance anomaly detection
- PM2.5 particulate sensing
- Home Assistant integration
- MQTT publishing
- Configurable alerts
- systemd service
- Health monitoring
