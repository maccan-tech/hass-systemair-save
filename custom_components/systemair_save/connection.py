"""Open the Modbus link to the SAVE unit's network gateway."""

from __future__ import annotations

from typing import TYPE_CHECKING

from modbus_connection.tmodbus import connect_serial, connect_tcp

from .const import CONNECT_TIMEOUT, FRAMER_RTU

if TYPE_CHECKING:
    from modbus_connection import ModbusConnection


async def async_connect(
    host: str,
    port: int,
    framer: str,
    *,
    message_spacing: float | None = None,
) -> ModbusConnection:
    """
    Open a native Modbus TCP or an RTU-over-TCP connection.

    RTU over TCP is a serial line carried on a socket, so modbus-connection
    opens it as a serial link on a socket:// device (``framer=`` on
    ``connect_tcp`` is deprecated since modbus-connection 4).
    """
    if framer == FRAMER_RTU:
        address = f"[{host}]" if ":" in host else host
        return await connect_serial(
            f"socket://{address}:{port}",
            framer="rtu",
            timeout=CONNECT_TIMEOUT,
            message_spacing=message_spacing,
        )
    return await connect_tcp(
        host,
        port=port,
        timeout=CONNECT_TIMEOUT,
        message_spacing=message_spacing,
    )
