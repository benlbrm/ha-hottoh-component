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
    DEVICE_CLASS_POWER_FACTOR,
    TEMP_CELSIUS,
    PERCENTAGE
)

from .const import DOMAIN, HOTTOH_SESSION

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    entities = []
    entities.append(HottohActionSensor(hottoh))
    entities.append(HottohSensor(hottoh, 'smoke_temperature', 'mdi:smoke', DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS))
    entities.append(HottohSensor(hottoh, 'speed_fan_smoke', 'mdi:fan', '', 'rpm'))
    entities.append(HottohSensor(hottoh, 'air_ex_1', 'mdi:air-filter', DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS))

    if hottoh.isTempRoom1Enabled():
        entities.append(HottohSensor(hottoh, 'temperature_room_1', 'mdi:thermometer', DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS))
    if hottoh.isTempRoom2Enabled():
        entities.append(HottohSensor(hottoh, 'temperature_room_2', 'mdi:thermometer', DEVICE_CLASS_TEMPERATURE,TEMP_CELSIUS))
    if hottoh.isTempRoom3Enabled():
        entities.append(HottohSensor(hottoh, 'temperature_room_3', 'mdi:thermometer', DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS))
    if hottoh.isTempWaterEnabled():
        entities.append(HottohSensor(hottoh, 'water_temperature', 'mdi:water-boiler', DEVICE_CLASS_TEMPERATURE, TEMP_CELSIUS))

    for fan in range(1, hottoh.getFanNumber() + 1):
        entities.append(HottohSensor(hottoh, 'speed_fan_' + str(fan), 'mdi:fan', DEVICE_CLASS_POWER_FACTOR, PERCENTAGE))

    entities.append(HottohSensor(hottoh, 'power_level', 'mdi:fan', DEVICE_CLASS_POWER_FACTOR, PERCENTAGE))

    async_add_entities(entities, True)

class HottohSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Sensor"""
    def __init__(self, hottoh, name, icon, device_class, unit_of_measurement):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
        self.nameSet = name
        self._attr_name = self.api.get_name() + ' ' + name
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_unit_of_measurement = unit_of_measurement
        self._attr_unique_id = self.api.get_name() + '_' + name

    @property
    def state(self):
        return getattr(self.api, 'get_' + self.nameSet)()
    @property
    def state_class(self):
        return 'measurement'

    @property
    def min_temp(self):
        """Return min value"""
        try:
            func = getattr(self.api, 'get_set_min_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def max_temp(self):
        """Return max value"""
        try:
            func = getattr(self.api, 'get_set_max_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def set_temp(self):
        """Return set value"""
        try:
            func = getattr(self.api, 'get_set_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    
    @property
    def extra_state_attributes(self):
        attr = {}
        if self.set_temp is not None:
            attr["set_value"] = self.set_temp
        if self.min_temp is not None:
            attr["min_value"] = self.min_temp
        if self.max_temp is not None:
            attr["max_value"] = self.max_temp
        return attr


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

class HottohTemperatureSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Temprature Sensor"""
    def __init__(self, hottoh, name, icon):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
        self.nameSet = name
        self._attr_name = self.api.get_name() + ' ' + name
        self._attr_icon = icon
        self._attr_device_class = DEVICE_CLASS_TEMPERATURE
        self._attr_unit_of_measurement = TEMP_CELSIUS
        self._attr_unique_id = self.api.get_name() + '_' + name

    @property
    def state(self):
        return getattr(self.api, 'get_' + self.nameSet)()
    @property
    def state_class(self):
        return 'measurement'

    @property
    def min_temp(self):
        """Return min temperature"""
        try:
            func = getattr(self.api, 'get_set_min_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def max_temp(self):
        """Return max temperature"""
        try:
            func = getattr(self.api, 'get_set_max_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def set_temp(self):
        """Return set temperature"""
        try:
            func = getattr(self.api, 'get_set_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    
    @property
    def extra_state_attributes(self):
        attr = {}
        if self.set_temp is not None:
            attr["set_temp"] = self.set_temp
        if self.min_temp is not None:
            attr["min_temp"] = self.min_temp
        if self.max_temp is not None:
            attr["max_temp"] = self.max_temp
        return attr

class HottohPowerSensor(SensorEntity):
    SCAN_INTERVAL = timedelta(seconds=10)
    """Representation of a Hottoh Temprature Sensor"""
    def __init__(self, hottoh, name, icon):
        """Initialize the Sensor."""
        SensorEntity.__init__(self)
        self.api = hottoh
        self.nameSet = name
        self._attr_name = self.api.get_name() + ' ' + name
        self._attr_icon = icon
        self._attr_device_class = DEVICE_CLASS_POWER_FACTOR
        self._attr_unit_of_measurement = '%'
        self._attr_unique_id = self.api.get_name() + '_' + name

    @property
    def state(self):
        return getattr(self.api, 'get_' + self.nameSet)()
    @property
    def state_class(self):
        return 'measurement'

    @property
    def min_temp(self):
        """Return min speed"""
        try:
            func = getattr(self.api, 'get_set_min_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def max_temp(self):
        """Return max speed"""
        try:
            func = getattr(self.api, 'get_set_max_' + self.nameSet)()
        except AttributeError:
            func = None
        return func
    @property
    def set_temp(self):
        """Return set speed"""
        try:
            func = getattr(self.api, 'get_set_' + self.nameSet)()
        except AttributeError:
            func = None
        return func

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

