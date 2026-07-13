"""Address helpers for Systemair register and coil references.

The manufacturer's Modbus variable list for the SAVE residential units numbers
registers from 1 (e.g. REG 101 = fan speed level). The Modbus protocol uses
zero-based PDU addresses, so REG 101 is read at address 100. Coils are
different: the variable list gives coil addresses directly in the protocol's
zero-based numbering (e.g. coil 12801 = filter alarm), so no conversion is
applied there. Both conversions are kept in this module so component
definitions can stay aligned with the maker docs.
"""

REGISTER_REFERENCE_BASE = 1
REGISTER_REFERENCE_MAX = 65536


def register_address(reg_number: int) -> int:
    """Return the zero-based Modbus address for a Systemair REG reference.

    Examples:
        REG 101 -> Modbus address 100, REG 214 -> Modbus address 213 ...
    """
    if reg_number < REGISTER_REFERENCE_BASE or reg_number > REGISTER_REFERENCE_MAX:
        raise ValueError(
            f"Expected Systemair register reference like 101, got {reg_number}"
        )

    return reg_number - REGISTER_REFERENCE_BASE


def coil_address(coil_number: int) -> int:
    """Return the Modbus address for a Systemair coil reference.

    The manufacturer lists coil addresses in the protocol's own zero-based
    numbering (coil 12801 = filter alarm reads at address 12801), so this is
    the identity — kept as a function so the convention stays in one place.
    """
    if coil_number < 0:
        raise ValueError(f"Invalid Systemair coil address: {coil_number}")

    return coil_number


def reg_range(start_reg: int, end_reg: int) -> tuple[int, int]:
    """Create an inclusive readable register range from REG references."""
    if end_reg < start_reg:
        raise ValueError(f"Invalid Systemair register range: {start_reg}..{end_reg}")

    return register_address(start_reg), register_address(end_reg)


def cl_range(start_cl: int, end_cl: int) -> tuple[int, int]:
    """Create an inclusive readable coil range from coil addresses."""
    if end_cl < start_cl:
        raise ValueError(f"Invalid Systemair coil range: {start_cl}..{end_cl}")

    return coil_address(start_cl), coil_address(end_cl)
