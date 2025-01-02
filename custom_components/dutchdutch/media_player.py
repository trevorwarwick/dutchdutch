"""Support for Dutch & Dutch speakers."""

from __future__ import annotations


from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerState,
    MediaType
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import DutchDutchCoordinator

SUPPORT_DUTCHDUTCH = (
    MediaPlayerEntityFeature.VOLUME_SET
    | MediaPlayerEntityFeature.VOLUME_MUTE
    | MediaPlayerEntityFeature.TURN_OFF
    | MediaPlayerEntityFeature.TURN_ON
    | MediaPlayerEntityFeature.SELECT_SOURCE
    | MediaPlayerEntityFeature.SELECT_SOUND_MODE
)

DUTCHDUTCH_TO_HA_FEATURE_MAP = {
    "play": MediaPlayerEntityFeature.PLAY | MediaPlayerEntityFeature.STOP,
    "pause": MediaPlayerEntityFeature.PAUSE,
    "previous": MediaPlayerEntityFeature.PREVIOUS_TRACK,
    "next": MediaPlayerEntityFeature.NEXT_TRACK,
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Dutch & Dutchentry."""
    client = hass.data[DOMAIN][entry.entry_id]
    coordinator = DutchDutchCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([DutchDutchMediaPlayerEntity(coordinator, entry)])


class DutchDutchMediaPlayerEntity(
    CoordinatorEntity[DutchDutchCoordinator], MediaPlayerEntity
):
    """Dutch & Dutchmedia player."""

    _attr_has_entity_name = True
    _attr_name = None

    def __init__(self, coordinator: DutchDutchCoordinator, entry: ConfigEntry) -> None:
        """Initialize the Dutch & Dutch device."""
        self.coordinator = coordinator
        super().__init__(coordinator)

        self._attr_unique_id = str(entry.unique_id)
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._attr_unique_id)},
            manufacturer=MANUFACTURER,
            model=self.coordinator.client.model,
            name=entry.data[CONF_NAME],
            sw_version=self.coordinator.client.version,
        )

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        if not self.coordinator.client.is_available:
            self.async_write_ha_state()
            return

        self._attr_volume_level = self.coordinator.client.volume_level
        self._attr_is_volume_muted = self.coordinator.client.is_volume_muted
        self._attr_source_list = self.coordinator.client.source_list
        self._attr_sound_mode_list = self.coordinator.client.preset_list
        self._attr_media_artist = self.coordinator.client.media_artist
        self._attr_media_album_name = self.coordinator.client.media_album_name
        self._attr_media_artist = self.coordinator.client.media_artist
        self._attr_media_image_url = self.coordinator.client.media_image_url
        self._attr_media_duration = self.coordinator.client.media_duration
        self._attr_media_position = self.coordinator.client.current_position
        self._attr_media_position_updated_at = (
            self.coordinator.client.position_updated_at
        )
        self._attr_media_title = (
            self.coordinator.client.media_title
            if self.coordinator.client.media_title
            else self.source
        )
        self._attr_media_content_type = (
            MediaType.MUSIC
            if self.coordinator.client.streaming
            else None
        )
        self.async_write_ha_state()

    @property
    def state(self) -> MediaPlayerState | None:
        """Return the state of the device."""
        playing_state = self.coordinator.client.playing_state
        power_state = self.coordinator.client.power_state

        if not power_state :
            return MediaPlayerState.OFF
        if playing_state is None :
            return MediaPlayerState.ON
        if playing_state :
            return MediaPlayerState.PLAYING
        return MediaPlayerState.PAUSED

    @property
    def available(self) -> bool:
        """Return if the media player is available."""
        return self.coordinator.client.is_available

    @property
    def supported_features(self) -> MediaPlayerEntityFeature:
        """Flag media player features that are supported."""
        features = SUPPORT_DUTCHDUTCH

        if not self.coordinator.client.streaming :
            return features

        if not self.coordinator.client.available_options:
            return features

        for option in self.coordinator.client.available_options:
            features |= DUTCHDUTCH_TO_HA_FEATURE_MAP.get(option, 0)
        return features

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        return self.coordinator.client.source

    @property
    def sound_mode(self) -> str | None:
        """Return the current sound mode."""
        if self.coordinator.client.preset is not None:
            return self.coordinator.client.preset
        return None

    @property
    def volume_step(self) -> float | None:
        """Return the preferred volume step for the media player up/down buttons."""
        return 0.02

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1."""
        await self.coordinator.client.async_set_volume_level(volume)

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        await self.coordinator.client.async_mute_volume(mute)

    async def async_media_play(self) -> None:
        """Play media player."""
        await self.coordinator.client.async_media_play()

    async def async_media_pause(self) -> None:
        """Pause media player."""
        await self.coordinator.client.async_media_pause()

    async def async_media_stop(self) -> None:
        """Pause media player."""
        await self.coordinator.client.async_media_stop()

    async def async_media_next_track(self) -> None:
        """Send the next track command."""
        await self.coordinator.client.async_media_next_track()

    async def async_media_previous_track(self) -> None:
        """Send the previous track command."""
        await self.coordinator.client.async_media_previous_track()

    async def async_select_sound_mode(self, sound_mode: str) -> None:
        """Send sound mode command."""
        await self.coordinator.client.async_set_preset(sound_mode)

    async def async_turn_off(self) -> None:
        """Turn off media player."""
        await self.coordinator.client.async_turn_off()

    async def async_turn_on(self) -> None:
        """Turn on media player."""
        await self.coordinator.client.async_turn_on()

    async def async_select_source(self, source: str) -> None:
        """Select input source."""
        await self.coordinator.client.async_select_source(source)
