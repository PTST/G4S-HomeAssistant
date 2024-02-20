"""Support for G4S sensors."""
from __future__ import annotations
from typing import Dict

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, ATTR_BATTERY_LEVEL, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_GIID, DEVICE_TYPE_NAME, DOMAIN
from .coordinator import G4sDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up G4S sensors based on a config entry."""
    coordinator: G4sDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    sensors: list[Entity] = [
        G4sThermometer(coordinator, serial_number)
        for serial_number, values in coordinator.data["climate"].items()
        if values.temperature_level is not None
    ]

    async_add_entities(sensors)


class G4sThermometer(CoordinatorEntity, SensorEntity):
    """Representation of a G4S thermometer."""

    coordinator: G4sDataUpdateCoordinator

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(
        self, coordinator: G4sDataUpdateCoordinator, serial_number: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{serial_number}_temperature"
        self.serial_number = serial_number

    @property
    def name(self) -> str:
        """Return the name of the entity."""
        name = self.coordinator.data["climate"][self.serial_number].name
        return f"{name} Temperature"

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        device_type = self.coordinator.data["climate"][self.serial_number].type.name
        area = self.coordinator.data["climate"][self.serial_number].name
        return {
            "name": area,
            "suggested_area": area,
            "manufacturer": "G4S",
            "model": DEVICE_TYPE_NAME.get(device_type, device_type),
            "identifiers": {(DOMAIN, self.serial_number)},
            "via_device": (DOMAIN, self.coordinator.entry.data[CONF_GIID]),
        }

    @property
    def native_value(self) -> str | None:
        """Return the state of the entity."""
        return self.coordinator.data["climate"][self.serial_number].temperature_level

    
    @property
    def extra_state_attributes(self) -> Dict[str, int]:
        """Return the state of the entity."""
        battery_level = self.coordinator.data["climate"][self.serial_number].battery_level
        if not battery_level:
            return {}
        return {ATTR_BATTERY_LEVEL: battery_level}


    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        return (
            super().available
            and self.serial_number in self.coordinator.data["climate"]
            and self.coordinator.data["climate"][self.serial_number].temperature_level is not None
        )
