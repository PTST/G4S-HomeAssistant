"""Constants for the G4S integration."""

import logging
from datetime import timedelta

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_NIGHT,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
)

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
    "DISARMED": STATE_ALARM_DISARMED,
    "NIGHT_ARM": STATE_ALARM_ARMED_NIGHT,
    "FULL_ARM": STATE_ALARM_ARMED_AWAY,
    "PENDING_ARM": STATE_ALARM_PENDING,
}
