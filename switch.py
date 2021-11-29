"""Support for Hottoh Climate Entity."""
from datetime import timedelta
import logging

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN, HOTTOH_SESSION
from . import HottohEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    switch_on = HottohIsOnSwitch(hottoh)
    eco_mode = HottohEcoModeSwitch(hottoh)
    chrono_mode = HottohChronoModeSwitch(hottoh)

    async_add_entities([switch_on, eco_mode, chrono_mode], True)

class HottohIsOnSwitch(HottohEntity, SwitchEntity):
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        SwitchEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'is_on'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'is_on'
    @property
    def icon(self):
        if self.api.get_is_on():
            return "mdi:fireplace"
        return "mdi:fireplace-off"

    @property
    def is_on(self):
        return self.api.get_is_on()

    def turn_on(self):
        self.api.setOn()

    def turn_off(self):
        self.api.setOff()

class HottohEcoModeSwitch(HottohEntity, SwitchEntity):
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        SwitchEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'is_eco_mode'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'is_eco_mode'
    @property
    def icon(self):
        return "mdi:leaf"
    @property
    def is_on(self):
        return self.api.get_eco_mode()

    def turn_on(self):
        self.api.set_eco_mode_on()

    def turn_off(self):
        self.api.set_eco_mode_off()

class HottohChronoModeSwitch(HottohEntity, SwitchEntity):
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        SwitchEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'is_chrono_mode'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'is_chrono_mode'
    @property
    def icon(self):
        return "mdi:watch"
    @property
    def is_on(self):
        return self.api.get_chrono_mode()

    def turn_on(self):
        self.api.set_chrono_mode_on()

    def turn_off(self):
        self.api.set_chrono_mode_off()
