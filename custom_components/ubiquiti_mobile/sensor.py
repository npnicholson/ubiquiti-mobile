"""Sensor platform for ubiquiti_mobile."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.device_tracker.config_entry import (
    TrackerEntity,
    TrackerEntityDescription,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfInformation

from custom_components.ubiquiti_mobile.const import DOMAIN
from custom_components.ubiquiti_mobile.data import UbiquitiMobileStateData

from .entity import UbiquitiMobileEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import UbiquitiDataUpdateCoordinator
    from .data import UbiquitiMobileConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UbiquitiMobileConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coord = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            UMSensorWanIp(coordinator=coord),
            UMSensorLanIp(coordinator=coord),
            UMSensorTracker(coordinator=coord),
            UMSensorDataUsage(coordinator=coord),
            UMSensorClients(coordinator=coord),
        ]
    )


class UMSensorWanIp(UbiquitiMobileEntity, SensorEntity):
    """Sensor class."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, "wan_ip")
        self.entity_description = SensorEntityDescription(
            key=DOMAIN,
            name="Wan Ip Address",
            icon="mdi:ip-network",
            unit_of_measurement=None,
            device_class=None,
            state_class=None,
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.info.wan_ip if state_data.info else None


class UMSensorLanIp(UbiquitiMobileEntity, SensorEntity):
    """Sensor class."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, "lan_ip")
        self.entity_description = SensorEntityDescription(
            key=DOMAIN,
            name="Lan Ip Address",
            icon="mdi:ip-network",
            unit_of_measurement=None,
            device_class=None,
            state_class=None,
        )

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.info.lan_ip if state_data.info else None


class UMSensorDataUsage(UbiquitiMobileEntity, SensorEntity):
    """Data Usage."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, "data_usage")
        self.entity_description = SensorEntityDescription(
            key=DOMAIN,
            name="Data Usage",
            icon="mdi:ip-network",
            native_unit_of_measurement=UnitOfInformation.BYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            state_class=SensorStateClass.TOTAL_INCREASING,
        )

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.high.total_usage if state_data.high else None


class UMSensorClients(UbiquitiMobileEntity, SensorEntity):
    """Uptime."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, "clients")
        self.entity_description = SensorEntityDescription(
            key=DOMAIN,
            name="Clients",
            icon="mdi:counter",
            state_class=SensorStateClass.MEASUREMENT,
        )

    @property
    def native_value(self) -> int | None:
        """Return the native value of the sensor."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.high.client_numbers if state_data.high else None


class UMSensorTracker(UbiquitiMobileEntity, TrackerEntity):
    """GPS Tracker."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
    ) -> None:
        """Initialize the tracker class."""
        super().__init__(coordinator, "location")
        self.entity_description = TrackerEntityDescription(
            key=DOMAIN,
            name="Location",
            icon="mdi:map-marker-radius",
            entity_category=EntityCategory.CONFIG,
        )

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the device."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.gps.latitude if state_data.gps else None

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the device."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return state_data.gps.longitude if state_data.gps else None

    @property
    def source_type(self) -> str:
        """Return the source type "GPS"."""
        return "gps"
