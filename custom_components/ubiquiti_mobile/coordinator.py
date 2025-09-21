"""DataUpdateCoordinator for ubiquiti_mobile."""

from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from custom_components.ubiquiti_mobile.const import DOMAIN, LOGGER
from custom_components.ubiquiti_mobile.data import (
    UbiquitiMobileStateData,
)

from .api import (
    UbiquitiMobileApiClient,
    UbiquitiMobileApiClientAuthenticationError,
    UbiquitiMobileApiClientError,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import UbiquitiMobileConfigEntry


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class UbiquitiDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: UbiquitiMobileConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        client: UbiquitiMobileApiClient,
        config_entry: UbiquitiMobileConfigEntry,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=5),
            config_entry=config_entry,
            always_update=True,
        )

        self.client = client

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            info = await self.client.get_device_info()
            gps = await self.client.get_gps_info()
            high = await self.client.get_high_info()

            state_data: UbiquitiMobileStateData = UbiquitiMobileStateData(
                info=info.result, gps=gps.result, high=high.result
            )

            return vars(state_data)
        except UbiquitiMobileApiClientAuthenticationError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except UbiquitiMobileApiClientError as exception:
            raise UpdateFailed(exception) from exception
