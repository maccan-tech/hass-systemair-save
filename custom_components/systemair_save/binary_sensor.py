"""
Binary-sensor platform — alarm outputs and PCU-PB heater relays.

The alarms come from the REG_ALARMS_ALL coil block. The relay states come
from the REG_PCU_PB_RELAYS word and show whether the pre-heater/re-heater is
actually energized right now (the *_type sensors only describe the installed
hardware).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.const import EntityCategory

from .entity import SystemairSaveEntity

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import SystemairSaveCoordinator
    from .data import SystemairSaveConfigEntry


@dataclass(frozen=True, kw_only=True)
class SystemairSaveBinaryDescription(BinarySensorEntityDescription):
    """Describes a binary sensor reading one boolean of one component."""

    component: str
    attribute: str


def _alarm(
    attribute: str, name: str, *, key: str | None = None
) -> SystemairSaveBinaryDescription:
    return SystemairSaveBinaryDescription(
        key=key or f"alarms_{attribute}",
        name=name,
        component="alarms",
        attribute=attribute,
        device_class=BinarySensorDeviceClass.PROBLEM,
    )


BINARY_SENSORS: tuple[SystemairSaveBinaryDescription, ...] = (
    # The filter alarm keeps its pre-Alarms-component key so existing entity
    # unique IDs survive the refactor.
    _alarm("filter", "Filter alarm", key="air_filter_alarm"),
    _alarm("fan", "Fan alarm"),
    _alarm("rotor", "Rotor alarm"),
    _alarm("frost", "Frost alarm"),
    _alarm("pcu_pb", "PCU-PB alarm"),
    _alarm("temperature_sensor", "Temperature sensor alarm"),
    _alarm("emergency_thermostat", "Emergency thermostat alarm"),
    _alarm("damper", "Damper alarm"),
    SystemairSaveBinaryDescription(
        key="ventilation_preheater_relay",
        name="Pre-heater active",
        component="ventilation",
        attribute="preheater_relay_active",
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    SystemairSaveBinaryDescription(
        key="ventilation_reheater_relay",
        name="Heater active",
        component="ventilation",
        attribute="reheater_relay_active",
        device_class=BinarySensorDeviceClass.HEAT,
    ),
    SystemairSaveBinaryDescription(
        key="ventilation_heater_common_relay",
        name="Heater common relay",
        component="ventilation",
        attribute="heater_common_relay_active",
        device_class=BinarySensorDeviceClass.POWER,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: SystemairSaveConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    coordinator = entry.runtime_data.coordinator
    async_add_entities(
        SystemairSaveBinarySensor(coordinator, d) for d in BINARY_SENSORS
    )


class SystemairSaveBinarySensor(SystemairSaveEntity, BinarySensorEntity):
    """A single boolean read from a component attribute."""

    entity_description: SystemairSaveBinaryDescription

    def __init__(
        self,
        coordinator: SystemairSaveCoordinator,
        description: SystemairSaveBinaryDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator, description.key, description.component)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        """Return true if the boolean is set."""
        return getattr(self._subsystem, self.entity_description.attribute)
