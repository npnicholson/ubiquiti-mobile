"""Sensor platform for ubiquiti_mobile."""

from __future__ import annotations

from dataclasses import dataclass
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
from homeassistant.const import (
    PERCENTAGE,
    SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
    EntityCategory,
    UnitOfDataRate,
    UnitOfInformation,
    UnitOfTime,
)
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo

from custom_components.ubiquiti_mobile.const import DOMAIN
from custom_components.ubiquiti_mobile.data import UbiquitiMobileStateData

from .entity import UbiquitiMobileEntity

if TYPE_CHECKING:
    from collections.abc import Callable

    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback
    from homeassistant.helpers.typing import StateType

    from custom_components.ubiquiti_mobile.model.uimqtt import HighClientInfo

    from .coordinator import UbiquitiDataUpdateCoordinator
    from .data import UbiquitiMobileConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: UbiquitiMobileConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coord = hass.data[DOMAIN][entry.entry_id]
    sensors = [
        UbiquitiMobileSensor(coordinator=coord, config=config)
        for config in SENSOR_CONFIGS
    ]
    trackers = [
        UbiquitiMobileTracker(coordinator=coord, config=config)
        for config in TRACKER_CONFIGS
    ]
    async_add_entities([*sensors, *trackers])

    # Remember which MAC/metric combinations already exist so we do not add duplicates.
    tracked_client_metrics: set[str] = set()

    def _register_client_sensors() -> None:
        """Create client-level sensors when new clients appear."""
        data = coord.data
        if not data:
            return

        state_data = UbiquitiMobileStateData(**data)
        if not state_data.high:
            return

        new_entities: list[UbiquitiMobileClientSensor] = []
        for client in state_data.high.client_details:
            mac = client.mac.lower()
            if not mac:
                continue
            sanitized_mac = mac.replace(":", "")

            for config in CLIENT_SENSOR_CONFIGS:
                unique_key = f"{sanitized_mac}_{config.key}"
                if unique_key in tracked_client_metrics:
                    continue

                new_entities.append(
                    UbiquitiMobileClientSensor(
                        coordinator=coord,
                        client=client,
                        config=config,
                    )
                )
                tracked_client_metrics.add(unique_key)

        if new_entities:
            # Create discovered entities with fresh coordinator state to avoid empty
            # values.
            async_add_entities(new_entities, update_before_add=True)

    _register_client_sensors()
    entry.async_on_unload(coord.async_add_listener(_register_client_sensors))


@dataclass(frozen=True, slots=True)
class UbiquitiMobileSensorConfig:
    """Configuration for a Ubiquiti Mobile sensor entity."""

    tag: str
    entity_description: SensorEntityDescription
    value_fn: Callable[[UbiquitiMobileStateData], StateType]


@dataclass(frozen=True, slots=True)
class UbiquitiMobileTrackerConfig:
    """Configuration for a Ubiquiti Mobile tracker entity."""

    tag: str
    entity_description: TrackerEntityDescription
    latitude_fn: Callable[[UbiquitiMobileStateData], float | None]
    longitude_fn: Callable[[UbiquitiMobileStateData], float | None]
    source_type: str = "gps"


def _client_rate_bytes_per_second(
    client: HighClientInfo,
    byte_attr: str,
    bit_attr: str,
) -> int | None:
    """Return client rate in bytes per second, handling bit/byte fields."""
    value = getattr(client, byte_attr, None)
    if value is not None:
        return value

    bit_value = getattr(client, bit_attr, None)
    if bit_value is None:
        return None

    # Wireless metrics report bits per second; convert to bytes per second.
    return int(bit_value / 8)


def _client_rx_rate_value(client: HighClientInfo) -> int | None:
    """Return receive rate in bytes per second."""
    return _client_rate_bytes_per_second(client, "rx_rate", "rxBitRate")


def _client_tx_rate_value(client: HighClientInfo) -> int | None:
    """Return transmit rate in bytes per second."""
    return _client_rate_bytes_per_second(client, "tx_rate", "txBitRate")


def _client_connection_value(client: HighClientInfo) -> str:
    """Return normalized connection string."""
    connection = (client.connection or "").lower()
    if connection in {"ethernet", "wireless"}:
        return connection
    return "unknown"


