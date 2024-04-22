"""DataUpdateCoordinator for the G4S integration."""
from __future__ import annotations

from datetime import timedelta

from g4s import Alarm
from g4s.utils.enums import DeviceType

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
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

        update_interval = DEFAULT_SCAN_INTERVAL if self.entry.data.get(CONF_SCAN_INTERVAL) is None else timedelta(seconds=self.entry.data.get(CONF_SCAN_INTERVAL))

        super().__init__(
            hass, LOGGER, name=DOMAIN, update_interval=update_interval
        )

    def validate_code(self, code) -> bool:
        valid_user_code = len([user for user in self.alarm.users if user.access_code == code]) > 0
        valid_chip_code = len([chip.name for chip in self.alarm.sensors if chip.type == DeviceType.ACCESSCHIP and chip.access_code is not None and chip.access_code == code]) > 0
        LOGGER.info("Valid user code: %s", valid_user_code)
        LOGGER.info("Valid access chip code: %s", valid_chip_code)
        return code is not None and (valid_user_code or valid_chip_code)

    async def _async_update_data(self) -> dict:
        """Fetch data from G4S."""
        try:
            LOGGER.warn("updating data")
            await self.hass.async_add_executor_job(
                self.alarm.update_status
            )
            LOGGER.warn("got new data")
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
