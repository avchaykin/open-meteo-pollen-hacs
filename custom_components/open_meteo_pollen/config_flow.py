from __future__ import annotations

import logging
from typing import Any
from urllib.parse import quote_plus

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_ADDRESS,
    CONF_LATITUDE,
    CONF_LOCATION_NAME,
    CONF_LONGITUDE,
    CONF_TIMEZONE,
    DEFAULT_TIMEZONE,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)


class OpenMeteoPollenConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        errors: dict[str, str] = {}

        if user_input is not None:
            address = user_input[CONF_ADDRESS].strip()
            timezone = user_input[CONF_TIMEZONE].strip() or DEFAULT_TIMEZONE

            try:
                geo = await _geocode_address(self.hass, address)
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_resolve_address"
            else:
                title = geo["name"]
                await self.async_set_unique_id(f"{geo['latitude']:.5f},{geo['longitude']:.5f}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data={
                        CONF_ADDRESS: address,
                        CONF_LATITUDE: geo["latitude"],
                        CONF_LONGITUDE: geo["longitude"],
                        CONF_LOCATION_NAME: title,
                        CONF_TIMEZONE: timezone,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_ADDRESS): str,
                vol.Optional(CONF_TIMEZONE, default=DEFAULT_TIMEZONE): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


async def _geocode_address(hass, address: str) -> dict[str, Any]:
    session = async_get_clientsession(hass)
    encoded = quote_plus(address)
    url = (
        "https://geocoding-api.open-meteo.com/v1/search"
        f"?name={encoded}&count=1&language=en&format=json"
    )

    resp = await session.get(url, timeout=20)
    resp.raise_for_status()
    data = await resp.json()

    results = data.get("results") or []
    if not results:
        raise ValueError("No results")

    result = results[0]
    name_parts = [result.get("name"), result.get("admin1"), result.get("country")]
    title = ", ".join([p for p in name_parts if p])

    return {
        "name": title,
        "latitude": float(result["latitude"]),
        "longitude": float(result["longitude"]),
    }