@dataclass(frozen=True, slots=True)
class UbiquitiMobileClientSensorConfig:
    """Configuration for a client-specific sensor entity."""

    key: str
    name: str
    icon: str | None
    unit_of_measurement: str | None
    device_class: SensorDeviceClass | None
    state_class: SensorStateClass | None
    value_fn: Callable[[HighClientInfo], StateType]
    options: tuple[str, ...] | None = None


SENSOR_CONFIGS: tuple[UbiquitiMobileSensorConfig, ...] = (
    UbiquitiMobileSensorConfig(
        tag="wan_ip",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Wan Ip Address",
            icon="mdi:ip-network",
        ),
        value_fn=lambda data: data.info.wan_ip if data.info else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="lan_ip",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Lan Ip Address",
            icon="mdi:ip-network",
        ),
        value_fn=lambda data: data.info.lan_ip if data.info else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="data_usage",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Data Usage",
            icon="mdi:ip-network",
            native_unit_of_measurement=UnitOfInformation.BYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        value_fn=lambda data: data.high.total_usage if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="clients",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Clients",
            icon="mdi:counter",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.client_numbers if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="uptime",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Uptime",
            icon="mdi:timer-outline",
            native_unit_of_measurement=UnitOfTime.SECONDS,
            device_class=SensorDeviceClass.DURATION,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.uptime if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="upload_usage",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Upload Usage",
            icon="mdi:upload",
            native_unit_of_measurement=UnitOfInformation.BYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        value_fn=lambda data: data.high.upload_usage if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="download_usage",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Download Usage",
            icon="mdi:download",
            native_unit_of_measurement=UnitOfInformation.BYTES,
            device_class=SensorDeviceClass.DATA_SIZE,
            state_class=SensorStateClass.TOTAL_INCREASING,
        ),
        value_fn=lambda data: data.high.download_usage if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="experience",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Experience",
            icon="mdi:star-circle",
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.experience if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="cpu",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="CPU Usage",
            icon="mdi:cpu-64-bit",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.cpu if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="memory",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="Memory Usage",
            icon="mdi:memory",
            native_unit_of_measurement=PERCENTAGE,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.memory if data.high else None,
    ),
    UbiquitiMobileSensorConfig(
        tag="rssi",
        entity_description=SensorEntityDescription(
            key=DOMAIN,
            name="RSSI",
            icon="mdi:signal-cellular-3",
            native_unit_of_measurement=SIGNAL_STRENGTH_DECIBELS_MILLIWATT,
            device_class=SensorDeviceClass.SIGNAL_STRENGTH,
            state_class=SensorStateClass.MEASUREMENT,
        ),
        value_fn=lambda data: data.high.rssi if data.high else None,
    ),
)

TRACKER_CONFIGS: tuple[UbiquitiMobileTrackerConfig, ...] = (
    UbiquitiMobileTrackerConfig(
        tag="location",
        entity_description=TrackerEntityDescription(
            key=DOMAIN,
            name="Location",
            icon="mdi:map-marker-radius",
            entity_category=EntityCategory.CONFIG,
        ),
        latitude_fn=lambda data: data.gps.latitude if data.gps else None,
        longitude_fn=lambda data: data.gps.longitude if data.gps else None,
    ),
)

CLIENT_SENSOR_CONFIGS: tuple[UbiquitiMobileClientSensorConfig, ...] = (
    UbiquitiMobileClientSensorConfig(
        key="connection",
        name="Connection Type",
        icon="mdi:lan-connect",
        unit_of_measurement=None,
        device_class=SensorDeviceClass.ENUM,
        state_class=None,
        value_fn=_client_connection_value,
        options=("ethernet", "wireless", "unknown"),
    ),
    UbiquitiMobileClientSensorConfig(
        key="ip_address",
        name="IP Address",
        icon="mdi:ip-network",
        unit_of_measurement=None,
        device_class=None,
        state_class=None,
        value_fn=lambda client: client.ip,
    ),
    UbiquitiMobileClientSensorConfig(
        key="rx_rate",
        name="Receive Rate",
        icon="mdi:download-network",
        unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_client_rx_rate_value,
    ),
    UbiquitiMobileClientSensorConfig(
        key="tx_rate",
        name="Transmit Rate",
        icon="mdi:upload-network",
        unit_of_measurement=UnitOfDataRate.BYTES_PER_SECOND,
        device_class=SensorDeviceClass.DATA_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_fn=_client_tx_rate_value,
    ),
)


