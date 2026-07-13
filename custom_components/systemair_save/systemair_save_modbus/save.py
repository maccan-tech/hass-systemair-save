"""The top-level SystemairSave device object."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from modbus_connection.model import Component, ComponentGroup

from .addresses import register_address
from .air_filter import AirFilter
from .alarms import Alarms
from .device_info import DeviceInformation, model_name
from .enums import SystemType
from .sensors import Sensors
from .ventilation import Ventilation

if TYPE_CHECKING:
    from modbus_connection import ModbusUnit

SYSTEM_TYPE_REG = 501  # REG 501, the safe single-register identity probe

STORE_NVM_REG = 549  # REG_STORE_NVM; accepts FC06 only
STORE_NVM_CODE = 165  # magic value that persists the volatile settings


@dataclass(frozen=True)
class SaveProbe:
    """Result of the safe setup probe."""

    system_type: SystemType | None

    @property
    def model_name(self) -> str:
        """Return the user-facing model name."""
        return f"Systemair {model_name(self.system_type)}"


class SystemairSave:
    """A Systemair SAVE ventilation unit."""

    def __init__(self, unit: ModbusUnit) -> None:
        self._unit = unit

        self.info = DeviceInformation(unit)
        self.sensors = Sensors(unit)
        self.ventilation = Ventilation(unit)
        self.air_filter = AirFilter(unit)
        self.alarms = Alarms(unit)

        self._group = ComponentGroup(unit, self.components)

    @classmethod
    async def async_probe(cls, unit: ModbusUnit) -> SaveProbe:
        """Read only the system-type register to identify the unit."""
        raw = (
            await unit.read_holding_registers(
                register_address(SYSTEM_TYPE_REG),
                1,
            )
        )[0]

        try:
            system_type: SystemType | None = SystemType(raw)
        except ValueError:
            system_type = None

        return SaveProbe(system_type=system_type)

    @property
    def components(self) -> tuple[Component, ...]:
        """Return every actively polled subsystem."""
        return (
            self.info,
            self.sensors,
            self.ventilation,
            self.air_filter,
            self.alarms,
        )

    async def async_update(self) -> None:
        """Refresh all active subsystems in pooled Modbus reads."""
        await self._group.async_update()

    async def async_store_settings(self) -> None:
        """Persist the volatile settings to the unit's non-volatile memory.

        Writes the magic code to ``REG_STORE_NVM`` (FC06), which stores the
        fan speed level, the temperature setpoint level, and the configured
        fan flows in EEPROM so they survive a power cycle. Sparingly — every
        call is an EEPROM write.
        """
        await self._unit.write_register(register_address(STORE_NVM_REG), STORE_NVM_CODE)
