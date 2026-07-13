"""Device identity: manufacturer and model of the ventilation unit.

The model is read from the system-type register (REG 501), so the library
reports what the controller is actually configured as — the register map is
shared across the SAVE residential family, even though only the SAVE has
been verified so far.
"""

from __future__ import annotations

from .enums import SystemType
from .model import SaveComponent, enum

FALLBACK_MODEL = "SAVE ventilation unit"


def model_name(system_type: SystemType | None) -> str:
    """Return the user-facing model name for a system type.

    Splits the enum name at the first digit (``VSR300`` -> ``SAVE VSR 300``);
    ``None`` (not read yet, or an unknown code) falls back to a generic name.
    """
    if system_type is None:
        return FALLBACK_MODEL
    name = system_type.name
    for index, char in enumerate(name):
        if char.isdigit():
            return f"SAVE {name[:index]} {name[index:]}"
    return f"SAVE {name}"


class DeviceInformation(SaveComponent):
    """Unit identity: static manufacturer plus the configured system type."""

    manufacturer = "Systemair"

    system_type = enum(
        501,
        SystemType,
        maker_key="REG_SYSTEM_TYPE",
        description="System type select",
    )

    @property
    def model(self) -> str:
        """Model name, e.g. 'SAVE VSR 300'."""
        return model_name(self.system_type)
