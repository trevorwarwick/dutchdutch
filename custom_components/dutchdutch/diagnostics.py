"""Diagnostics support for Dutch & Dutch."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .dutchdutch_api import DutchDutchApi


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    client: DutchDutchApi = hass.data[DOMAIN][entry.entry_id]

    return await client.async_get_diagnostics()
