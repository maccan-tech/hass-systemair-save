"""Constants for the Systemair SAVE integration."""

from datetime import timedelta
from logging import Logger, getLogger
from typing import Final

LOGGER: Logger = getLogger(__package__)

DOMAIN: Final = "systemair_save"

CONF_UNIT_ID: Final = "unit_id"
CONF_FRAMER: Final = "framer"

FRAMER_SOCKET: Final = "socket"  # native Modbus TCP (MBAP)
FRAMER_RTU: Final = "rtu"  # RTU-over-TCP (transparent serial gateways)

DEFAULT_PORT: Final = 502
DEFAULT_UNIT_ID: Final = 1  # the unit's default Modbus station address

# A ventilation unit changes slowly, but we poll aggressively and fixed.
SCAN_INTERVAL: Final = timedelta(seconds=30)

# TCP gateways in front of the unit's RS-485 bus are slow and occasionally
# glitchy: give each request extra headroom and leave a small gap between
# requests so back-to-back block reads do not overrun the gateway.
CONNECT_TIMEOUT: Final = 5.0  # seconds per request
MESSAGE_SPACING: Final = 0.05  # seconds between requests
