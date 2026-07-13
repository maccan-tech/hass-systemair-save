"""Enumerations used across the SAVE model."""

from __future__ import annotations

from enum import IntEnum, IntFlag


class FanSpeedLevel(IntEnum):
    """Fan speed level for both fans (REG 101).

    Matches the manufacturer's variable list; ``OFF`` is only reachable when
    the unit is configured to allow stopping the fans. ``AUTO`` hands control
    to the demand-control regulator (CO2/RH sensors required).
    """

    OFF = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    AUTO = 4


class SystemType(IntEnum):
    """System type select (REG 501, NVM configuration value).

    Identifies which SAVE residential unit the controller is configured as;
    all other register codes are ignored by the unit.
    """

    VR400 = 0
    VR700 = 1
    VR700DK = 2
    VR400DE = 3
    VTC300 = 4
    VTC700 = 5
    VTR150K = 12
    VTR200B = 13
    VSR300 = 14
    VSR500 = 15
    VSR150 = 16
    VTR300 = 17
    VTR500 = 18
    VSR300DE = 19
    VTC200 = 20


class HeaterType(IntEnum):
    """Installed heating-coil type (REG 201, NVM configuration value)."""

    NONE = 0
    WATER = 1
    ELECTRICAL = 2
    CONTACTOR = 3


class CoolerType(IntEnum):
    """Installed cooling-coil type (REG 202, NVM configuration value)."""

    NONE = 0
    WATER = 1


class PreheaterType(IntEnum):
    """Installed pre-heater type (REG 220, NVM configuration value)."""

    NONE = 0
    ELECTRICAL = 1


class PcuPbRelays(IntFlag):
    """PCU-PB relay outputs (REG 751, one bit per relay).

    The bits mirror the manufacturer's coil block: bit 0 is coil 12001
    (pre-heater relay), bit 1 is coil 12002 (re-heater relay), and bit 2 is
    coil 12003 (common relay for heater and pre-heater).
    """

    PREHEATER = 1
    REHEATER = 2
    COMMON = 4


class RotorState(IntEnum):
    """Rotary heat-exchanger state (REG 351).

    Matches the manufacturer's state list; an unlisted code decodes to
    ``None``.
    """

    NORMAL = 0
    ROTOR_FAULT_ASSUMED = 1
    ROTOR_FAULT_DETECTED = 2
    # Summer mode conditions valid, but summer mode not yet active.
    SUMMER_MODE_PENDING = 3
    SUMMER_MODE = 4
    # Waiting to go out of manual summer mode due to temperature conditions.
    LEAVING_MANUAL_SUMMER_MODE = 5
    MANUAL_SUMMER_MODE = 6
    ROTOR_CLEANING_SUMMER_MODE = 7
    ROTOR_CLEANING_MANUAL_SUMMER_MODE = 8
    FANS_OFF = 9
    ROTOR_CLEANING_FANS_OFF = 10
    # Rotor fault, conditions for rotor fault not valid anymore.
    ROTOR_FAULT_CLEARED = 11
