"""Config flow for HottoH CMG integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.components.dhcp import IP_ADDRESS, MAC_ADDRESS
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import DOMAIN, HOTTOH_DEFAULT_HOST, HOTTOH_DEFAULT_PORT, HOTTOH_SESSION, CONF_AWAY_TEMP, CONF_COMFORT_TEMP, CONF_ECO_TEMP
from hottohpy import Hottoh
from . import CannotConnect, async_connect_or_timeout, async_disconnect_or_timeout

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST, default=HOTTOH_DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=HOTTOH_DEFAULT_PORT): int,
        vol.Required(CONF_AWAY_TEMP, default=15.00): vol.Coerce(float),
        vol.Required(CONF_COMFORT_TEMP, default=20.00): vol.Coerce(float),
        vol.Required(CONF_ECO_TEMP, default=18.00): vol.Coerce(float),
    }
)

def hottoh_config_shema(options: dict = {}) -> dict:
    """Return a schema for Hottoh configuration options."""
    if not options:
        options = {
            CONF_HOST: HOTTOH_DEFAULT_HOST,
            CONF_PORT: HOTTOH_DEFAULT_PORT,
            CONF_AWAY_TEMP: 15.00,
            CONF_COMFORT_TEMP: 20.00,
            CONF_ECO_TEMP: 18.00
        }
    
    return {
        vol.Required(CONF_HOST, default=options.get(CONF_HOST, HOTTOH_DEFAULT_HOST)): str,
        vol.Required(CONF_PORT, default=options.get(CONF_PORT, HOTTOH_DEFAULT_PORT)): int,
        vol.Optional(CONF_AWAY_TEMP, default=options.get(CONF_AWAY_TEMP)): vol.Coerce(float),
        vol.Optional(CONF_COMFORT_TEMP, default=options.get(CONF_COMFORT_TEMP)): vol.Coerce(float),
        vol.Optional(CONF_ECO_TEMP, default=options.get(CONF_ECO_TEMP)): vol.Coerce(float),
    }

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    hottoh = Hottoh(
        address=data[CONF_HOST],
        port=data[CONF_PORT]
    )

    info = await async_connect_or_timeout(hass, hottoh)
    
    # await async_disconnect_or_timeout(hass, hottoh)

    return {
        HOTTOH_SESSION: hottoh,
        CONF_NAME: info[CONF_NAME],
        CONF_HOST: data[CONF_HOST],
        CONF_AWAY_TEMP: data[CONF_AWAY_TEMP],
        CONF_COMFORT_TEMP: data[CONF_COMFORT_TEMP],
        CONF_ECO_TEMP: data[CONF_ECO_TEMP]
    }


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for HottoH"""

    VERSION = 1

    async def async_step_user(self, user_input) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )
        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info[CONF_NAME], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return HottohOptionsFlowHandler(config_entry)

class HottohOptionsFlowHandler(config_entries.OptionsFlow):
    """Hottoh config flow options handler."""

    def __init__(self, config_entry):
        """Initialize Hottoh options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        return await self.async_step_user()

    async def async_step_user(self, user_input=None):
        """Handle a flow initialized by the user."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = hottoh_config_shema(self.config_entry.options)

        return self.async_show_form(step_id="user", data_schema=vol.Schema(schema))

class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
