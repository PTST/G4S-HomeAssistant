"""Support for G4S binary sensors."""

from __future__ import annotations
from typing import Dict

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import ATTR_BATTERY_LEVEL
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_GIID, DOMAIN
from .coordinator import G4sDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up G4S binary sensors based on a config entry."""
    coordinator: G4sDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = [
        G4sDoorWindowSensor(coordinator, serial_number)
        for serial_number in coordinator.data["door_window"]
    ]

    async_add_entities(sensors)


class G4sDoorWindowSensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a G4S door window sensor."""

    coordinator: G4sDataUpdateCoordinator

    _attr_device_class = BinarySensorDeviceClass.OPENING

    def __init__(
        self, coordinator: G4sDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the G4S door window sensor."""
        super().__init__(coordinator)
        self._attr_name = coordinator.data["door_window"][serial_number].name
        self._attr_unique_id = f"{serial_number}_door_window"
        self.serial_number = serial_number

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        area = self.coordinator.data["door_window"][self.serial_number].name
        return {
            "name": area,
            "suggested_area": area,
            "manufacturer": "G4S",
            "model": "Door Window Sensor",
            "identifiers": {(DOMAIN, self.serial_number)},
            "via_device": (DOMAIN, self.coordinator.entry.data[CONF_GIID]),
        }

    @property
    def is_on(self) -> bool:
        """Return the state of the sensor."""
        return self.coordinator.data["door_window"][self.serial_number].is_open

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.serial_number in self.coordinator.data["door_window"]
        )

    @property
    def extra_state_attributes(self) -> Dict[str, int]:
        """Return the state of the entity."""
        battery_level = self.coordinator.data["climate"][
            self.serial_number
        ].battery_level
        if not battery_level:
            return {}
        return {ATTR_BATTERY_LEVEL: battery_level}
