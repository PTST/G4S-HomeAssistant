"""Config flow for G4S integration."""
from __future__ import annotations

from typing import Any

from datetime import timedelta

from g4s import Alarm
from .const import DEFAULT_SCAN_INTERVAL

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_GIID,
    CONF_LOCK_CODE_DIGITS,
    CONF_LOCK_DEFAULT_CODE,
    DEFAULT_LOCK_CODE_DIGITS,
    DOMAIN,
    LOGGER,
)

class G4SOptionsFlowHandler(OptionsFlow):
    def __init__(self, entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self.entry = entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            for k, v in self.entry.data.items():
                if k not in user_input.keys():
                    user_input[k] = v
            self.hass.config_entries.async_update_entry(
                self.entry, data=user_input, options=self.entry.options
            )
            self.async_abort(reason="configuration updated")
            return self.async_create_entry(title="", data={})

        default_scan_interval = DEFAULT_SCAN_INTERVAL
        if self.entry.data.get(CONF_SCAN_INTERVAL) is not None:
            default_scan_interval = timedelta(seconds=int(self.entry.data.get(CONF_SCAN_INTERVAL)))
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_SCAN_INTERVAL, default=default_scan_interval.total_seconds): int
                }
            ),
        )


class G4SConfigFlowHandler(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for G4S."""

    VERSION = 1

    email: str
    entry: ConfigEntry
    installations: dict[str, str]
    password: str

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            alarm = Alarm(username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD])
            try:
                await self.hass.async_add_executor_job(alarm.update_status)
            except Exception as ex:
                LOGGER.debug("Could not log in to G4S, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                self.email = user_input[CONF_EMAIL]
                self.password = user_input[CONF_PASSWORD]
                self.installations = {
                    str(alarm.status.panel_id): alarm.status.name
                }
                return await self.async_step_installation()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    async def async_step_installation(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Select Verisure installation to add."""
        if len(self.installations) == 1:
            user_input = {CONF_GIID: list(self.installations)[0]}

        if user_input is None:
            return self.async_show_form(
                step_id="installation",
                data_schema=vol.Schema(
                    {vol.Required(CONF_GIID): vol.In(self.installations)}
                ),
            )

        await self.async_set_unique_id(user_input[CONF_GIID])
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
            title=self.installations[user_input[CONF_GIID]],
            data={
                CONF_EMAIL: self.email,
                CONF_PASSWORD: self.password,
                CONF_GIID: user_input[CONF_GIID],
            },
        )

    async def async_step_reauth(self, data: dict[str, Any]) -> FlowResult:
        """Handle initiation of re-authentication with Verisure."""
        self.entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle re-authentication with Verisure."""
        errors: dict[str, str] = {}

        if user_input is not None:
            alarm = Alarm(username=user_input[CONF_EMAIL], password=user_input[CONF_PASSWORD])
            try:
                await self.hass.async_add_executor_job(alarm.update_status)
            except Exception as ex:
                LOGGER.debug("Could not log in to Verisure, %s", ex)
                errors["base"] = "invalid_auth"
            else:
                data = self.entry.data.copy()
                self.hass.config_entries.async_update_entry(
                    self.entry,
                    data={
                        **data,
                        CONF_EMAIL: user_input[CONF_EMAIL],
                        CONF_PASSWORD: user_input[CONF_PASSWORD],
                    },
                )
                self.hass.async_create_task(
                    self.hass.config_entries.async_reload(self.entry.entry_id)
                )
            return self.async_abort(reason="reauth_successful")

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL, default=self.entry.data[CONF_EMAIL]): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ) -> OptionsFlow:
        """Create the options flow."""
        return G4SOptionsFlowHandler(config_entry)
