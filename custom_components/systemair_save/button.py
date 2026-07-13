"""
Button platform — maintenance actions.

The filter reset restarts the unit's filter timer after a physical filter
replacement: it zeroes the elapsed-days counter. The configured replacement
period is left untouched.

The save-settings button persists the volatile settings (fan speed level,
temperature setpoint level, configured fan flows) to the unit's EEPROM so
they survive a power cycle.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.const import EntityCategory

from .entity import SystemairSaveEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairSaveCoordinator
    from .data import SystemairSaveConfigEntry
    from .systemair_save_modbus import AirFilter


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairSaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the button platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        [
            SystemairSaveFilterResetButton(coordinator),
            SystemairSaveStoreSettingsButton(coordinator),
        ]
    )


class SystemairSaveFilterResetButton(SystemairSaveEntity, ButtonEntity):
    """Restart the filter timer after a filter replacement."""

    _attr_name = "Reset filter timer"

    def __init__(self, coordinator: SystemairSaveCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator, key="air_filter_reset", component="air_filter")

    @property
    def _air_filter(self) -> AirFilter:
        return self._subsystem  # type: ignore[return-value]

    async def async_press(self) -> None:
        """Reset the filter timer on the unit."""
        await self._air_filter.async_reset()
        await self.coordinator.async_request_refresh()


class SystemairSaveStoreSettingsButton(SystemairSaveEntity, ButtonEntity):
    """Persist the volatile settings to the unit's non-volatile memory."""

    _attr_name = "Save settings"
    # Every press is an EEPROM write; keep it out of the primary controls.
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: SystemairSaveCoordinator) -> None:
        """Initialize the button."""
        super().__init__(coordinator, key="store_settings", component="ventilation")

    async def async_press(self) -> None:
        """Store fan speed and temperature level in the unit's EEPROM."""
        await self.coordinator.device.async_store_settings()
