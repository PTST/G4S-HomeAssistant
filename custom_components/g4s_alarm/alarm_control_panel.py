"""Support for G4S alarm control panels."""
from __future__ import annotations

import asyncio
from typing import Dict

from homeassistant.components.alarm_control_panel import (
    AlarmControlPanelEntity,
    AlarmControlPanelEntityFeature,
    CodeFormat,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.const import ATTR_BATTERY_LEVEL

from .const import ALARM_STATE_TO_HA, CONF_GIID, DOMAIN, LOGGER
from .coordinator import G4sDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up G4S alarm control panel from a config entry."""
    async_add_entities([G4sAlarm(coordinator=hass.data[DOMAIN][entry.entry_id])])


class G4sAlarm(CoordinatorEntity, AlarmControlPanelEntity):
    """Representation of a G4S alarm status."""

    coordinator: G4sDataUpdateCoordinator

    _attr_code_format = CodeFormat.NUMBER
    _attr_name = "G4S Alarm"
    _attr_supported_features = AlarmControlPanelEntityFeature.ARM_NIGHT | AlarmControlPanelEntityFeature.ARM_AWAY
    _attr_code_arm_required: bool = False


    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this entity."""
        return {
            "name": "G4S Alarm",
            "manufacturer": "G4S",
            "model": "Alarm",
            "identifiers": {(DOMAIN, self.coordinator.entry.data[CONF_GIID])},
        }

    @property
    def unique_id(self) -> str:
        """Return the unique ID for this entity."""
        return self.coordinator.entry.data[CONF_GIID]

    async def _async_set_arm_state(self, state: str, code: str | None = None) -> None:
        """Send set arm state command."""
        if state == "ARMED_NIGHT":
            arm_state = await self.hass.async_add_executor_job(
                self.coordinator.alarm.night_arm
            )
        elif state == "ARMED_AWAY":
            arm_state = await self.hass.async_add_executor_job(
                self.coordinator.alarm.arm
            )
        elif state == "DISARMED":
            if self.coordinator.validate_code(code):
                arm_state = await self.hass.async_add_executor_job(
                    self.coordinator.alarm.disarm
                )
        LOGGER.debug("G4S set arm state %s", state)
        await self.coordinator.async_refresh()

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        await self._async_set_arm_state("DISARMED", code)

    async def async_alarm_arm_night(self, code: str | None = None) -> None:
        """Send arm home command."""
        await self._async_set_arm_state("ARMED_NIGHT")

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        await self._async_set_arm_state("ARMED_AWAY")

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_state = ALARM_STATE_TO_HA.get(
            self.coordinator.alarm.state.name
        )
        try:
            self._attr_changed_by = self.coordinator.alarm.last_state_change_by.name
        except AttributeError:
            LOGGER.info("Could not find user for last change")
        super()._handle_coordinator_update()

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
    
    @property
    def extra_state_attributes(self) -> Dict[str, int]:
        """Return the state of the entity."""
        battery_level = None
        for _, panel in self.coordinator.data["panel"].items():
            battery_level = panel.battery_level
        if not battery_level:
            return {}
        return {ATTR_BATTERY_LEVEL: battery_level}
