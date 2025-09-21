"""BlueprintEntity class."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from custom_components.ubiquiti_mobile.data import UbiquitiMobileStateData

from .coordinator import UbiquitiDataUpdateCoordinator


class UbiquitiMobileEntity(CoordinatorEntity[UbiquitiDataUpdateCoordinator]):
    """Entity class."""

    def __init__(self, coordinator: UbiquitiDataUpdateCoordinator, tag: str) -> None:
        """Initialize."""
        super().__init__(coordinator)

        state_data = UbiquitiMobileStateData(**coordinator.data)

        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{tag}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    coordinator.config_entry.domain,
                    coordinator.config_entry.entry_id,
                ),
            },
            name="Ubiquiti Mobile " + (state_data.info.mac if state_data.info else ""),
            manufacturer="Ubiquiti",
            model=state_data.info.model_name if state_data.info else None,
            serial_number=state_data.info.device_ac.upper()
            if state_data.info
            else None,
            sw_version=state_data.high.fw if state_data.high else None,
        )
