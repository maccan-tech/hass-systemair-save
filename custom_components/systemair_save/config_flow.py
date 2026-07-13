"""Config flow for the Systemair SAVE integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)
from modbus_connection import ModbusError
from modbus_connection.tmodbus import connect_tcp

from .const import (
    CONF_FRAMER,
    CONF_UNIT_ID,
    CONNECT_TIMEOUT,
    DEFAULT_PORT,
    DEFAULT_UNIT_ID,
    DOMAIN,
    FRAMER_RTU,
    FRAMER_SOCKET,
    LOGGER,
)
from .systemair_save_modbus import SystemairSave

STEP_USER = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): vol.Coerce(int),
        vol.Required(CONF_UNIT_ID, default=DEFAULT_UNIT_ID): NumberSelector(
            NumberSelectorConfig(min=1, max=255, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_FRAMER, default=FRAMER_SOCKET): SelectSelector(
            SelectSelectorConfig(
                options=[FRAMER_SOCKET, FRAMER_RTU],
                mode=SelectSelectorMode.DROPDOWN,
                translation_key="framer",
            )
        ),
    }
)


class SystemairSaveConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Systemair SAVE."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Collect the transport parameters, then probe the unit for the title."""
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{user_input[CONF_HOST]}_{user_input[CONF_PORT]}"
                f"_{int(user_input[CONF_UNIT_ID])}"
            )
            self._abort_if_unique_id_configured()
            if (title := await self._async_title(user_input)) is None:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title=title, data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=STEP_USER, errors=errors
        )

    async def _async_title(self, data: dict[str, Any]) -> str | None:
        """Probe the unit for the entry title, or None if unreachable."""
        try:
            connection = await connect_tcp(
                data[CONF_HOST],
                port=data[CONF_PORT],
                framer=data[CONF_FRAMER],
                timeout=CONNECT_TIMEOUT,
            )
        except ModbusError as err:
            LOGGER.warning("Could not open Modbus connection: %s", err)
            return None
        try:
            unit = connection.for_unit(int(data[CONF_UNIT_ID]))
            probe = await SystemairSave.async_probe(unit)
        except (ModbusError, OSError, ValueError) as err:
            LOGGER.warning("Could not probe SAVE: %s", err)
            return None
        finally:
            await connection.close()
        return f"{probe.model_name} ({data[CONF_HOST]})"
