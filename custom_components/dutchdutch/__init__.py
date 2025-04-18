"""The Dutch and Dutch integration."""

from __future__ import annotations

from .dutchdutch_api import DutchDutchApi

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

PLATFORMS = [Platform.MEDIA_PLAYER]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Dutch & Dutch from a config entry."""
    session = async_get_clientsession(hass)
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = DutchDutchApi(
        entry.data[CONF_HOST], session, None
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Dutch & Dutch config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        del hass.data[DOMAIN][entry.entry_id]
    return unload_ok
