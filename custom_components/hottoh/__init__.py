"""The HottoH integration."""

from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
import async_timeout

from homeassistant import exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_HOST,
    CONF_PORT,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
)

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import Entity

from .const import DOMAIN, PLATFORMS, HOTTOH_SESSION, CANCEL_STOP
from hottohpy import Hottoh, HottohConnectionError

_LOGGER = logging.getLogger(__name__)

# async def async_setup(hass: HomeAssistant, config: dict):
#     """Set up the Hottoh component."""
#     hass.data.setdefault(DOMAIN, {})
#     return True


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up HottoH from a config entry."""

    hottoh = Hottoh(
        address=config_entry.data[CONF_HOST],
        port=config_entry.data[CONF_PORT],
    )

    try:
        if not await async_connect_or_timeout(hass, hottoh):
            return False
    except CannotConnect as err:
        raise exceptions.ConfigEntryNotReady from err

    async def _async_disconnect_hottoh(event):
        await async_disconnect_or_timeout(hass, hottoh)

    cancel_stop = hass.bus.async_listen_once(
        EVENT_HOMEASSISTANT_STOP, _async_disconnect_hottoh
    )

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][config_entry.entry_id] = {
        HOTTOH_SESSION: hottoh,
        CANCEL_STOP: cancel_stop,
    }

    for component in PLATFORMS:
        hass.async_create_task(
            hass.config_entries.async_forward_entry_setups(config_entry, component)
        )

    if not config_entry.update_listeners:
        config_entry.add_update_listener(async_update_options)

    def stoveSetTemperature(call) -> None:
        """Set Stove Temperature."""
        hottoh.set_temperature(call.data["value"])

    def stoveSetPowerLevel(call) -> None:
        """Set Stove Power Level."""
        hottoh.set_power_level(call.data["value"])

    def stoveSetSpeedFan1(call) -> None:
        """Set Stove Fan 1 Speed."""
        hottoh.set_speed_fan_1(call.data["value"])

    def stoveSetSpeedFan2(call) -> None:
        """Set Stove Fan 2 Speed."""
        hottoh.set_speed_fan_2(call.data["value"])

    def stoveSetSpeedFan3(call) -> None:
        """Set Stove Fan 3 Speed."""
        hottoh.set_speed_fan_3(call.data["value"])

    def stoveSetEcoModeOn(call) -> None:
        """Set Stove Eco Mode On."""
        hottoh.set_eco_mode_on()

    def stoveSetEcoModeOff(call) -> None:
        """Set Stove Eco Mode Off."""
        hottoh.set_eco_mode_off()

    def stoveSetChronoModeOn(call) -> None:
        """Set Stove Chrono Mode On."""
        hottoh.set_chrono_mode_on()

    def stoveSetChronoModeOff(call) -> None:
        """Set Stove Chrono Mode Off."""
        hottoh.set_chrono_mode_off()

    def stoveSetOn(call) -> None:
        """Set Stove On."""
        hottoh.set_on()

    def stoveSetOff(call) -> None:
        """Set Stove Off."""
        hottoh.set_off()

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "set_temperature", stoveSetTemperature)
    hass.services.async_register(DOMAIN, "set_power_level", stoveSetPowerLevel)
    hass.services.async_register(DOMAIN, "eco_mode_turn_on", stoveSetEcoModeOn)
    hass.services.async_register(DOMAIN, "eco_mode_turn_off", stoveSetEcoModeOff)
    hass.services.async_register(DOMAIN, "chrono_mode_turn_on", stoveSetChronoModeOn)
    hass.services.async_register(DOMAIN, "chrono_mode_turn_off", stoveSetChronoModeOff)
    hass.services.async_register(DOMAIN, "turn_on", stoveSetOn)
    hass.services.async_register(DOMAIN, "turn_off", stoveSetOff)

    if hottoh.getFanNumber() == 1:
        hass.services.async_register(DOMAIN, "set_speed_fan_1", stoveSetSpeedFan1)
    if hottoh.getFanNumber() == 2:
        hass.services.async_register(DOMAIN, "set_speed_fan_1", stoveSetSpeedFan1)
        hass.services.async_register(DOMAIN, "set_speed_fan_2", stoveSetSpeedFan2)
    if hottoh.getFanNumber() == 3:
        hass.services.async_register(DOMAIN, "set_speed_fan_1", stoveSetSpeedFan1)
        hass.services.async_register(DOMAIN, "set_speed_fan_2", stoveSetSpeedFan2)
        hass.services.async_register(DOMAIN, "set_speed_fan_3", stoveSetSpeedFan3)

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    for component in PLATFORMS:
        unload_ok = await hass.config_entries.async_forward_entry_unload(
            config_entry, component
        )

    if unload_ok:
        domain_data = hass.data[DOMAIN][config_entry.entry_id]
        domain_data[CANCEL_STOP]()
        await async_disconnect_or_timeout(hass, hottoh=domain_data[HOTTOH_SESSION])
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok


async def async_connect_or_timeout(hass, hottoh):
    """Connect to HottoH."""
    try:
        name = None
        with async_timeout.timeout(10):
            _LOGGER.debug("Initialize connection to Hottoh")
            if not hottoh.is_connected():
                await hass.async_add_executor_job(hottoh.connect)
            while not hottoh.is_connected() or name is None:
                # Waiting for connection and check datas ready
                name = hottoh.get_name()
                if name:
                    break
                await asyncio.sleep(1)

            name = hottoh.get_name()

    except HottohConnectionError as err:
        _LOGGER.debug("Error to connect to Hottoh: %s", err)
        raise CannotConnect from err
    except asyncio.TimeoutError as err:
        # api looping if address or port incorrect and hottoh exist
        await async_disconnect_or_timeout(hass, hottoh)
        _LOGGER.debug("Timeout expired: %s", err)
        raise CannotConnect from err

    return {HOTTOH_SESSION: hottoh, CONF_NAME: name}


async def async_disconnect_or_timeout(hass, hottoh):
    """Disconnect to Hottoh."""
    _LOGGER.debug("Disconnect Hottoh")
    with async_timeout.timeout(3):
        await hass.async_add_executor_job(hottoh.disconnect)
    return True


async def async_update_options(hass, config_entry):
    """Update options."""
    await hass.config_entries.async_reload(config_entry.entry_id)


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class HottohEntity(Entity):
    SCAN_INTERVAL = timedelta(seconds=10)

    def __init__(self, hottoh):
        """Initialize the Climate."""
        Entity.__init__(self)
        self.api = hottoh

    @property
    def should_poll(self):
        return True

    @property
    def available(self):
        return self.api.is_connected()

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {(DOMAIN, self.api.get_name())},
            "name": self.api.get_name(),
            "sw_version": self.api.get_firmware(),
            "model": self.api.get_manufacturer(),
            "manufacturer": self.api.get_manufacturer(),
        }
