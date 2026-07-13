"""SAVE-specific pieces layered on the ``modbus_connection.model`` framework."""

from __future__ import annotations

from collections.abc import Callable
from enum import IntEnum, IntFlag
from typing import Any

from modbus_connection.model import (
    Component,
    RegisterField,
)
from modbus_connection.model import (
    coil as _modbus_coil,
)
from modbus_connection.model import (
    enum as _modbus_enum,
)
from modbus_connection.model import (
    flags as _modbus_flags,
)
from modbus_connection.model import (
    gauge as _modbus_gauge,
)
from modbus_connection.model import (
    integer as _modbus_integer,
)

from .addresses import coil_address, register_address
from .exceptions import SaveValueValidationError
from .metadata import (
    BooleanMetadata,
    DatapointMetadata,
    EnumMetadata,
    NumberMetadata,
    OptionMetadata,
    attach_metadata,
    step_from_digits,
)
from .ranges import COIL_RANGES, REGISTER_RANGES


def _number_validator(
    *,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    step: float | int | None = None,
) -> Callable[[Any], Any]:
    """Return a write validator for numeric SAVE values."""

    def validate(value: Any) -> Any:
        number = float(value)

        if min_value is not None and number < min_value:
            raise SaveValueValidationError(
                f"Value {value} is below minimum {min_value}"
            )

        if max_value is not None and number > max_value:
            raise SaveValueValidationError(
                f"Value {value} is above maximum {max_value}"
            )

        # Step is primarily UI metadata for now. Avoid hard float-modulo
        # validation until we see invalid writes slipping through.
        return value

    return validate


def _allowed_values_validator(
    allowed_values: tuple[float | int, ...],
) -> Callable[[Any], Any]:
    """Return a write validator that only accepts a discrete set of values."""
    allowed = {float(value) for value in allowed_values}

    def validate(value: Any) -> Any:
        if float(value) not in allowed:
            raise SaveValueValidationError(
                f"Value {value} is not one of {sorted(allowed_values)}"
            )
        return value

    return validate


def _with_number_validator(
    writable: bool | Callable[[Any], Any],
    *,
    min_value: float | int | None,
    max_value: float | int | None,
    step: float | int | None,
    allowed_values: tuple[float | int, ...] | None = None,
) -> bool | Callable[[Any], Any]:
    """Return writable or a validator-backed writable value."""
    if not writable:
        return False

    if callable(writable):
        return writable

    if allowed_values is not None:
        return _allowed_values_validator(allowed_values)

    if min_value is None and max_value is None and step is None:
        return True

    return _number_validator(
        min_value=min_value,
        max_value=max_value,
        step=step,
    )


def integer(
    reg_number: int,
    *args: Any,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    step: float | int | None = None,
    digits: int | None = None,
    unit: str | None = None,
    raw_min: float | int | None = None,
    raw_max: float | int | None = None,
    allowed_values: tuple[float | int, ...] | None = None,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    writable: bool | Callable[[Any], Any] = False,
    **kwargs: Any,
):
    """Create an integer field from a manufacturer Systemair REG reference."""
    effective_step = step if step is not None else step_from_digits(digits)
    effective_writable = _with_number_validator(
        writable,
        min_value=min_value,
        max_value=max_value,
        step=effective_step,
        allowed_values=allowed_values,
    )

    field = _modbus_integer(
        register_address(reg_number),
        *args,
        writable=effective_writable,
        unit=unit,
        **kwargs,
    )

    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            maker_reference=reg_number,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=bool(writable),
            number=NumberMetadata(
                min_value=min_value,
                max_value=max_value,
                step=effective_step,
                digits=digits,
                unit=unit,
                raw_min=raw_min,
                raw_max=raw_max,
                allowed_values=allowed_values,
            ),
        ),
    )


def gauge(
    reg_number: int,
    scale: float,
    *args: Any,
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    step: float | int | None = None,
    digits: int | None = None,
    unit: str | None = None,
    raw_min: float | int | None = None,
    raw_max: float | int | None = None,
    allowed_values: tuple[float | int, ...] | None = None,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    writable: bool | Callable[[Any], Any] = False,
    **kwargs: Any,
):
    """Create a gauge field from a manufacturer Systemair REG reference."""
    effective_step = step if step is not None else step_from_digits(digits)
    effective_writable = _with_number_validator(
        writable,
        min_value=min_value,
        max_value=max_value,
        step=effective_step,
        allowed_values=allowed_values,
    )

    field = _modbus_gauge(
        register_address(reg_number),
        scale,
        *args,
        writable=effective_writable,
        unit=unit,
        **kwargs,
    )

    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="number",
            maker_reference=reg_number,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=bool(writable),
            number=NumberMetadata(
                min_value=min_value,
                max_value=max_value,
                step=effective_step,
                digits=digits,
                unit=unit,
                raw_min=raw_min,
                raw_max=raw_max,
                allowed_values=allowed_values,
            ),
        ),
    )


