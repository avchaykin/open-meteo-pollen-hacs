# Open-Meteo Pollen (Home Assistant)

Custom Home Assistant integration that provides pollen and air quality sensors from Open-Meteo for a configurable city/address.

## Features

- Config flow in UI (enter city/address)
- Hourly polling from Open-Meteo Air Quality API
- Config-entry reload support (changes can be applied without full HA restart)
- Sensors:
  - Alder Pollen
  - Birch Pollen
  - Grass Pollen
  - Mugwort Pollen
  - Olive Pollen
  - Ragweed Pollen
  - European AQI
  - Max Pollen Next 24h
  - Dominant Pollen Next 24h

## Installation (HACS)

1. HACS → Integrations → ⋮ → **Custom repositories**
2. Add this repository URL
3. Category: **Integration**
4. Install **Open-Meteo Pollen**
5. Restart Home Assistant
6. Settings → Devices & Services → Add Integration → **Open-Meteo Pollen**

## Data source

- Open-Meteo Air Quality API: https://open-meteo.com/en/docs/air-quality-api

## Notes

- Pollen values are model-based forecasts from CAMS data provided via Open-Meteo.
