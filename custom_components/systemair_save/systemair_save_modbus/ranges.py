"""Readable Systemair SAVE Modbus ranges.

Definitions use manufacturer references:

- register references such as REG 214
- coil references such as CL 12802

The ranges are derived from the manufacturer's variable list (D24810) and
verified against a running SAVE VSR 300. Known gaps between the blocks are
preserved intentionally so pooled reads stay on documented addresses.
"""

from __future__ import annotations

from .addresses import cl_range, reg_range


def _reg_ranges(
    *ranges: tuple[int, int],
) -> tuple[tuple[int, int], ...]:
    """Convert manufacturer REG ranges to Modbus PDU ranges."""
    return tuple(reg_range(start, end) for start, end in ranges)


def _cl_ranges(
    *ranges: tuple[int, int],
) -> tuple[tuple[int, int], ...]:
    """Convert manufacturer coil ranges to Modbus PDU ranges."""
    return tuple(cl_range(start, end) for start, end in ranges)


# SAVE VSR 300 (residential SAVE register profile).
REGISTER_RANGES = _reg_ranges(
    (101, 101),  # fan speed level
    (111, 112),  # supply / extract fan rpm
    (201, 202),  # heater type / cooler type
    (207, 213),  # setpoint level / resulting setpoint / level temperatures 1-5
    (214, 216),  # supply / extract / exhaust air temperature
    (218, 218),  # outdoor air temperature
    (220, 220),  # pre-heater type
    (351, 351),  # rotor state code
    (501, 504),  # system type / program version high-mid-low
    (601, 602),  # filter period / filter days
    (751, 751),  # PCU-PB relay outputs
)

COIL_RANGES = _cl_ranges(
    (12801, 12809),  # REG_ALARMS_ALL alarm block (12803 unused but readable)
)
