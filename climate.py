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
    SUPPORT_PRESET_MODE,
    PRESET_AWAY,
    PRESET_NONE,
    PRESET_ECO,
    PRESET_BOOST,
    PRESET_COMFORT,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)


from .const import DOMAIN, HOTTOH_SESSION, CONF_AWAY_TEMP, CONF_COMFORT_TEMP, CONF_ECO_TEMP

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities, discovery_info=None):
    """Add sensors for passed config_entry in HA."""
    away_temp = config_entry.data[CONF_AWAY_TEMP]
    eco_temp = config_entry.data[CONF_ECO_TEMP]
    comfort_temp = config_entry.data[CONF_COMFORT_TEMP]
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    climate = HottohDevice(hottoh, away_temp, eco_temp, comfort_temp)

    async_add_entities([climate], True)

class HottohDevice(ClimateEntity):
    """Reprensentation of the Stove Device """
    _attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
    _attr_max_temp = 30
    _attr_min_temp = 15
    _attr_supported_features = SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE
    _attr_target_temperature_step = PRECISION_HALVES
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_preset_mode = PRESET_NONE
    SCAN_INTERVAL = timedelta(seconds=10)

    """Representation of a Stove Climate"""
    def __init__(self, hottoh, away_temp, eco_temp, comfort_temp):
        """Initialize the Climate."""
        ClimateEntity.__init__(self)
        self.api = hottoh
        self._away_temp = away_temp
        self._eco_temp = eco_temp
        self._comfort_temp = comfort_temp

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
        return self.api.get_temperature_room_1()

    @property
    def target_temperature(self):
        return self.api.get_set_temperature_room_1()

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
    
    @property
    def preset_mode(self):
        """Return the current preset mode, e.g., home, away, temp."""
        return self._attr_preset_mode
    
    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        preset_modes = [PRESET_NONE]
        for mode, preset_mode_temp in [
            (PRESET_AWAY, self._away_temp),
            (PRESET_ECO, self._eco_temp),
            (PRESET_COMFORT, self._comfort_temp)
            ]:
            if preset_mode_temp is not None:
                preset_modes.append(mode)
        return preset_modes
    
    @property
    def presets(self):
        """Return a dict of available preset and temperatures."""
        presets = {}
        for mode, preset_mode_temp in [
            (PRESET_AWAY, self._away_temp),
            (PRESET_ECO, self._eco_temp),
            (PRESET_COMFORT, self._comfort_temp)
            ]:
            if preset_mode_temp is not None:
                presets.update({mode: preset_mode_temp})
        return presets

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
        if preset_mode not in self.preset_modes:
            return None
        if preset_mode == PRESET_ECO:
            await self.hass.async_add_executor_job(self.api.setTemperature, self._eco_temp)
            await self.hass.async_add_executor_job(self.api.setEcoModeOn)
        if preset_mode == PRESET_COMFORT:
            await self.hass.async_add_executor_job(self.api.setTemperature, self._comfort_temp)
            await self.hass.async_add_executor_job(self.api.setEcoModeOff)
        if preset_mode == PRESET_AWAY:
            await self.hass.async_add_executor_job(self.api.setTemperature, self._away_temp)
            await self.hass.async_add_executor_job(self.api.setEcoModeOn)

        self._attr_preset_mode = preset_mode
        await self.async_update_ha_state()
            
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
