"""Adds config flow for Blueprint."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.ubiquiti_mobile.data import SessionData

from .api import UbiquitiMobileApiClient
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigFlowResult


class UbiquitiMobileConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ubiquiti Mobile Gateway."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the configuration flow that is presented to the user."""
        errors = {}

        # If user input is defined, then the form has been submitted
        if user_input:
            host = user_input["host"].rstrip("/")
            username = user_input["username"]
            password = user_input["password"]

            session_data = SessionData(host=host, username=username, password=password)
            aiohttp_session = async_get_clientsession(self.hass)
            client = UbiquitiMobileApiClient(session_data, aiohttp_session)

            # attempt login and fetch status
            await client.async_start_session()
            status = await client.get_device_info()

            if status.result is not None:
                return self.async_create_entry(
                    title="Ubiquiti Mobile " + status.result.mac or host,
                    description=status.result.model_name,
                    # This is all of the data that is required to re-create this entry
                    # whenhome assistant restarts. vars() converts the dataobject to a
                    # dictionary, which is how the data will be presented to this
                    # configuration when home assistant restarts. Converting it keeps
                    # the locic in __init__ the same regardless.
                    data={"session_data": vars(session_data)},
                )

        data_schema = vol.Schema(
            {
                vol.Required(
                    "host",
                ): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
                ),
                vol.Required("username", default="ui"): selector.TextSelector(
                    selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT),
                ),
                vol.Required("password"): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.PASSWORD
                    ),
                ),
            }
        )
        return self.async_show_form(
            step_id="user", data_schema=data_schema, errors=errors
        )
