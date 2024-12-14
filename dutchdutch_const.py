"""Constants for the Dutch & Dutch integration."""
import logging
from enum import Enum

LOGGER = logging.getLogger(__package__)

#
# AES Streamer and File Player are returned by the speakers as possible inputs
# but they don't appear in the D&D app, so leaving them out for now
#
#NORMAL_INPUTS = {
#    "Analog High Gain": "analogHighGain",
#    "Analog Low Gain": "analogLowGain",
#    "AES3" : "aes",
#    "Spotify Connect": "Spotify Connect",
#    "Roon Ready": "Roon Ready",
##    "AES Streamer": "AES Streamer",
##    "File Player": "File Player"
#}

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
