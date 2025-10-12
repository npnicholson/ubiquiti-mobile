"""Device tracker platform for ubiquiti_mobile clients."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.components.device_tracker.const import SourceType
from homeassistant.const import STATE_HOME, STATE_NOT_HOME
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo

from custom_components.ubiquiti_mobile.const import DOMAIN
from custom_components.ubiquiti_mobile.data import UbiquitiMobileStateData
from custom_components.ubiquiti_mobile.entity import UbiquitiMobileEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.ubiquiti_mobile.model.uimqtt import HighClientInfo

    from .coordinator import UbiquitiDataUpdateCoordinator
    from .data import UbiquitiMobileConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UbiquitiMobileConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up client trackers."""
    coordinator: UbiquitiDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    # Cache MACs so each tracker entity is only created once.
    tracked_clients: set[str] = set()

    def _handle_coordinator_update() -> None:
        data = coordinator.data
        if not data:
            return

        state_data = UbiquitiMobileStateData(**data)
        if not state_data.high:
            return

        new_entities: list[UbiquitiMobileClientTracker] = []
        for client in state_data.high.client_details:
            mac = client.mac.lower()
            if mac in tracked_clients:
                continue

            new_entities.append(
                UbiquitiMobileClientTracker(
                    coordinator=coordinator,
                    client=client,
                )
            )
            tracked_clients.add(mac)

        if new_entities:
            # Ensure the first state reflects the current coordinator snapshot.
            async_add_entities(new_entities, update_before_add=True)

    _handle_coordinator_update()
    entry.async_on_unload(coordinator.async_add_listener(_handle_coordinator_update))


class UbiquitiMobileClientTracker(UbiquitiMobileEntity, TrackerEntity):
    """Device tracker representing a connected client."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
        client: HighClientInfo,
    ) -> None:
        """Initialize the client tracker."""
        self._mac: str = client.mac.lower()
        self._sanitized_mac = self._mac.replace(":", "")
        self._upper_mac = self._mac.upper()
        self._default_name = f"Client {self._upper_mac}"

        device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{coordinator.config_entry.entry_id}_client_{self._sanitized_mac}",
                )
            },
            connections={(CONNECTION_NETWORK_MAC, self._upper_mac)},
            name=client.host_name or self._default_name,
            manufacturer="Ubiquiti",
            via_device=(DOMAIN, coordinator.config_entry.entry_id),
        )
        super().__init__(
            coordinator,
            f"client_{self._sanitized_mac}",
            device_info=device_info,
        )

        self._attr_source_type = SourceType.ROUTER
        self._attr_name = client.host_name or self._default_name
        self._attr_should_poll = False

    @property
    def state(self) -> str:
        """Return Home Assistant state for the client."""
        return STATE_HOME if self.is_connected else STATE_NOT_HOME

    @property
    def mac_address(self) -> str:
        """Return the MAC address of the client."""
        return self._upper_mac

    @property
    def ip_address(self) -> str | None:
        """Return the IP address for the client."""
        client = self._client
        return client.ip if client else None

    @property
    def hostname(self) -> str | None:
        """Return the hostname provided by the gateway."""
        client = self._client
        return client.host_name if client else None

    @property
    def is_connected(self) -> bool:
        """Return the connection state."""
        return self._client is not None

    @property
    def name(self) -> str:
        """Return the display name."""
        client = self._client
        if client and client.host_name:
            if client.host_name != self._attr_name:
                self._attr_name = client.host_name
            return client.host_name
        if self._attr_name != self._default_name:
            self._attr_name = self._default_name
        return self._default_name

    @property
    def extra_state_attributes(self) -> dict[str, str | int | None]:
        """Return extra attributes describing the client."""
        client = self._client
        if not client:
            return {}

        return {
            "ip_address": client.ip,
            "mac_address": client.mac.upper(),
            "hostname": client.host_name,
            "connection": client.connection,
            "link_speed": client.link_speed,
            "rx_bytes": client.rxBytes,
            "tx_bytes": client.txBytes,
            "rx_rate": client.rx_rate,
            "tx_rate": client.tx_rate,
            "rx_packets": client.rxPackets,
            "tx_packets": client.txPackets,
            "band": client.band,
            "channel": client.channel,
            "signal": client.signal,
            "score": client.score,
            "uptime": client.uptime,
            "associated_at": client.associated_at,
            "ssid": client.ssid,
            "mode": client.mode,
            "rx_bitrate": client.rxBitRate,
            "tx_bitrate": client.txBitRate,
        }

    @property
    def _client(self) -> HighClientInfo | None:
        """Return the current client information from the coordinator."""
        data = self.coordinator.data
        if not data:
            return None

        state_data = UbiquitiMobileStateData(**data)
        if not state_data.high:
            return None

        for client in state_data.high.client_details:
            if client.mac.lower() == self._mac:
                return client

        # Client disappeared from the latest payload.
        return None
