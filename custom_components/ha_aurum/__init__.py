""" The Aurum Component."""
import asyncio
import logging
from datetime import timedelta
from typing import Dict

import async_timeout
import voluptuous as vol
from py_aurum import Aurum

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_SCAN_INTERVAL
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    API,
    ATTR_MAC,
    CONF_SELECTION,
    COORDINATOR,
    DOMAIN,
    SENSOR_LIST,
)

CONFIG_SCHEMA = vol.Schema({DOMAIN: vol.Schema({})}, extra=vol.ALLOW_EXTRA)

_LOGGER = logging.getLogger(__name__)

DEFAULT_SCAN_INTERVAL = 10

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Aurum platform."""
    return True


async def async_setup_entry(hass, entry):
    """Set up the Aurum Meetstekker from a config entry."""
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Aurum(host=entry.data["host"], websession=websession)
    
    if entry.data[CONF_SELECTION] is not None:
        sensor_list = [int(s) for s in entry.data[CONF_SELECTION].split(',')]
    else:
        sensor_list = None
    _LOGGER.debug("sensor list: %s", sensor_list)

    try:
        connected = await api.connect()

        if not connected:
            raise ConfigEntryNotReady

    except Aurum.AurumError:
        _LOGGER.error("Error while communicating to device")
        raise ConfigEntryNotReady

    except asyncio.TimeoutError:
        _LOGGER.error("Timeout while connecting to Smile")
        raise ConfigEntryNotReady

    async def async_update_data():
        """Update data via API endpoint."""
        _LOGGER.debug("Updating Aurum...")
        try:
            async with async_timeout.timeout(10):
                await api.update_data()
                _LOGGER.debug("Succesfully updated Aurum...")
                return True
        except Aurum.XMLDataMissingError:
            _LOGGER.debug("Updating Aurum failed...")
            raise UpdateFailed("Aurum update failed")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="Aurum",
        update_method=async_update_data,
        update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL)
    )

    await coordinator.async_refresh()

    if not coordinator.last_update_success:
        raise ConfigEntryNotReady

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        API: api,
        COORDINATOR: coordinator,
        SENSOR_LIST : sensor_list
    }

    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, ATTR_MAC)},
        manufacturer="Aurum Europe",
        name=entry.title,
        model="Meetstekker"
    )

    entry.add_update_listener(_update_listener)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def _update_listener(hass: HomeAssistant, entry: ConfigEntry):
    """Handle options update."""
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    coordinator.update_interval = timedelta(
        seconds=entry.options.get(CONF_SCAN_INTERVAL)
    )

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[
                hass.config_entries.async_forward_entry_unload(entry, component)
                for component in PLATFORMS
            ]
        )
    )
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class AurumBase(CoordinatorEntity):
    """Represent Aurum Base."""

    def __init__(self, api, coordinator, name):
        """Initialise the gateway."""
        super().__init__(coordinator)

        self._api = api
        self._name = name

        self._unique_id = None

        self._entity_name = self._name

    @property
    def unique_id(self):
        """Return a unique ID."""
        return self._unique_id

    @property
    def name(self):
        """Return the name of the entity, if any."""
        return self._name

    @property
    def device_info(self) -> Dict[str, any]:
        """Return the device information."""
        device_information = {
            "identifiers": {(DOMAIN, ATTR_MAC)},
            "name": self._entity_name,
            "manufacturer": "Aurum Europe",
            "model": "Meetstekker"
        }

        return device_information

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self._async_process_data()
        self.async_on_remove(
            self.coordinator.async_add_listener(self._async_process_data)
        )

    @callback
    def _async_process_data(self):
        """Interpret and process API data."""
        raise NotImplementedError

