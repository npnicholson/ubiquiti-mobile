"""Custom types for ubiquiti_mobile."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from custom_components.ubiquiti_mobile.model.uimqtt import (
        GetDeviceInfoResponse,
        GetGPSInfoResponse,
        GetHighInfoResponse,
    )

    from .api import UbiquitiMobileApiClient
    from .coordinator import UbiquitiDataUpdateCoordinator


type UbiquitiMobileConfigEntry = ConfigEntry[UbiquitiMobileData]


@dataclass
class SessionData:
    """Represents an authenticated session with the gateway."""

    host: str | None = None
    username: str | None = None
    password: str | None = None
    token: str | None = None


@dataclass
class UbiquitiMobileData:
    """Data for the Blueprint integration."""

    client: UbiquitiMobileApiClient
    coordinator: UbiquitiDataUpdateCoordinator
    integration: Integration

    session_data: SessionData


@dataclass
class UbiquitiMobileStateData:
    """Data for the Blueprint integration."""

    info: GetDeviceInfoResponse | None = None
    gps: GetGPSInfoResponse | None = None
    high: GetHighInfoResponse | None = None
