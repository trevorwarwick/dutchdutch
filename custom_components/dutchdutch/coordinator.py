"""Class representing a Dutch and Dutch update coordinator."""

from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .dutchdutch_api import DutchDutchApi

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
        self.client.set_push_callback(self.push_callback)

    async def push_callback(self) -> None:
        """Call back from client when a push notification is received."""
        self.async_set_updated_data(True)

    async def _async_setup(self) -> None:
        """Call once at setup time only."""

    async def _async_update_data(self) -> None:
        """Fetch data from API endpoint."""
        await self.client.async_update()
