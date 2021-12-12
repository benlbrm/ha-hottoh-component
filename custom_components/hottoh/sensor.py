"""Support for Hottoh Climate Entity."""
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.sensor import SensorDeviceClass

from homeassistant.const import TEMP_CELSIUS, PERCENTAGE

from .const import DOMAIN, HOTTOH_SESSION
from . import HottohEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    domain_data = hass.data[DOMAIN][config_entry.entry_id]
    hottoh = domain_data[HOTTOH_SESSION]

    entities = []
    entities.append(HottohActionSensor(hottoh))
    entities.append(
        HottohSensor(
            hottoh,
            "smoke_temperature",
            "mdi:smoke",
            SensorDeviceClass.TEMPERATURE,
            TEMP_CELSIUS,
        )
    )
    entities.append(HottohSensor(hottoh, "speed_fan_smoke", "mdi:fan", "", "g/m"))

    if hottoh.isTempRoom1Enabled():
        entities.append(
            HottohSensor(
                hottoh,
                "temperature_room_1",
                "mdi:thermometer",
                SensorDeviceClass.TEMPERATURE,
                TEMP_CELSIUS,
            )
        )
    if hottoh.isTempRoom2Enabled():
        entities.append(
            HottohSensor(
                hottoh,
                "temperature_room_2",
                "mdi:thermometer",
                SensorDeviceClass.TEMPERATURE,
                TEMP_CELSIUS,
            )
        )
    if hottoh.isTempRoom3Enabled():
        entities.append(
            HottohSensor(
                hottoh,
                "temperature_room_3",
                "mdi:thermometer",
                SensorDeviceClass.TEMPERATURE,
                TEMP_CELSIUS,
            )
        )
    if hottoh.isTempWaterEnabled():
        entities.append(
            HottohSensor(
                hottoh,
                "water_temperature",
                "mdi:water-boiler",
                SensorDeviceClass.TEMPERATURE,
                TEMP_CELSIUS,
            )
        )

    for fan in range(1, hottoh.getFanNumber() + 1):
        entities.append(
            HottohSensor(
                hottoh,
                "speed_fan_" + str(fan),
                "mdi:fan",
                SensorDeviceClass.POWER_FACTOR,
                PERCENTAGE,
            )
        )
        entities.append(
            HottohSensor(
                hottoh,
                "air_ex_" + str(fan),
                "mdi:air-filter",
                SensorDeviceClass.POWER_FACTOR,
                PERCENTAGE,
            )
        )

    entities.append(
        HottohSensor(
            hottoh, "power_level", "mdi:fan", SensorDeviceClass.POWER_FACTOR, PERCENTAGE
        )
    )

    async_add_entities(entities, True)


class HottohSensor(HottohEntity, SensorEntity):
    """Representation of a Hottoh Sensor"""

    def __init__(self, hottoh, name, icon, device_class, unit_of_measurement):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        SensorEntity.__init__(self)
        self.api = hottoh
        self.nameSet = name
        self._attr_name = self.api.get_name() + " " + name
        self._attr_icon = icon
        self._attr_device_class = device_class
        self._attr_unit_of_measurement = unit_of_measurement
        self._attr_unique_id = self.api.get_name() + "_" + name

    @property
    def state(self):
        return getattr(self.api, "get_" + self.nameSet)()

    @property
    def state_class(self):
        return "measurement"

    @property
    def min_temp(self):
        """Return min value"""
        try:
            func = getattr(self.api, "get_set_min_" + self.nameSet)()
        except AttributeError:
            func = None
        return func

    @property
    def max_temp(self):
        """Return max value"""
        try:
            func = getattr(self.api, "get_set_max_" + self.nameSet)()
        except AttributeError:
            func = None
        return func

    @property
    def set_temp(self):
        """Return set value"""
        try:
            func = getattr(self.api, "get_set_" + self.nameSet)()
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


class HottohActionSensor(HottohEntity, SensorEntity):
    """Representation of a Hottoh Status"""

    def __init__(self, hottoh):
        """Initialize the Sensor."""
        HottohEntity.__init__(self, hottoh)
        SensorEntity.__init__(self)
        self.api = hottoh

    @property
    def name(self):
        return self.api.get_name() + " " + "action"

    @property
    def unique_id(self):
        return self.api.get_name() + "_" + "action"

    @property
    def state(self):
        return self.api.get_action()
