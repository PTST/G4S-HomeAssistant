"""Support for G4S devices."""
from __future__ import annotations

from contextlib import suppress
import os
from g4s import Alarm
from homeassistant.components.alarm_control_panel import (
    DOMAIN as ALARM_CONTROL_PANEL_DOMAIN,
)
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.camera import DOMAIN as CAMERA_DOMAIN
from homeassistant.components.lock import DOMAIN as LOCK_DOMAIN
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EVENT_HOMEASSISTANT_STOP
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.storage import STORAGE_DIR

from .const import DOMAIN
from .coordinator import G4sDataUpdateCoordinator

PLATFORMS = [
    ALARM_CONTROL_PANEL_DOMAIN,
    BINARY_SENSOR_DOMAIN,
    # CAMERA_DOMAIN,
    # LOCK_DOMAIN,
    SENSOR_DOMAIN,
    # SWITCH_DOMAIN,
]

CONFIG_SCHEMA = cv.deprecated(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up G4S from a config entry."""
    coordinator = G4sDataUpdateCoordinator(hass, entry=entry)

    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Set up all platforms for this device/entry.
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload G4S config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if not unload_ok:
        return False

    del hass.data[DOMAIN][entry.entry_id]

    if not hass.data[DOMAIN]:
        del hass.data[DOMAIN]

    return True