"""The Pixoo REST integration."""
from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import (
    CONF_BASE_PATH,
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    SERVICE_DRAW_GIF_FROM_URL,
    SERVICE_DRAW_IMAGE_FROM_URL,
    SERVICE_DRAW_TEXT,
    SERVICE_DRAW_TEXT_FROM_URL,
    SERVICE_PASSTHROUGH,
    SERVICE_SCREEN_ON_OFF,
    SERVICE_SET_BRIGHTNESS,
    SERVICE_SET_CHANNEL,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = []


def _base_url(entry: ConfigEntry) -> str:
    base_path = entry.data.get(CONF_BASE_PATH, "").strip("/")
    url = f"http://{entry.data[CONF_HOST]}:{entry.data[CONF_PORT]}"
    return f"{url}/{base_path}" if base_path else url


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Pixoo REST from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {"base_url": _base_url(entry)}

    if not hass.services.has_service(DOMAIN, SERVICE_DRAW_IMAGE_FROM_URL):
        _register_services(hass)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    hass.data[DOMAIN].pop(entry.entry_id, None)

    if not hass.data[DOMAIN]:
        for service in (
            SERVICE_DRAW_IMAGE_FROM_URL,
            SERVICE_DRAW_GIF_FROM_URL,
            SERVICE_DRAW_TEXT_FROM_URL,
            SERVICE_DRAW_TEXT,
            SERVICE_SET_BRIGHTNESS,
            SERVICE_SET_CHANNEL,
            SERVICE_SCREEN_ON_OFF,
            SERVICE_PASSTHROUGH,
        ):
            hass.services.async_remove(DOMAIN, service)

    return True


def _first_base_url(hass: HomeAssistant) -> str:
    """Return the base URL of an arbitrary configured entry.

    Services are registered once, domain-wide, but each config entry has its
    own server. Multiple entries are unlikely, so the first is used; a
    per-target selector can be added if that turns out to be needed.
    """
    entries = list(hass.data.get(DOMAIN, {}).values())
    if not entries:
        raise HomeAssistantError("No Pixoo REST config entry is set up.")
    return entries[0]["base_url"]


async def _request(hass: HomeAssistant, method: str, path: str, **kwargs) -> None:
    session = async_get_clientsession(hass)
    url = f"{_first_base_url(hass)}{path}"

    try:
        response = await session.request(method, url, **kwargs)
        response.raise_for_status()
    except Exception as err:  # noqa: BLE001 - surfaced to the user as-is
        raise HomeAssistantError(f"Pixoo REST call to {path} failed: {err}") from err


def _register_services(hass: HomeAssistant) -> None:
    async def draw_image_from_url(call: ServiceCall) -> None:
        await _request(
            hass,
            "POST",
            "/download/image",
            data={
                "url": call.data["url"],
                "x": call.data.get("x", 0),
                "y": call.data.get("y", 0),
                "push_immediately": call.data.get("push_immediately", True),
            },
        )

    async def draw_gif_from_url(call: ServiceCall) -> None:
        await _request(
            hass,
            "POST",
            "/download/gif",
            data={
                "url": call.data["url"],
                "animation_speed": call.data.get("animation_speed", 100),
                "skip_first_frame": call.data.get("skip_first_frame", False),
            },
        )

    async def draw_text_from_url(call: ServiceCall) -> None:
        await _request(
            hass,
            "POST",
            "/download/text",
            data={
                "id": call.data.get("id", 1),
                "url": call.data["url"],
                "x": call.data.get("x", 0),
                "y": call.data.get("y", 0),
                "horizontal_alignment": call.data.get("horizontal_alignment", 1),
                "update_interval": call.data.get("update_interval", 60),
            },
        )

    async def draw_text(call: ServiceCall) -> None:
        await _request(
            hass,
            "POST",
            "/text",
            data={
                "text": call.data["text"],
                "x": call.data.get("x", 0),
                "y": call.data.get("y", 0),
                "r": call.data.get("r", 255),
                "g": call.data.get("g", 255),
                "b": call.data.get("b", 255),
                "push_immediately": call.data.get("push_immediately", True),
            },
        )

    async def set_brightness(call: ServiceCall) -> None:
        await _request(hass, "PUT", f"/brightness/{call.data['percentage']}")

    async def set_channel(call: ServiceCall) -> None:
        await _request(hass, "PUT", f"/channel/{call.data['number']}")

    async def screen_on_off(call: ServiceCall) -> None:
        await _request(hass, "PUT", f"/screen/on/{call.data['on']}")

    async def passthrough(call: ServiceCall) -> None:
        await _request(hass, "POST", f"/{call.data['route'].lstrip('/')}", json=call.data.get("payload", {}))

    hass.services.async_register(
        DOMAIN,
        SERVICE_DRAW_IMAGE_FROM_URL,
        draw_image_from_url,
        schema=vol.Schema(
            {
                vol.Required("url"): cv.string,
                vol.Optional("x"): cv.positive_int,
                vol.Optional("y"): cv.positive_int,
                vol.Optional("push_immediately"): cv.boolean,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DRAW_GIF_FROM_URL,
        draw_gif_from_url,
        schema=vol.Schema(
            {
                vol.Required("url"): cv.string,
                vol.Optional("animation_speed"): cv.positive_int,
                vol.Optional("skip_first_frame"): cv.boolean,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DRAW_TEXT_FROM_URL,
        draw_text_from_url,
        schema=vol.Schema(
            {
                vol.Required("url"): cv.string,
                vol.Optional("id"): vol.All(int, vol.Range(min=0, max=39)),
                vol.Optional("x"): cv.positive_int,
                vol.Optional("y"): cv.positive_int,
                vol.Optional("horizontal_alignment"): vol.All(int, vol.Range(min=1, max=3)),
                vol.Optional("update_interval"): cv.positive_int,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_DRAW_TEXT,
        draw_text,
        schema=vol.Schema(
            {
                vol.Required("text"): cv.string,
                vol.Optional("x"): cv.positive_int,
                vol.Optional("y"): cv.positive_int,
                vol.Optional("r"): vol.All(int, vol.Range(min=0, max=255)),
                vol.Optional("g"): vol.All(int, vol.Range(min=0, max=255)),
                vol.Optional("b"): vol.All(int, vol.Range(min=0, max=255)),
                vol.Optional("push_immediately"): cv.boolean,
            }
        ),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_BRIGHTNESS,
        set_brightness,
        schema=vol.Schema({vol.Required("percentage"): vol.All(int, vol.Range(min=0, max=100))}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_CHANNEL,
        set_channel,
        schema=vol.Schema({vol.Required("number"): cv.positive_int}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_SCREEN_ON_OFF,
        screen_on_off,
        schema=vol.Schema({vol.Required("on"): cv.boolean}),
    )
    hass.services.async_register(
        DOMAIN,
        SERVICE_PASSTHROUGH,
        passthrough,
        schema=vol.Schema(
            {
                vol.Required("route"): cv.string,
                vol.Optional("payload", default={}): dict,
            }
        ),
    )
