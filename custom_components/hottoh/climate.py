"""Support for Hottoh Climate Entity."""
import json
import logging

from homeassistant.helpers.restore_state import RestoreEntity
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    HVAC_MODE_HEAT,
    HVAC_MODE_OFF,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_PRESET_MODE,
    SUPPORT_FAN_MODE,
    PRESET_AWAY,
    PRESET_NONE,
    PRESET_ECO,
    PRESET_BOOST,
    PRESET_COMFORT,
    ATTR_PRESET_MODE,
)
from homeassistant.const import (
    ATTR_TEMPERATURE,
    PRECISION_HALVES,
    TEMP_CELSIUS,
)


from .const import (
    DOMAIN,
    HOTTOH_SESSION,
    CONF_AWAY_TEMP,
    CONF_COMFORT_TEMP,
    CONF_ECO_TEMP,
)
from . import HottohEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass, config_entry, async_add_entities, discovery_info=None
):
    """Add sensors for passed config_entry in HA."""
    away_temp = config_entry.data[CONF_AWAY_TEMP]
    eco_temp = config_entry.data[CONF_ECO_TEMP]
    comfort_temp = config_entry.data[CONF_COMFORT_TEMP]
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    climate = HottohDevice(hottoh, away_temp, eco_temp, comfort_temp)

    async_add_entities([climate], True)


class HottohDevice(HottohEntity, ClimateEntity, RestoreEntity):
    """Reprensentation of the Stove Device """

    _attr_hvac_modes = [HVAC_MODE_HEAT, HVAC_MODE_OFF]
    _attr_max_temp = 30
    _attr_min_temp = 15
    _attr_supported_features = (
        SUPPORT_TARGET_TEMPERATURE | SUPPORT_PRESET_MODE | SUPPORT_FAN_MODE
    )
    _attr_target_temperature_step = PRECISION_HALVES
    _attr_temperature_unit = TEMP_CELSIUS
    _attr_preset_mode = PRESET_NONE

    """Representation of a Stove Climate"""

    def __init__(self, hottoh, away_temp, eco_temp, comfort_temp):
        """Initialize the Climate."""
        HottohEntity.__init__(self, hottoh)
        ClimateEntity.__init__(self)
        RestoreEntity.__init__(self)
        self.api = hottoh
        self._away_temp = away_temp
        self._eco_temp = eco_temp
        self._comfort_temp = comfort_temp

    async def async_added_to_hass(self):
        """Run when entity about to be added."""
        await super().async_added_to_hass()

        # Check If we have an old state
        old_state = await self.async_get_last_state()
        if old_state is not None:
            if old_state.attributes.get(ATTR_PRESET_MODE) is not None:
                self._attr_preset_mode = old_state.attributes.get(ATTR_PRESET_MODE)

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
            (PRESET_COMFORT, self._comfort_temp),
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
            (PRESET_COMFORT, self._comfort_temp),
        ]:
            if preset_mode_temp is not None:
                presets.update({mode: preset_mode_temp})
        return presets

    async def async_set_temperature(self, **kwargs):
        """Set new target temperature."""
        temperature = kwargs.get(ATTR_TEMPERATURE)
        if temperature is None:
            return
        await self.hass.async_add_executor_job(self.api.set_temperature, temperature)

    async def async_set_preset_mode(self, preset_mode):
        """Set new target preset mode."""
        if preset_mode not in self.preset_modes:
            return None
        if preset_mode == PRESET_ECO:
            await self.hass.async_add_executor_job(
                self.api.set_temperature, self._eco_temp
            )
            await self.hass.async_add_executor_job(self.api.set_eco_mode_on)
        if preset_mode == PRESET_COMFORT:
            await self.hass.async_add_executor_job(
                self.api.set_temperature, self._comfort_temp
            )
            await self.hass.async_add_executor_job(self.api.set_eco_mode_off)
        if preset_mode == PRESET_AWAY:
            await self.hass.async_add_executor_job(
                self.api.set_temperature, self._away_temp
            )
            await self.hass.async_add_executor_job(self.api.set_eco_mode_on)

        self._attr_preset_mode = preset_mode
        await self.async_update_ha_state()

    async def async_set_hvac_mode(self, hvac_mode):
        """Set new target hvac mode."""
        if hvac_mode == HVAC_MODE_HEAT:
            await self.hass.async_add_executor_job(self.api.set_on)

        if hvac_mode == HVAC_MODE_OFF:
            await self.hass.async_add_executor_job(self.api.set_off)

    @property
    def fan_mode(self):
        return str(self.api.get_set_speed_fan_1())

    @property
    def fan_modes(self):
        return ["0", "1", "2", "3", "4", "5", "6"]

    async def async_set_fan_mode(self, fan_mode):
        """Set new target fan mode."""
        await self.hass.async_add_executor_job(self.api.set_speed_fan_1, fan_mode)
