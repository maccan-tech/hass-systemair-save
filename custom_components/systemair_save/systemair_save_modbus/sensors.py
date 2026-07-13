"""Duct temperature inputs."""

from __future__ import annotations

from .model import SaveComponent, temperature


class Sensors(SaveComponent):
    """Physical temperature sensor inputs.

    Naming follows the airflow path through the unit.
    """

    supply_air = temperature(
        214,
        maker_key="REG_SENSOR_SAT",
        description="Supply air temperature (into the dwelling)",
    )
    extract_air = temperature(
        215,
        maker_key="REG_SENSOR_ETT",
        description="Extract air temperature (out of the dwelling)",
    )
    exhaust_air = temperature(
        216,
        maker_key="REG_SENSOR_EAT",
        description="Exhaust air temperature (after the heat exchanger)",
    )
    outdoor_air = temperature(
        218,
        maker_key="REG_SENSOR_OAT",
        description="Outdoor air temperature (fresh air intake)",
    )
