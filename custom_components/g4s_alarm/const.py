"""Constants for the G4S integration."""

from datetime import timedelta
import logging

from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_DISARMED,
    STATE_ALARM_PENDING,
    STATE_ALARM_ARMED_NIGHT,
)

DOMAIN = "g4s_alarm"

LOGGER = logging.getLogger(__package__)

CONF_GIID = "giid"
# CONF_SCAN_INTERVAL = "scan_interval"
CONF_LOCK_CODE_DIGITS = "lock_code_digits"
CONF_LOCK_DEFAULT_CODE = "lock_default_code"

DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
DEFAULT_LOCK_CODE_DIGITS = 4

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
