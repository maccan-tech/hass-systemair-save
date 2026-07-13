"""Custom types for the Systemair SAVE integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from modbus_connection import ModbusConnection

    from .coordinator import SystemairSaveCoordinator


type SystemairSaveConfigEntry = ConfigEntry[SystemairSaveData]


@dataclass
class SystemairSaveData:
    """
    Runtime data for a SAVE config entry.

    Unlike the core integration (which borrows a unit from the shared
    ``modbus_connection`` integration), this custom integration owns its
    connection and must close it on unload.
    """

    connection: ModbusConnection
    coordinator: SystemairSaveCoordinator
