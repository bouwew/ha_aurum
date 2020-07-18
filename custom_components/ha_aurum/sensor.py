"""Aurum Meetstekker Sensor component for Home Assistant."""

import logging

from homeassistant.const import (
    DEVICE_CLASS_POWER,
    ENERGY_KILO_WATT_HOUR,
    ENERGY_WATT_HOUR,
    POWER_WATT,
    VOLUME_CUBIC_METERS,
)
from homeassistant.core import callback
from homeassistant.helpers.entity import Entity

from . import AurumBase

from .const import (
    ATTR_MAC,
    DOMAIN,
    SENSOR_MAP_DEVICE_CLASS,
    SENSOR_MAP_MODEL,
    SENSOR_MAP_UOM,
)

#ACTIVE_SENSORS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

_LOGGER = logging.getLogger(__name__)

SENSOR_PREFIX = 'Aurum'
SENSOR_TYPES = {
    'powerBattery': ['Inverter Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterOutBattery': ['Cumulative Inverter Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterInBattery': ['Cumulative Inverter Power In', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'powerMCHP': ['MCHP Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterOutMCHP': ['Cumulative MCHP Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterInMCHP': ['Cumulative MCHP Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'powerSolar': ['Solar Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterOutSolar': ['Cumulative Solar Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterInSolar': ['Cumulative Solar Power In', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'powerEV': ['EV Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterOutEV': ['Cumulative EV Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterInEV': ['Cumulative EV Power In', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'powerMain': ['Grid Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterOutMain': ['Cumulative Grid Power Out', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterInMain': ['Cumulative Grid Power In', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'smartMeterTimestamp': ['Smartmeter Timestamp', None, None],
    'powerElectricity': ['Grid Power', POWER_WATT, DEVICE_CLASS_POWER],
    'counterElectricityInLow': ['Cumulative Grid Power In Low', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterElectricityOutLow': ['Cumulative Grid Power Out Low', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterElectricityInHigh': ['Cumulative Grid Power In High', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'counterElectricityOutHigh': ['Cumulative Grid Power Out High', ENERGY_KILO_WATT_HOUR, DEVICE_CLASS_POWER],
    'rateGas': ['Gas Rate','m3/h', None],
    'counterGas': ['Cumulative Consumed Gas', VOLUME_CUBIC_METERS, None],
}

CUSTOM_ICONS = {
    "counterGas": "mdi:fire",
    "rateGas": "mdi:gas-cylinder",
    "smartMeterTimestamp": "mdi:calendar-clock",
}


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Set up the Aurum Meetstekker from a config entry."""
    _LOGGER.debug("Aurum hass data %s", hass.data[DOMAIN])
    api = hass.data[DOMAIN][config_entry.entry_id]["api"]
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]
    sensor_list = hass.data[DOMAIN][config_entry.entry_id]["sensor_list"]

    _LOGGER.debug("Aurum sensor")

    devices = []
    new_data = {}
    numbered_data = api.get_aurum_data()
    _LOGGER.debug("Aurum raw data, %s", numbered_data)

    _LOGGER.debug("ACTIVE SENSORS: %s", sensor_list)
    for count, data in numbered_data.items():
        if count in sensor_list:
            new_data.update(data)
            
    _LOGGER.debug("Aurum filtered data, %s", new_data)
    for sensor, sensor_type in SENSOR_TYPES.items():
        if sensor in new_data:
            devices.append(
                AurumPowerSensor(
                    api,
                    coordinator,
                    SENSOR_PREFIX,
                    sensor,
                    sensor_type,
                    sensor_list
                )
            )
            _LOGGER.info("Added sensor: %s", sensor)

    async_add_entities(devices, True)


class AurumSensor(AurumBase):
    """Represent Smile Sensors."""

    def __init__(self, api, coordinator, name, sensor, sensor_type):
        """Initialise the sensor."""
        super().__init__(api, coordinator, name)

        self._sensor = sensor

        self._dev_class = None
        self._state = None
        self._icon = None
        self._unit_of_measurement = None

        sensorname = sensor_type[SENSOR_MAP_MODEL]
        self._name = f"{self._entity_name} {sensorname}"

        self._unique_id = f"{ATTR_MAC}-{sensor}"

    @property
    def device_class(self):
        """Device class of this entity."""
        return self._dev_class

    @property
    def icon(self):
        """Return the icon to use in the frontend."""
        if CUSTOM_ICONS.get(self._sensor) is not None:
            self._icon = CUSTOM_ICONS.get(self._sensor)
        return self._icon

    @property
    def state(self):
        """Device class of this entity."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit_of_measurement


class AurumPowerSensor(AurumSensor, Entity):
    """Power sensor devices."""

    def __init__(self, api, coordinator, name, sensor, sensor_type, sensor_list):
        """Set up the Aurum API."""
        super().__init__(api, coordinator, name, sensor, sensor_type)

        self._model = sensor_type[SENSOR_MAP_MODEL]
        self._unit_of_measurement = sensor_type[SENSOR_MAP_UOM]
        self._dev_class = sensor_type[SENSOR_MAP_DEVICE_CLASS]
        self._sensor_list = sensor_list

    @callback
    def _async_process_data(self):
        """Update the entity."""
        _LOGGER.debug("Update sensor called")
        numbered_data = self._api.get_aurum_data()
        if not numbered_data:
            _LOGGER.error("Received no data...")
            self.async_write_ha_state()
            return

        new_data = {}
        for count, data in numbered_data.items():
            if count in self._sensor_list:
                new_data.update(data)
        if new_data.get(self._sensor) is not None:
            measurement = new_data[self._sensor]
            
            self._state = measurement

        self.async_write_ha_state()