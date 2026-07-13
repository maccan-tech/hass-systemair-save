"""DataUpdateCoordinator that polls the SAVE ventilation unit."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError

from .const import DOMAIN, LOGGER, SCAN_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairSaveConfigEntry
    from .systemair_save_modbus import SystemairSave


class SystemairSaveCoordinator(DataUpdateCoordinator["SystemairSave"]):
    """
    Refreshes every sub-system on a schedule.

    ``async_update`` fans out to each component (each reads only its own
    registers), so adding/removing entities never changes what is polled.
    """

    config_entry: SystemairSaveConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: SystemairSaveConfigEntry,
        device: SystemairSave,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            LOGGER,
            name=DOMAIN,
            config_entry=entry,
            update_interval=SCAN_INTERVAL,
        )
        self.device = device

    async def _async_update_data(self) -> SystemairSave:
        """Update data via the vendored device library."""
        try:
            await self.device.async_update()
        except ModbusError as err:
            msg = f"Error communicating with SAVE: {err}"
            raise UpdateFailed(msg) from err
        return self.device
