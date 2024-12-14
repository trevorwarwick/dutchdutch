# dutchdutch
Home Assistant Custom Component for Dutch &amp; Dutch active loudspeakers

This Home Assistant integration provides a simple Media Player interface
to a pair of Dutch &amp; Dutch speakers. It supports the following features:

- Wake/Sleep
- Volume Mute/Unmute
- Volume Level
- Input Selection (XLR, Spotify, Roon)
- When streaming is active:
  - Play/Pause/Next/Prev controls
  - Artist Information
  - Artwork Display
- Preset Selection (full list of what you have configured via Ascend)

The integration is not intended to replace the use of the much more comprehensive Ascend 
application, rather just to allow automation of common use cases. 

When started, the integration will attempt to locate any speakers on the network and offer
them as an option for configuration. If this doesn't work, for example your speakers are on
a different subnet to the HA system, they can be manually configured by manually adding
the "Dutch &amp; Dutch" integration, and just entering a hostname or IPv4 address.

The integration will always use the identity of the "master" speaker to represent the pair 
within HA, and will reject the other speaker if you try to configure it as well.

The integration needs to be manually installed into the custom_components directory of your 
Home Assistant installation.
