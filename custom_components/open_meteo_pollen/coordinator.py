from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class OpenMeteoPollenCoordinator(DataUpdateCoordinator[dict]):
    def __init__(self, hass: HomeAssistant, *, latitude: float, longitude: float, timezone: str) -> None:
        self._session = async_get_clientsession(hass)
        self.latitude = latitude
        self.longitude = longitude
        self.timezone = timezone
        super().__init__(
            hass,
            _LOGGER,
            name="Open-Meteo Pollen",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )

    async def _async_update_data(self) -> dict:
        url = (
            "https://air-quality-api.open-meteo.com/v1/air-quality"
            f"?latitude={self.latitude}"
            f"&longitude={self.longitude}"
            "&current=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen,european_aqi"
            "&hourly=alder_pollen,birch_pollen,grass_pollen,mugwort_pollen,olive_pollen,ragweed_pollen,european_aqi"
            "&forecast_days=3"
            f"&timezone={self.timezone}"
        )

        try:
            resp = await self._session.get(url, timeout=20)
            resp.raise_for_status()
            data = await resp.json()
        except Exception as err:
            raise UpdateFailed(f"Open-Meteo request failed: {err}") from err

        return data
