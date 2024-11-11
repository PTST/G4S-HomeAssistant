"""Constants for the G4S integration."""

import logging
from datetime import timedelta

from homeassistant.components.alarm_control_panel import AlarmControlPanelState

DOMAIN = "g4s_alarm"

LOGGER = logging.getLogger(__package__)

CONF_GIID = "giid"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)

# Mapping of device types to a human readable name
DEVICE_TYPE_NAME = {
    "CAMERAPIR2": "Camera detector",
    "HOMEPAD1": "VoiceBox",
    "HUMIDITY1": "Climate sensor",
    "PIR2": "Camera detector",
    "SIREN1": "Siren",
    "SMARTCAMERA1": "SmartCam",
    "SMOKE2": "Smoke detector",
    "SMOKE3": "Smoke detector",
    "VOICEBOX1": "VoiceBox",
    "WATER1": "Water detector",
}

ALARM_STATE_TO_HA = {
    "DISARMED": AlarmControlPanelState.DISARMED,
    "NIGHT_ARM": AlarmControlPanelState.ARMED_NIGHT,
    "FULL_ARM": AlarmControlPanelState.ARMED_AWAY,
    "PENDING_ARM": AlarmControlPanelState.ARMING,
}
