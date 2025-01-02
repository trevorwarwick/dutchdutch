"""Constants for the Dutch & Dutch integration."""
import logging

LOGGER = logging.getLogger(__package__)

VALID_STREAMERS = [ "Spotify Connect", "Roon Ready" ]

INPUT_TO_SOURCE = {
    "analogHighGain" : "XLR",
    "analogLowGain" : "XLR",
    "aes" : "XLR",
    "Spotify Connect": "Spotify Connect",
    "Roon Ready": "Roon Ready",
}

# The HA volume sliders are easy to set full scale by mistake, so for safety:
MAXGAIN = -10
