"""DataUpdateCoordinator for the G4S integration."""
from __future__ import annotations

from datetime import timedelta

from g4s import Alarm
from g4s.utils.enums import DeviceType

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.core import Event, HomeAssistant
from homeassistant.helpers.storage import STORAGE_DIR
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import Throttle

from .const import CONF_GIID, DEFAULT_SCAN_INTERVAL, DOMAIN, LOGGER


class G4sDataUpdateCoordinator(DataUpdateCoordinator):
    """A G4S Data Update Coordinator."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the G4S hub."""
        self.entry = entry

        self.alarm = Alarm(
            username=entry.data[CONF_EMAIL],
            password=entry.data[CONF_PASSWORD]        
        )

        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=DEFAULT_SCAN_INTERVAL
        )

    def validate_code(self, code) -> bool:
        return code is not None and len([user for user in self.alarm.users if user.access_code == code]) > 0

    async def _async_update_data(self) -> dict:
        """Fetch data from G4S."""
        try:
            await self.hass.async_add_executor_job(
                self.alarm.update_status
            )
        except Exception as ex:
            LOGGER.error("Could not read overview, %s", ex)
            raise

        # Store data in a way Home Assistant can easily consume it
        return {
            "alarm": self.alarm.state.name,
            #"ethernet": overview.get("ethernetConnectedNow"),
            # "cameras": {
            #     device["deviceLabel"]: device
            #     for device in overview["customerImageCameras"]
            # },
            "climate": {
                device.name: device
                for device in self.alarm.sensors if device.temperature_level is not None
            },
            "door_window": {
                device.name: device
                for device in self.alarm.sensors if device.type == DeviceType.DOORWINDOWSENSOR
            },
            "panel": {
                device.name: device
                for device in self.alarm.sensors if device.type == DeviceType.PANEL
            }
            
            # "locks": {
            #     device["deviceLabel"]: device
            #     for device in overview["doorLockStatusList"]
            # },
            # "mice": {
            #     device["deviceLabel"]: device
            #     for device in overview["eventCounts"]
            #     if device["deviceType"] == "MOUSE1"
            # },
            # "smart_plugs": {
            #     device["deviceLabel"]: device for device in overview["smartPlugs"]
            # },
        }