class UbiquitiMobileSensor(UbiquitiMobileEntity, SensorEntity):
    """Generic Ubiquiti Mobile sensor entity."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
        config: UbiquitiMobileSensorConfig,
    ) -> None:
        """Initialize the generic sensor entity."""
        super().__init__(coordinator, config.tag)
        self.entity_description = config.entity_description
        self._value_fn = config.value_fn

    @property
    def native_value(self) -> StateType:
        """Return the native value of the sensor."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return self._value_fn(state_data)


class UbiquitiMobileTracker(UbiquitiMobileEntity, TrackerEntity):
    """Generic Ubiquiti Mobile tracker entity."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
        config: UbiquitiMobileTrackerConfig,
    ) -> None:
        """Initialize the tracker entity."""
        super().__init__(coordinator, config.tag)
        self.entity_description = config.entity_description
        self._latitude_fn = config.latitude_fn
        self._longitude_fn = config.longitude_fn
        self._source_type = config.source_type

    @property
    def latitude(self) -> float | None:
        """Return the latitude of the device."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return self._latitude_fn(state_data)

    @property
    def longitude(self) -> float | None:
        """Return the longitude of the device."""
        state_data = UbiquitiMobileStateData(**self.coordinator.data)
        return self._longitude_fn(state_data)

    @property
    def source_type(self) -> str:
        """Return the tracker source type."""
        return self._source_type


class UbiquitiMobileClientSensor(UbiquitiMobileEntity, SensorEntity):
    """Sensor that represents a per-client metric."""

    def __init__(
        self,
        coordinator: UbiquitiDataUpdateCoordinator,
        client: HighClientInfo,
        config: UbiquitiMobileClientSensorConfig,
    ) -> None:
        """Initialize the client sensor."""
        self._config = config
        self._mac = client.mac.lower()
        self._upper_mac = self._mac.upper()
        self._sanitized_mac = self._mac.replace(":", "")
        self._default_device_name = f"Client {self._upper_mac}"

        device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    f"{coordinator.config_entry.entry_id}_client_{self._sanitized_mac}",
                )
            },
            connections={(CONNECTION_NETWORK_MAC, self._upper_mac)},
            name=client.host_name or self._default_device_name,
            manufacturer="Ubiquiti",
            via_device=(DOMAIN, coordinator.config_entry.entry_id),
        )
        super().__init__(
            coordinator,
            f"client_{self._sanitized_mac}_{config.key}",
            device_info=device_info,
        )

        options = list(config.options) if config.options is not None else None
        self.entity_description = SensorEntityDescription(
            key=config.key,
            name=config.name,
            icon=config.icon,
            native_unit_of_measurement=config.unit_of_measurement,
            device_class=config.device_class,
            state_class=config.state_class,
            options=options,
        )
        self._attr_should_poll = False
        self._attr_name = f"{self._default_device_name} {config.name}"

    @property
    def name(self) -> str:
        """Return a friendly name for the sensor."""
        client = self._client
        base_name = (
            client.host_name
            if client and client.host_name
            else self._default_device_name
        )
        combined_name = f"{base_name} {self._config.name}"
        if self._attr_name != combined_name:
            self._attr_name = combined_name
        return combined_name

    @property
    def native_value(self) -> StateType:
        """Return the current value for the metric."""
        client = self._client
        if not client:
            return None
        return self._config.value_fn(client)

    @property
    def _client(self) -> HighClientInfo | None:
        """Return the current client data from the coordinator."""
        data = self.coordinator.data
        if not data:
            return None

        state_data = UbiquitiMobileStateData(**data)
        if not state_data.high:
            return None

        for client in state_data.high.client_details:
            if client.mac.lower() == self._mac:
                return client

        return None
