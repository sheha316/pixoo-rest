"""Config flow for the Pixoo REST integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_BASE_PATH,
    CONF_HOST,
    CONF_PORT,
    DEFAULT_BASE_PATH,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME, default="Pixoo REST"): str,
        vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
        vol.Required(CONF_PORT, default=DEFAULT_PORT): int,
        vol.Optional(CONF_BASE_PATH, default=DEFAULT_BASE_PATH): str,
    }
)


async def _can_connect(hass, host: str, port: int, base_path: str) -> bool:
    session = async_get_clientsession(hass)
    base_path = base_path.strip("/")
    url = f"http://{host}:{port}"
    if base_path:
        url = f"{url}/{base_path}"
    url = f"{url}/health"

    try:
        response = await session.get(url, timeout=10)
        return response.status == 200
    except Exception:  # noqa: BLE001
        return False


class PixooRestConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Pixoo REST."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            self._async_abort_entries_match(
                {CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]}
            )

            if await _can_connect(
                self.hass,
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_BASE_PATH],
            ):
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)

            errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
