"""
Custom integration for the Systemair SAVE ventilation unit.

Standalone HACS version: it opens and owns its own Modbus TCP connection via
the ``modbus-connection`` library (the core version instead borrows a unit
from the ``modbus_connection`` integration). The device model is the vendored
``systemair_save_modbus`` library in this package.

For more details about this integration, please refer to
https://github.com/maccan-tech/hass-systemair-save
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_HOST, CONF_PORT, Platform
from homeassistant.exceptions import ConfigEntryNotReady
from modbus_connection import ModbusConnectionError
from modbus_connection.tmodbus import connect_tcp

from .const import (
    CONF_FRAMER,
    CONF_UNIT_ID,
    CONNECT_TIMEOUT,
    FRAMER_SOCKET,
    MESSAGE_SPACING,
)
from .coordinator import SystemairSaveCoordinator
from .data import SystemairSaveData
from .systemair_save_modbus import SystemairSave

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import SystemairSaveConfigEntry

PLATFORMS: list[Platform] = [
    Platform.BINARY_SENSOR,
    Platform.BUTTON,
    Platform.CLIMATE,
    Platform.SENSOR,
]


async def async_setup_entry(
    hass: HomeAssistant, entry: SystemairSaveConfigEntry
) -> bool:
    """Set up this integration using UI."""
    try:
        connection = await connect_tcp(
            entry.data[CONF_HOST],
            port=entry.data[CONF_PORT],
            framer=entry.data.get(CONF_FRAMER, FRAMER_SOCKET),
            timeout=CONNECT_TIMEOUT,
            message_spacing=MESSAGE_SPACING,
        )
    except ModbusConnectionError as err:
        msg = f"Could not open Modbus connection: {err}"
        raise ConfigEntryNotReady(msg) from err

    unit = connection.for_unit(int(entry.data[CONF_UNIT_ID]))
    device = SystemairSave(unit)
    coordinator = SystemairSaveCoordinator(hass, entry, device)

    try:
        await coordinator.async_config_entry_first_refresh()
    except ConfigEntryNotReady:
        await connection.close()
        raise

    entry.runtime_data = SystemairSaveData(
        connection=connection, coordinator=coordinator
    )

    # The connection does not self-reconnect: on a drop, reload this entry.
    # Home Assistant's ConfigEntryNotReady retry is the reconnect backoff.
    entry.async_on_unload(
        connection.on_connection_lost(
            lambda: hass.config_entries.async_schedule_reload(entry.entry_id)
        )
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: SystemairSaveConfigEntry
) -> bool:
    """Handle removal of an entry and close the owned connection."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    await entry.runtime_data.connection.close()
    return unload_ok
