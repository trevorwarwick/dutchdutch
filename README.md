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

The integration currently needs to be manually installed into the custom_components directory of your 
Home Assistant installation.  I will be attempting to get it installable via HACS in due course. In 
the meantime, you will need to have SSH access to your Home Assistant system, and manually execute 
the following commands, or some equivalent:

```
~ # cd /root/config
config # mkdir custom_components  # if not already existing
config # wget https://github.com/trevorwarwick/dutchdutch/archive/refs/heads/main.zip
config # cd custom_components
custom_components # unzip ../main.zip
custom_components # mv dutchdutch-main dutchdutch
custom_components # ls -l dutchdutch
-rwxr-xr-x    1 root     root          1070 Dec 14 12:25 __init__.py
-rwxr-xr-x    1 root     root          3769 Dec 14 12:25 config_flow.py
-rwxr-xr-x    1 root     root           141 Dec 14 12:25 const.py
-rwxr-xr-x    1 root     root          1142 Dec 14 12:25 coordinator.py
-rwxr-xr-x    1 root     root           547 Dec 14 12:25 diagnostics.py
-rwxr-xr-x    1 root     root         24240 Dec 14 12:25 dutchdutch_api.py
-rwxr-xr-x    1 root     root           880 Dec 14 12:25 dutchdutch_const.py
-rwxr-xr-x    1 root     root           365 Dec 13 15:52 manifest.json
-rwxr-xr-x    1 root     root          7209 Dec 14 12:25 media_player.py
-rwxr-xr-x    1 root     root           619 Dec 13 17:16 strings.json
drwxr-xr-x    2 root     root          4096 Dec 13 17:16 translations
```

Then restart Home Assistant and go to the Devices page within Settings to find
or add your speakers.
