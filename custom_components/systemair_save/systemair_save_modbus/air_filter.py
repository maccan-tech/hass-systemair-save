"""Filter monitoring: replacement interval, elapsed days, and the timer reset.

The filter alarm itself lives with the other alarm coils in
:class:`~systemair_save_modbus.alarms.Alarms`.
"""

from __future__ import annotations

from .model import SaveComponent, integer


class AirFilter(SaveComponent):
    """Filter replacement bookkeeping."""

    period = integer(
        601,
        signed=False,
        unit="months",
        maker_key="REG_FILTER_PER",
        description="Filter replacement time in months",
    )

    days = integer(
        602,
        signed=False,
        writable=True,
        min_value=0,
        unit="d",
        maker_key="REG_FILTER_DAYS",
        description="Elapsed days since the last filter replacement",
    )

    async def async_reset(self) -> None:
        """Restart the filter timer after a filter replacement.

        Zeroes the elapsed-days counter; the configured replacement period is
        left untouched.
        """
        await self.write("days", 0)