def enum(
    reg_number: int,
    enum_type: type[IntEnum],
    *args: Any,
    options: tuple[OptionMetadata, ...] | None = None,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    writable: bool | Callable[[Any], Any] = False,
    **kwargs: Any,
):
    """Create an enum field from a manufacturer Systemair REG reference."""
    field = _modbus_enum(
        register_address(reg_number),
        enum_type,
        *args,
        writable=writable,
        **kwargs,
    )

    resolved_options = options or tuple(
        OptionMetadata(member.name.lower(), int(member), member.name)
        for member in enum_type
    )

    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="enum",
            maker_reference=reg_number,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=bool(writable),
            enum=EnumMetadata(enum_type=enum_type, options=resolved_options),
        ),
    )


def flags(
    reg_number: int,
    flag_type: type[IntFlag],
    *args: Any,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
    writable: bool | Callable[[Any], Any] = False,
    **kwargs: Any,
):
    """Create a bitfield register from a manufacturer Systemair REG reference.

    Reading the register word instead of the coil block keeps the addressing
    unambiguous (see the ``coiladress = registeradress x 16 - 15`` mapping).
    """
    field = _modbus_flags(
        register_address(reg_number),
        flag_type,
        *args,
        writable=writable,
        **kwargs,
    )

    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="raw",
            maker_reference=reg_number,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=bool(writable),
        ),
    )


def coil(
    cl_number: int,
    *,
    stride: int = 0,
    writable: bool = False,
    false_key: str = "off",
    true_key: str = "on",
    false_label: str | None = None,
    true_label: str | None = None,
    inverted: bool = False,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
):
    """Create a coil field from a manufacturer Systemair coil number."""
    field = _modbus_coil(
        coil_address(cl_number),
        stride=stride,
        writable=writable,
    )

    return attach_metadata(
        field,
        DatapointMetadata(
            value_kind="boolean",
            maker_reference=cl_number,
            maker_key=maker_key,
            maker_category=maker_category,
            description=description,
            writable=writable,
            boolean=BooleanMetadata(
                false_key=false_key,
                true_key=true_key,
                false_label=false_label,
                true_label=true_label,
                inverted=inverted,
            ),
        ),
    )


def temperature(
    reg_number: int,
    *,
    stride: int = 0,
    writable: bool = False,
    unit: str = "°C",
    min_value: float | int | None = None,
    max_value: float | int | None = None,
    step: float | int | None = None,
    digits: int | None = None,
    raw_min: float | int | None = None,
    raw_max: float | int | None = None,
    allowed_values: tuple[float | int, ...] | None = None,
    maker_key: str | None = None,
    maker_category: str | None = None,
    description: str | None = None,
) -> RegisterField[float]:
    """A signed 0.1-scaled Systemair temperature register."""
    return gauge(
        reg_number,
        0.1,
        signed=True,
        stride=stride,
        writable=writable,
        unit=unit,
        min_value=min_value,
        max_value=max_value,
        step=step,
        digits=digits,
        raw_min=raw_min,
        raw_max=raw_max,
        allowed_values=allowed_values,
        maker_key=maker_key,
        maker_category=maker_category,
        description=description,
    )


class SaveComponent(Component):
    """A SAVE sub-system: readable ranges + neutral datapoint metadata."""

    register_ranges = REGISTER_RANGES
    coil_ranges = COIL_RANGES
    # Conservative read width: TCP gateways in front of the unit's RS-485 bus
    # commonly cap a single read well below the Modbus ceiling of 125.
    max_span = 50

    def metadata_for(self, field: str) -> DatapointMetadata | None:
        """Return neutral SAVE metadata for a field."""
        descriptor = self._register_fields.get(field)
        if descriptor is None:
            descriptor = self._bit_fields.get(field)
        if descriptor is None:
            return None
        return getattr(descriptor, "save_metadata", None)

    def require_metadata_for(self, field: str) -> DatapointMetadata:
        """Return SAVE metadata for a field or raise."""
        metadata = self.metadata_for(field)
        if metadata is None:
            raise AttributeError(f"unknown or untyped SAVE field {field!r}")
        return metadata
