"""Config flow for the Aurum Meetstekker integration."""
import logging
from typing import Any, Dict

import voluptuous as vol

from homeassistant import config_entries, core, exceptions
from homeassistant.const import CONF_BASE, CONF_HOST, CONF_SCAN_INTERVAL
from homeassistant.core import callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from py_aurum import Aurum

from .const import DOMAIN, CONF_SELECTION  # pylint:disable=unused-import
from . import DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str, 
        vol.Required(CONF_SELECTION): str,
        vol.Optional(
            CONF_SCAN_INTERVAL, default=DEFAULT_SCAN_INTERVAL
        ): cv.positive_int
    }, extra=vol.ALLOW_EXTRA
)


async def validate_input(hass: core.HomeAssistant, data):
    """
    Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    websession = async_get_clientsession(hass, verify_ssl=False)
    api = Aurum(host=data[CONF_HOST], timeout=30, websession=websession)
    sensor_list = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]

    try:
        await api.connect()
        if data[CONF_SELECTION] is not None:
            sensor_list = [int(s) for s in data["selection"].split(',')]
    except Aurum.AurumError:
        raise CannotConnect
    except ValueError:
        raise InvalidInput

    return api, sensor_list

@config_entries.HANDLERS.register(DOMAIN)
class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Aurum."""

    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:

            for entry in self._async_current_entries():
                if entry.data.get(CONF_HOST) == user_input[CONF_HOST]:
                    return self.async_abort(reason="already_configured")

            try:
                api, sensor_list = await validate_input(self.hass, user_input)

                return self.async_create_entry(title="Aurum", data=user_input)
            except CannotConnect:
                errors[CONF_BASE] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors[CONF_BASE] = "unknown"
            except InvalidInput:
                errors[CONF_BASE] = "invalid input data provided"

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class CannotConnect(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidInput(exceptions.HomeAssistantError):
    """Error to indicate invalid input data entered."""
