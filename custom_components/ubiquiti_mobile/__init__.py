"""
Custom integration to integrate ubiquiti_mobile with Home Assistant.

For more details about this integration, please refer to
https://github.com/npnicholson/ubiquiti-mobile
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from custom_components.ubiquiti_mobile.coordinator import UbiquitiDataUpdateCoordinator
from custom_components.ubiquiti_mobile.data import SessionData

from .api import UbiquitiMobileApiClient
from .const import DOMAIN

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import UbiquitiMobileConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    # Platform.BINARY_SENSOR,
    # Platform.SWITCH,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant, entry: UbiquitiMobileConfigEntry
) -> bool:
    """Set up Ubiquiti Mobile Gateway from a config entry."""
    session = async_get_clientsession(hass)

    # Build a session data object from the session_data key in entry.data
    session_data: SessionData = SessionData(**entry.data["session_data"])

    # Make an API client using this session data
    client = UbiquitiMobileApiClient(
        session_data=session_data,
        session=session,
    )

    # Create and store a coordinator that has a reference to the API client as well
    # as the origional entry
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator = UbiquitiDataUpdateCoordinator(
        hass=hass,
        client=client,
        config_entry=entry,
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    # Set up each platform that is supported by this integration
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: UbiquitiMobileConfigEntry
) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def async_reload_entry(
    hass: HomeAssistant,
    entry: UbiquitiMobileConfigEntry,
) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(entry.entry_id)
