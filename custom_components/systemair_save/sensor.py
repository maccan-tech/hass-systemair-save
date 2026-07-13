"""
Sensor platform — duct temperatures, fan speed, and filter bookkeeping.

The duct temperatures and the setpoint are the unit's primary readings; the
installed-hardware types, rotor state code, and filter counters are diagnostic.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import EntityCategory, UnitOfTemperature, UnitOfTime

from .entity import SystemairSaveEntity
from .systemair_save_modbus import (
    CoolerType,
    FanSpeedLevel,
    HeaterType,
    PreheaterType,
    RotorState,
    SystemType,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairSaveCoordinator
    from .data import SystemairSaveConfigEntry

_FAN_SPEED_OPTIONS = [level.name.lower() for level in FanSpeedLevel]
_ROTOR_STATE_OPTIONS = [state.name.lower() for state in RotorState]
_HEATER_TYPE_OPTIONS = [heater.name.lower() for heater in HeaterType]
_PREHEATER_TYPE_OPTIONS = [preheater.name.lower() for preheater in PreheaterType]
_COOLER_TYPE_OPTIONS = [cooler.name.lower() for cooler in CoolerType]
_SYSTEM_TYPE_OPTIONS = [system.name.lower() for system in SystemType]


@dataclass(frozen=True, kw_only=True)
class SystemairSaveSensorDescription(SensorEntityDescription):
    """Describes a sensor reading one attribute of one component."""

    component: str
    attribute: str


def _temp(component: str, attribute: str, name: str) -> SystemairSaveSensorDescription:
    return SystemairSaveSensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    )


def _diagnostic(
    component: str, attribute: str, name: str, *, unit: str | None = None
) -> SystemairSaveSensorDescription:
    return SystemairSaveSensorDescription(
        key=f"{component}_{attribute}",
        name=name,
        component=component,
        attribute=attribute,
        native_unit_of_measurement=unit,
        entity_category=EntityCategory.DIAGNOSTIC,
    )


SENSORS: tuple[SystemairSaveSensorDescription, ...] = (
    _temp("sensors", "supply_air", "Supply air temperature"),
    _temp("sensors", "extract_air", "Extract air temperature"),
    _temp("sensors", "exhaust_air", "Exhaust air temperature"),
    _temp("sensors", "outdoor_air", "Outdoor air temperature"),
    _temp("ventilation", "temperature_setpoint", "Temperature setpoint"),
    SystemairSaveSensorDescription(
        key="ventilation_fan_speed_level",
        name="Fan speed level",
        component="ventilation",
        attribute="fan_speed_level",
        device_class=SensorDeviceClass.ENUM,
        options=_FAN_SPEED_OPTIONS,
    ),
    SystemairSaveSensorDescription(
        key="ventilation_preheater_type",
        name="Pre-heater type",
        component="ventilation",
        attribute="preheater_type",
        device_class=SensorDeviceClass.ENUM,
        options=_PREHEATER_TYPE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSaveSensorDescription(
        key="ventilation_rotor_state",
        name="Rotor state",
        component="ventilation",
        attribute="rotor_state",
        device_class=SensorDeviceClass.ENUM,
        options=_ROTOR_STATE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    _diagnostic("air_filter", "period", "Filter period", unit="months"),
    _diagnostic("air_filter", "days", "Filter days", unit=UnitOfTime.DAYS),
    SystemairSaveSensorDescription(
        key="ventilation_heater_type",
        name="Heater type",
        component="ventilation",
        attribute="heater_type",
        device_class=SensorDeviceClass.ENUM,
        options=_HEATER_TYPE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSaveSensorDescription(
        key="ventilation_cooler_type",
        name="Cooler type",
        component="ventilation",
        attribute="cooler_type",
        device_class=SensorDeviceClass.ENUM,
        options=_COOLER_TYPE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    SystemairSaveSensorDescription(
        key="info_system_type",
        name="System type",
        component="info",
        attribute="system_type",
        device_class=SensorDeviceClass.ENUM,
        options=_SYSTEM_TYPE_OPTIONS,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairSaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(SystemairSaveSensor(coordinator, d) for d in SENSORS)


class SystemairSaveSensor(SystemairSaveEntity, SensorEntity):
    """A single value read from a component attribute."""

    entity_description: SystemairSaveSensorDescription

    def __init__(
        self,
        coordinator: SystemairSaveCoordinator,
        description: SystemairSaveSensorDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def native_value(self) -> object:
        """Return the current value, mapping enums to their lowercase name."""
        value = getattr(self._subsystem, self.entity_description.attribute)
        if isinstance(value, IntEnum):
            return value.name.lower()
        return value
