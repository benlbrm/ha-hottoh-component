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
    EVENT_HOMEASSISTANT_STOP
    )

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    DOMAIN, 
    PLATFORMS,
    HOTTOH_SESSION,
    CANCEL_STOP
)
from hottohpy import (
    Hottoh, 
    HottohConnectionError
)

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Hottoh component."""
    hass.data.setdefault(DOMAIN, {})
    return True

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
            hass.config_entries.async_forward_entry_setup(config_entry, component)
        )

    if not config_entry.update_listeners:
        config_entry.add_update_listener(async_update_options)

    def stoveSetTemperature(call) -> None:
        """Set Stove Temperature."""
        hottoh.setTemperature(call.data["value"])

    def stoveSetPowerLevel(call) -> None:
        """Set Stove Power Level."""
        hottoh.setPowerLevel(call.data["value"])

    def stoveSetEcoModeOn(call) -> None:
        """Set Stove Eco Mode On."""
        hottoh.setEcoModeOn()

    def stoveSetEcoModeOff(call) -> None:
        """Set Stove Eco Mode Off."""
        hottoh.setEcoModeOff()

    def stoveSetChronoModeOn(call) -> None:
        """Set Stove Chrono Mode On."""
        hottoh.setEcoModeOn()

    def stoveSetChronoModeOff(call) -> None:
        """Set Stove Chrono Mode Off."""
        hottoh.setEcoModeOff()

    def stoveSetOn(call) -> None:
        """Set Stove On."""
        hottoh.setOn()

    def stoveSetOff(call) -> None:
        """Set Stove Off."""
        hottoh.setOff()

    # Register our service with Home Assistant.
    hass.services.async_register(DOMAIN, "set_temperature", stoveSetTemperature)
    hass.services.async_register(DOMAIN, "set_power_level", stoveSetPowerLevel)
    hass.services.async_register(DOMAIN, "eco_mode_turn_on", stoveSetEcoModeOn)
    hass.services.async_register(DOMAIN, "eco_mode_turn_off", stoveSetEcoModeOff)
    hass.services.async_register(DOMAIN, "chrono_mode_turn_on", stoveSetChronoModeOn)
    hass.services.async_register(DOMAIN, "chrono_mode_turn_off", stoveSetChronoModeOff)
    hass.services.async_register(DOMAIN, "turn_on", stoveSetOn)
    hass.services.async_register(DOMAIN, "turn_off", stoveSetOff)
    return True

async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    for component in PLATFORMS:
        unload_ok = await hass.config_entries.async_forward_entry_unload(config_entry, component)
                
    if unload_ok:
        domain_data = hass.data[DOMAIN][config_entry.entry_id]
        domain_data[CANCEL_STOP]()
        await async_disconnect_or_timeout(hass, hottoh=domain_data[HOTTOH_SESSION])
        hass.data[DOMAIN].pop(config_entry.entry_id)

    return unload_ok

# async def options_updated_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
#     """Handle options update."""
#     if entry.options[CONF_MANUAL]:
#         hass.data[DOMAIN].update_interval = None
#         return

#     hass.data[DOMAIN].update_interval = timedelta(
#         seconds=entry.options[CONF_SCAN_INTERVAL]
#     )
#     await hass.data[DOMAIN].async_request_refresh()

# class HottohDataCoordinator(DataUpdateCoordinator):
#     """Get the latest data from the Stove"""

#     def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry) -> None:
#         """Initialize the data object."""
#         self.hass = hass
#         self.config_entry = config_entry
#         self.api = Stove(config_entry.data[CONF_IP_ADDRESS], config_entry.data[CONF_PORT]) 
#         super().__init__(
#             self.hass,
#             _LOGGER,
#             name=DOMAIN,
#             update_method=self.update_data,
#             update_interval=timedelta(seconds=15),
#         )
    
#     async def initialize(self)->None:
#         "Initialize Hottoh Api"
#         self.api = Stove(config_entry.data[CONF_IP_ADDRESS], config_entry.data[CONF_PORT])
#         await self.api.refresh()

#     async def async_update(self) -> dict[str, str]:
#         """Update Stove data."""
#         return await self.hass.async_add_executor_job(self.update_data)

#     async def update_data(self):
#         """Get the latest data from the stove."""
#         data = await self.api.refresh()
#         _LOGGER.debug('Received data', data)
#         return data

#     async def async_setup(self) -> None:
#         """Set up Hottoh."""
#         await self.hass.async_add_executor_job(self.initialize)

#         async def stoveSetTemperature(call) -> None:
#             """Set Stove Temperature."""
#             # _LOGGER.info('Received data', call.data["value"])
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setTemperature(call.data["value"])
#             # await self.async_update()

#         async def stoveSetPowerLevel(call) -> None:
#             """Set Stove Power Level."""
#             # _LOGGER.info('Received data', call.data["value"])
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setPowerLevel(call.data["value"])

#         async def stoveSetEcoModeOn(call) -> None:
#             """Set Stove Eco Mode On."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setEcoModeOn()

#         async def stoveSetEcoModeOff(call) -> None:
#             """Set Stove Eco Mode Off."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setEcoModeOff()

#         async def stoveSetChronoModeOn(call) -> None:
#             """Set Stove Chrono Mode On."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setEcoModeOn()

#         async def stoveSetChronoModeOff(call) -> None:
#             """Set Stove Chrono Mode Off."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setEcoModeOff()

#         async def stoveSetOn(call) -> None:
#             """Set Stove On."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setOn()

#         async def stoveSetOff(call) -> None:
#             """Set Stove Off."""
#             #stove = Stove(entry.data[CONF_IP_ADDRESS], entry.data[CONF_PORT])
#             await self.api.setOff()

#         # Register our service with Home Assistant.
#         self.hass.services.async_register(DOMAIN, "set_temperature", stoveSetTemperature)
#         self.hass.services.async_register(DOMAIN, "set_power_level", stoveSetPowerLevel)
#         self.hass.services.async_register(DOMAIN, "eco_mode_turn_on", stoveSetEcoModeOn)
#         self.hass.services.async_register(DOMAIN, "eco_mode_turn_off", stoveSetEcoModeOff)
#         self.hass.services.async_register(DOMAIN, "chrono_mode_turn_on", stoveSetChronoModeOn)
#         self.hass.services.async_register(DOMAIN, "chrono_mode_turn_off", stoveSetChronoModeOff)
#         self.hass.services.async_register(DOMAIN, "turn_on", stoveSetOn)
#         self.hass.services.async_register(DOMAIN, "turn_off", stoveSetOff)

#         self.config_entry.async_on_unload(
#             self.config_entry.add_update_listener(options_updated_listener)
#         )

async def async_connect_or_timeout(hass, hottoh):
    """Connect to HottoH."""
    try:
        name = None
        with async_timeout.timeout(10):
            _LOGGER.debug("Initialize connection to Hottoh")
            if not hottoh.is_connected:
                await hass.async_add_executor_job(hottoh.connect)
            while not hottoh.is_connected or name is None:
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

# async def async_unload_entry(hass, config_entry):
#     """Unload a config entry."""
#     unload_ok = await hass.config_entries.async_unload_platforms(
#         config_entry, PLATFORMS
#     )
#     if unload_ok:
#         domain_data = hass.data[DOMAIN][config_entry.entry_id]
#         domain_data[CANCEL_STOP]()
#         await async_disconnect_or_timeout(hass, hottoh=domain_data[HOTTOH_SESSION])
#         hass.data[DOMAIN].pop(config_entry.entry_id)

#     return unload_ok

class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""
