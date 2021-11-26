"""Support for Hottoh Climate Entity."""
import logging

from homeassistant.components.binary_sensor import BinarySensorEntity

from .const import DOMAIN, HOTTOH_SESSION
from . import HottohEntity

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    entities = []
    if hottoh.isPumpEnabled():
        entities.append(HottohBinarySensor(hottoh, "water_pump", "mdi:pump"))

    async_add_entities(entities, True)

class HottohBinarySensor(HottohEntity, BinarySensorEntity):
    """Representation of a Hottoh Binary Sensor"""
    def __init__(self, hottoh, name, icon):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        BinarySensorEntity.__init__(self)
        self.api = hottoh
        self.nameSet = name
        self._attr_name = self.api.get_name() + ' ' + name
        self._attr_icon = icon
        self._attr_unique_id = self.api.get_name() + '_' + name

    @property
    def is_on(self):
        return getattr(self.api, 'get_' + self.nameSet)()
