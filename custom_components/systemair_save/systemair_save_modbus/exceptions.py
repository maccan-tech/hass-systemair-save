"""Exceptions raised by systemair-save-modbus."""

from __future__ import annotations


class SaveValueValidationError(ValueError):
    """Raised when a SAVE value is outside its allowed domain."""
