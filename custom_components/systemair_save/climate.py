"""
Climate platform — the ventilation unit as a fan-only thermostat.

The unit has no heating/cooling mode of its own: the fans either run (at low,
medium or high speed, or automatically under demand control) or are off, and
the supply air is tempered towards a level-based setpoint. Extract air is the
closest thing to a room temperature the unit measures, so it is exposed as
the current temperature.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

from homeassistant.components.climate import (
    FAN_AUTO,
    FAN_HIGH,
    FAN_LOW,
    FAN_MEDIUM,
    FAN_OFF,
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature

from .entity import SystemairSaveEntity
from .systemair_save_modbus import FanSpeedLevel, Ventilation

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairSaveCoordinator
    from .data import SystemairSaveConfigEntry

_TO_FAN_MODE = {
    FanSpeedLevel.OFF: FAN_OFF,
    FanSpeedLevel.LOW: FAN_LOW,
    FanSpeedLevel.NORMAL: FAN_MEDIUM,
    FanSpeedLevel.HIGH: FAN_HIGH,
    FanSpeedLevel.AUTO: FAN_AUTO,
}
_FROM_FAN_MODE = {mode: level for level, mode in _TO_FAN_MODE.items()}

# Shown until the unit's configured level temperatures have been read.
_FALLBACK_MAX_TEMP = 22.0


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairSaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the climate platform."""
    async_add_entities([SystemairSaveClimate(entry.runtime_data.coordinator)])


class SystemairSaveClimate(SystemairSaveEntity, ClimateEntity):
    """The ventilation unit as a thermostat (setpoint level + fan speed)."""

    _attr_name = None  # primary entity -> takes the device's name
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes: ClassVar[list[HVACMode]] = [HVACMode.OFF, HVACMode.FAN_ONLY]
    _attr_fan_modes: ClassVar[list[str]] = [
        FAN_OFF,
        FAN_LOW,
        FAN_MEDIUM,
        FAN_HIGH,
        FAN_AUTO,
    ]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.FAN_MODE
        | ClimateEntityFeature.TURN_OFF
        | ClimateEntityFeature.TURN_ON
    )
    _attr_min_temp = 0  # 0 selects manual summer mode (temperature control off)
    _attr_target_temperature_step = 1

    def __init__(self, coordinator: SystemairSaveCoordinator) -> None:
        """Initialize the climate entity."""
        super().__init__(coordinator, key="climate", component="ventilation")

    @property
    def _ventilation(self) -> Ventilation:
        return self._subsystem  # type: ignore[return-value]

    @property
    def max_temp(self) -> float:
        """Return the highest configured level temperature."""
        levels = [t for t in self._ventilation.temperature_levels if t is not None]
        return max(levels) if levels else _FALLBACK_MAX_TEMP

    @property
    def current_temperature(self) -> float | None:
        """Return the extract air temperature (the air leaving the dwelling)."""
        return self.coordinator.device.sensors.extract_air

    @property
    def target_temperature(self) -> float | None:
        """Return the resulting supply air temperature setpoint."""
        return self._ventilation.temperature_setpoint

    @property
    def hvac_mode(self) -> HVACMode | None:
        """Return off when the fans are stopped, fan-only otherwise."""
        level = self._ventilation.fan_speed_level
        if level is None:
            return None
        return HVACMode.OFF if level is FanSpeedLevel.OFF else HVACMode.FAN_ONLY

    @property
    def hvac_action(self) -> HVACAction | None:
        """Return the current HVAC action."""
        level = self._ventilation.fan_speed_level
        if level is None:
            return None
        return HVACAction.OFF if level is FanSpeedLevel.OFF else HVACAction.FAN

    @property
    def fan_mode(self) -> str | None:
        """Return the current fan mode."""
        level = self._ventilation.fan_speed_level
        return _TO_FAN_MODE.get(level) if level is not None else None

    async def async_set_temperature(self, **kwargs: Any) -> None:
        """
        Set a new target temperature via the unit's setpoint levels.

        The requested temperature is mapped to the nearest configured level
        (REG 209-213) and the level index is written; 0 °C selects manual
        summer mode.
        """
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is not None:
            level = self._ventilation.level_for_temperature(temperature)
            await self._ventilation.set_temperature_level(level)
            await self.coordinator.async_request_refresh()

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        """Set a new HVAC mode: off stops the fans, fan-only resumes at medium."""
        if hvac_mode is HVACMode.OFF:
            level = FanSpeedLevel.OFF
        elif self._ventilation.fan_speed_level in (None, FanSpeedLevel.OFF):
            level = FanSpeedLevel.NORMAL
        else:
            return  # already running; keep the current speed
        await self._ventilation.set_fan_speed_level(level)
        await self.coordinator.async_request_refresh()

    async def async_set_fan_mode(self, fan_mode: str) -> None:
        """Set a new fan speed."""
        await self._ventilation.set_fan_speed_level(_FROM_FAN_MODE[fan_mode])
        await self.coordinator.async_request_refresh()
