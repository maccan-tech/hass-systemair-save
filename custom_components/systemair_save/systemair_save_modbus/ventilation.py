"""Ventilation control state: fan speed, setpoint levels, pre-heater and rotor.

The supply-air setpoint is level-based: the writable knob is the setpoint
*level* (REG 207, ``0`` = manual summer mode, ``1``-``5`` selects one of the
five temperatures configured in REG 209-213). The resulting setpoint itself
(REG 208) is read-only.
"""

from __future__ import annotations

from .enums import (
    CoolerType,
    FanSpeedLevel,
    HeaterType,
    PcuPbRelays,
    PreheaterType,
    RotorState,
)
from .exceptions import SaveValueValidationError
from .model import SaveComponent, enum, flags, integer, temperature

# Level 0 disables the temperature control ("manual summer mode").
TEMPERATURE_LEVEL_MANUAL_SUMMER = 0
TEMPERATURE_LEVEL_MAX = 5


class Ventilation(SaveComponent):
    """Unit-wide ventilation status and settings."""

    fan_speed_level = enum(
        101,
        FanSpeedLevel,
        # The enum class doubles as the write validator: an unknown level code
        # raises ValueError instead of being written to the unit.
        writable=FanSpeedLevel,
        maker_key="REG_FAN_SPEED_LEVEL",
        description="Fan speed level for both fans",
    )

    # NVM-stored configuration values: R/W in the manufacturer list, but
    # deliberately modeled read-only — they describe the installed hardware.
    heater_type = enum(
        201,
        HeaterType,
        maker_key="REG_HC_HEATER_TYPE",
        description="Installed heating-coil type",
    )

    cooler_type = enum(
        202,
        CoolerType,
        maker_key="REG_HC_COOLER_TYPE",
        description="Installed cooling-coil type",
    )

    # The writable setpoint channel. The manual also documents "6 to 29:
    # extension of levels 1 to 5"; only the base 0-5 range is accepted here.
    temperature_level = integer(
        207,
        signed=False,
        writable=True,
        min_value=TEMPERATURE_LEVEL_MANUAL_SUMMER,
        max_value=TEMPERATURE_LEVEL_MAX,
        maker_key="REG_HC_TEMP_LVL",
        description="Temperature setpoint level (0 = manual summer mode)",
    )

    temperature_setpoint = temperature(
        208,
        maker_key="REG_HC_TEMP_SP",
        description="Resulting supply air temperature setpoint",
    )

    temperature_level_1 = temperature(
        209,
        maker_key="REG_HC_TEMP_LVL1",
        description="Configured temperature for level 1",
    )
    temperature_level_2 = temperature(
        210,
        maker_key="REG_HC_TEMP_LVL2",
        description="Configured temperature for level 2",
    )
    temperature_level_3 = temperature(
        211,
        maker_key="REG_HC_TEMP_LVL3",
        description="Configured temperature for level 3",
    )
    temperature_level_4 = temperature(
        212,
        maker_key="REG_HC_TEMP_LVL4",
        description="Configured temperature for level 4",
    )
    temperature_level_5 = temperature(
        213,
        maker_key="REG_HC_TEMP_LVL5",
        description="Configured temperature for level 5",
    )

    # NVM configuration value, modeled read-only like heater/cooler type.
    preheater_type = enum(
        220,
        PreheaterType,
        maker_key="REG_HC_PRE-HEATER_TYPE",
        description="Installed pre-heater type",
    )

    rotor_state = enum(
        351,
        RotorState,
        maker_key="REG_ROTOR_STATE",
        description="Rotary heat-exchanger state",
    )

    # The relay word is the live "heating right now" status; the *_type
    # fields above only describe the installed hardware.
    pcu_pb_relays = flags(
        751,
        PcuPbRelays,
        maker_key="REG_PCU_PB_RELAYS",
        description="PCU-PB relay outputs (pre-heater / re-heater / common)",
    )

    @property
    def preheater_relay_active(self) -> bool | None:
        """Whether the pre-heater relay is energized (coil 12001)."""
        return self._relay_active(PcuPbRelays.PREHEATER)

    @property
    def reheater_relay_active(self) -> bool | None:
        """Whether the re-heater relay is energized (coil 12002)."""
        return self._relay_active(PcuPbRelays.REHEATER)

    @property
    def heater_common_relay_active(self) -> bool | None:
        """Whether the common heater/pre-heater relay is energized (coil 12003)."""
        return self._relay_active(PcuPbRelays.COMMON)

    def _relay_active(self, relay: PcuPbRelays) -> bool | None:
        relays = self.pcu_pb_relays
        if relays is None:
            return None
        return relay in relays

    @property
    def temperature_levels(self) -> tuple[float | None, ...]:
        """The five configured setpoint temperatures, for levels 1-5."""
        return (
            self.temperature_level_1,
            self.temperature_level_2,
            self.temperature_level_3,
            self.temperature_level_4,
            self.temperature_level_5,
        )

    def level_for_temperature(self, celsius: float) -> int:
        """Return the setpoint level whose temperature is closest to ``celsius``.

        ``0`` or below selects manual summer mode (temperature control off).
        Raises :class:`SaveValueValidationError` when the level temperatures
        have not been read yet.
        """
        if celsius <= 0:
            return TEMPERATURE_LEVEL_MANUAL_SUMMER
        candidates = [
            (abs(temperature - celsius), level)
            for level, temperature in enumerate(self.temperature_levels, start=1)
            if temperature is not None
        ]
        if not candidates:
            raise SaveValueValidationError(
                "Temperature levels have not been read from the unit yet"
            )
        return min(candidates)[1]

    async def set_fan_speed_level(self, level: FanSpeedLevel) -> None:
        """Set the fan speed level for both fans."""
        await self.write("fan_speed_level", level)

    async def set_temperature_level(self, level: int) -> None:
        """Set the temperature setpoint level (0 = manual summer mode, 1-5)."""
        await self.write("temperature_level", level)
