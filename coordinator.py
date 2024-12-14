"""Class representing a Dutch and Dutch update coordinator."""

from datetime import timedelta
import logging

from .dutchdutch_api import DutchDutchApi

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=5)


class DutchDutchCoordinator(DataUpdateCoordinator[None]):
    """Dutch & Dutch update coordinator."""

    def __init__(self, hass: HomeAssistant, client: DutchDutchApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.client = client

    async def _async_setup(self) -> None:
        """Called once at setup time only."""
        return None

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        await self.client.async_update()

    async def devices_update_callback(self):
        """Receive callback from api with device update."""
        return None
