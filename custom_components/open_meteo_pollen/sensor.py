from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTR_UPDATED_AT,
    CONF_LOCATION_NAME,
    DOMAIN,
)
from .coordinator import OpenMeteoPollenCoordinator


@dataclass(frozen=True, kw_only=True)
class OpenMeteoPollenSensorDescription(SensorEntityDescription):
    key_in_payload: str


SENSORS: tuple[OpenMeteoPollenSensorDescription, ...] = (
    OpenMeteoPollenSensorDescription(
        key="alder_pollen",
        key_in_payload="alder_pollen",
        name="Alder Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="birch_pollen",
        key_in_payload="birch_pollen",
        name="Birch Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="grass_pollen",
        key_in_payload="grass_pollen",
        name="Grass Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="mugwort_pollen",
        key_in_payload="mugwort_pollen",
        name="Mugwort Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="olive_pollen",
        key_in_payload="olive_pollen",
        name="Olive Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="ragweed_pollen",
        key_in_payload="ragweed_pollen",
        name="Ragweed Pollen",
        icon="mdi:flower-pollen",
        native_unit_of_measurement="grains/m³",
    ),
    OpenMeteoPollenSensorDescription(
        key="european_aqi",
        key_in_payload="european_aqi",
        name="European AQI",
        icon="mdi:air-filter",
        native_unit_of_measurement="EAQI",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = OpenMeteoPollenCoordinator(
        hass,
        latitude=float(entry.data["latitude"]),
        longitude=float(entry.data["longitude"]),
        timezone=str(entry.data["timezone"]),
    )
    await coordinator.async_config_entry_first_refresh()

    location_name = str(entry.data.get(CONF_LOCATION_NAME, "Location"))

    entities: list[OpenMeteoPollenSensor] = [
        OpenMeteoPollenSensor(coordinator, entry, description, location_name)
        for description in SENSORS
    ]

    entities.extend(
        [
            OpenMeteoMaxPollenNext24hSensor(coordinator, entry, location_name),
            OpenMeteoDominantPollenNext24hSensor(coordinator, entry, location_name),
        ]
    )

    async_add_entities(entities)


class OpenMeteoPollenSensor(CoordinatorEntity[OpenMeteoPollenCoordinator], SensorEntity):
    entity_description: OpenMeteoPollenSensorDescription

    def __init__(
        self,
        coordinator: OpenMeteoPollenCoordinator,
        entry: ConfigEntry,
        description: OpenMeteoPollenSensorDescription,
        location_name: str,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"{location_name} {description.name}"

    @property
    def native_value(self) -> Any:
        current = self.coordinator.data.get("current", {})
        return current.get(self.entity_description.key_in_payload)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        current = self.coordinator.data.get("current", {})
        return {ATTR_UPDATED_AT: current.get("time")}


class OpenMeteoMaxPollenNext24hSensor(CoordinatorEntity[OpenMeteoPollenCoordinator], SensorEntity):
    _attr_icon = "mdi:chart-line"
    _attr_native_unit_of_measurement = "grains/m³"

    def __init__(self, coordinator: OpenMeteoPollenCoordinator, entry: ConfigEntry, location_name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_max_pollen_next_24h"
        self._attr_name = f"{location_name} Max Pollen Next 24h"

    @property
    def native_value(self) -> float:
        hourly = self.coordinator.data.get("hourly", {})
        max_value = 0.0
        for key in (
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ):
            values = hourly.get(key, [])[:24]
            if values:
                max_value = max(max_value, max(float(v) for v in values))
        return round(max_value, 2)


class OpenMeteoDominantPollenNext24hSensor(CoordinatorEntity[OpenMeteoPollenCoordinator], SensorEntity):
    _attr_icon = "mdi:flower"

    def __init__(self, coordinator: OpenMeteoPollenCoordinator, entry: ConfigEntry, location_name: str) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_dominant_pollen_next_24h"
        self._attr_name = f"{location_name} Dominant Pollen Next 24h"

    @property
    def native_value(self) -> str:
        hourly = self.coordinator.data.get("hourly", {})
        best_name = "none"
        best_value = -1.0
        for key in (
            "alder_pollen",
            "birch_pollen",
            "grass_pollen",
            "mugwort_pollen",
            "olive_pollen",
            "ragweed_pollen",
        ):
            values = hourly.get(key, [])[:24]
            local_max = max((float(v) for v in values), default=0.0)
            if local_max > best_value:
                best_value = local_max
                best_name = key
        return best_name
