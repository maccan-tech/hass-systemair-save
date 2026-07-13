"""systemair-save-modbus — read a Systemair SAVE ventilation unit over Modbus.

Construct ``SystemairSave(unit)`` with a ``modbus_connection.ModbusUnit``,
call ``await device.async_update()``, then read its sub-systems as normal
Python objects::

    device.sensors.supply_air
    device.ventilation.fan_speed_level
    device.alarms.filter

The library is organized by sub-system — one file each for ``device_info``,
``sensors``, ``ventilation``, ``air_filter`` and ``alarms`` — built on the generic
``Component`` / ``RegisterField`` / ``CoilField`` framework in
``modbus_connection.model``.
"""

from .addresses import coil_address, register_address
from .air_filter import AirFilter
from .alarms import Alarms
from .device_info import DeviceInformation
from .enums import (
    CoolerType,
    FanSpeedLevel,
    HeaterType,
    PcuPbRelays,
    PreheaterType,
    RotorState,
    SystemType,
)
from .exceptions import SaveValueValidationError
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
)
from .save import SaveProbe, SystemairSave
from .sensors import Sensors
from .ventilation import Ventilation

__all__ = [
    "coil_address",
    "register_address",
    "AirFilter",
    "Alarms",
    "CoolerType",
    "DeviceInformation",
    "FanSpeedLevel",
    "HeaterType",
    "PcuPbRelays",
    "PreheaterType",
    "RotorState",
    "Sensors",
    "SystemType",
    "SystemairSave",
    "Ventilation",
    "SaveProbe",
    "SaveValueValidationError",
    "BooleanMetadata",
    "DatapointMetadata",
    "EnumMetadata",
    "NumberMetadata",
    "OptionMetadata",
]
