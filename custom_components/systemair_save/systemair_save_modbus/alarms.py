"""Unit alarms: the REG_ALARMS_ALL block exposed as coils 12801-12809.

A coil value of 1 means the alarm is active. Coil 12803 is marked "not used"
in the manufacturer's variable list and is not modeled.
"""

from __future__ import annotations

from .model import SaveComponent, coil


class Alarms(SaveComponent):
    """Alarm outputs of the unit (read-only)."""

    filter = coil(
        12801,
        maker_category="REG_ALARMS_ALL",
        description="Filter alarm",
    )
    fan = coil(
        12802,
        maker_category="REG_ALARMS_ALL",
        description="Fan alarm",
    )
    rotor = coil(
        12804,
        maker_category="REG_ALARMS_ALL",
        description="Rotor alarm",
    )
    frost = coil(
        12805,
        maker_category="REG_ALARMS_ALL",
        description="Frost alarm",
    )
    pcu_pb = coil(
        12806,
        maker_category="REG_ALARMS_ALL",
        description="PCU-PB alarm",
    )
    temperature_sensor = coil(
        12807,
        maker_category="REG_ALARMS_ALL",
        description="Temperature sensor alarm",
    )
    emergency_thermostat = coil(
        12808,
        maker_category="REG_ALARMS_ALL",
        description="Emergency thermostat alarm",
    )
    damper = coil(
        12809,
        maker_category="REG_ALARMS_ALL",
        description="Damper alarm",
    )
