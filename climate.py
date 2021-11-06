"""Support for Hottoh Climate Entity."""
from datetime import timedelta
import json
import logging
import asyncio
import async_timeout

from homeassistant.helpers.entity import Entity

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    CURRENT_HVAC_OFF,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    SUPPORT_TARGET_TEMPERATURE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)

from .const import DOMAIN, HOTTOH_SESSION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    climate = HottohDevice(hottoh)

    async_add_entities([climate], True)

class HottohDevice(ClimateEntity):
    """Reprensentation of the Stove Device """
    _attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
    _attr_max_temp = 30
    _attr_min_temp = 15
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE
    _attr_target_temperature_step = PRECISION_HALVES
    _attr_temperature_unit = TEMP_CELSIUS
    SCAN_INTERVAL = timedelta(seconds=10)

    """Representation of a Stove Climate"""
    def __init__(self, hottoh):
        """Initialize the Climate."""
        ClimateEntity.__init__(self)
        self.api = hottoh

    @property
    def should_poll(self) -> bool:        
        return True

    @property
    def unique_id(self):
        """Return Unique ID string."""
        return DOMAIN + self.name

    @property
    def name(self) -> str:
        """Return the name of the device, if any."""
        return self.api.get_name()

    @property
    def current_temperature(self):
        return self.api.get_temperature()

    @property
    def target_temperature(self):
        return self.api.get_set_temperature()

    @property
    def hvac_mode(self):
        if self.api.get_mode() == "on":
            return HVAC_MODE_HEAT
        return HVAC_MODE_OFF

    @property
    def hvac_action(self):
        return self.api.get_action()

    @property
    def icon(self) -> str:
        """Return nice icon for heater."""
        if self.hvac_mode == HVAC_MODE_HEAT:
            return "mdi:fireplace"
        return "mdi:fireplace-off"

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self.hass.async_add_executor_job(
            self.api.setTemperature, temperature
        )
    
    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""

    
    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.hass.async_add_executor_job(
                self.api.setOn
            )

        if hvac_mode == HVAC_MODE_OFF:
            await self.hass.async_add_executor_job(
                self.api.setOff
            )

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {(DOMAIN, self.name)},
            "name": self.name,
            "sw_version": self.api.get_firmware(),
            "model": self.api.get_manufacturer(),
            "manufacturer": self.api.get_manufacturer(),
        }
