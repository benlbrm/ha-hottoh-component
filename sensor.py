"""Support for Hottoh Climate Entity."""
from datetime import timedelta
import json
import logging
import asyncio
import async_timeout

from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import SensorEntity

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

    action = HottohActionSensor(hottoh)
    smoke = HottohSmokeTemperatureSensor(hottoh)
    fan = HottohFanSpeedSensor(hottoh)

    async_add_entities([action, smoke, fan], True)

class HottohActionSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'action'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'action'
    @property
    def state(self):
        return self.api.get_action()

class HottohSmokeTemperatureSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'smoke_temperature'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'smoke_temperature'
    @property
    def device_class(self):
        return DEVICE_CLASS_TEMPERATURE
    @property
    def state(self):
        return self.api.get_smoke_temperature()
    @property
    def state_class(self):
        return 'measurement'
    @property
    def icon(self):
        return "mdi:smoke"
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS

class HottohFanSpeedSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Status"""
    def __init__(self, hottoh):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
    @property
    def name(self):
        return self.api.get_name() + ' ' + 'fan_speed'
    @property
    def unique_id(self):
        return self.api.get_name() + '_' + 'fan_speed'
    @property
    def state(self):
        return self.api.get_fan_speed()
    @property
    def state_class(self):
        return 'measurement'
    @property
    def icon(self):
        return "mdi:fan"
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return 'rpm'

