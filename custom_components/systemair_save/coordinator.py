"""DataUpdateCoordinator that polls the SAVE ventilation unit."""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from modbus_connection import ModbusError

from .const import DOMAIN, LOGGER, SCAN_INTERVAL

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairSaveConfigEntry
    from .systemair_save_modbus import SystemairSave

# Serial gateways in front of the unit's RS-485 bus glitch occasionally
# (corrupted transaction IDs, dropped frames). A failed poll is retried once
# after this delay, and entities keep their last values until this many polls
# in a row have failed — a ventilation unit changes slowly, so values a
# couple of cycles old beat unavailable entities.
_UPDATE_RETRY_DELAY = 2.0
_MAX_FAILED_POLLS = 3


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
        self._failed_polls = 0

    async def _async_update_data(self) -> SystemairSave:
        """Update data via the vendored device library."""
        try:
            await self._update_with_retry()
        except ModbusError as err:
            self._failed_polls += 1
            # The first refresh must fail loudly so setup raises
            # ConfigEntryNotReady instead of loading with empty data.
            if self.data is None or self._failed_polls >= _MAX_FAILED_POLLS:
                msg = f"Error communicating with SAVE: {err}"
                raise UpdateFailed(msg) from err
            LOGGER.warning(
                "Poll failed (%s/%s in a row), keeping last values: %s",
                self._failed_polls,
                _MAX_FAILED_POLLS,
                err,
            )
        else:
            self._failed_polls = 0
        return self.device

    async def _update_with_retry(self) -> None:
        """Read the unit, retrying once to absorb a transient gateway glitch."""
        try:
            await self.device.async_update()
        except ModbusError as err:
            LOGGER.debug("Poll attempt failed, retrying once: %s", err)
            await asyncio.sleep(_UPDATE_RETRY_DELAY)
            await self.device.async_update()
