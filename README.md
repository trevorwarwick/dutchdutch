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

The integration needs to be installed into the custom_components directory of your Home Assistant installation. 
You can do this via the Home Assistant Community Store (HACS). See: https://www.hacs.xyz/docs/use/download/download/ . 
An advantage of using HACS over manual installation is that HACS will automatically tell you whenever an update for the integration is available.

Once you have HACS installed, follow the instructions for adding a Custom Repository here: https://www.hacs.xyz/docs/faq/custom_repositories/ . 
Specify "trevorwarwick/dutchdutch" as the Repo and "Integration" as the type. This will add the integration to the allowed list of downloads within HACS. 
Then search within HACS for "dutchdutch", and select Download from the three-dot menu. It will tell you which version it's downloading. 
Then restart Home Assistant, and the integration will find your speakers if or when they are powered up.

Alternatively, to install manually without HACS, you will need to have SSH access to your Home Assistant system. 
Use wget or curl to download the latest release from https://github.com/trevorwarwick/dutchdutch/releases, and unpack the tar or zip file. 
The actual files you need for the integration are in the custom_components/dutchdutch directory in the archive, and this is also where 
they need to end up on your system when you've unpacked the release.

For example:
```
~ # cd /root/config
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

Example screenshots of HA Media Player card:

With AES input selected:\
<img width="395" height="151" alt="mediasmall" src="https://github.com/user-attachments/assets/7204dacc-420b-4720-85ba-236fbe0151bb" />

Playing from Spotify directly:\
<img width="394" height="175" alt="mediaspotty" src="https://github.com/user-attachments/assets/87c9911f-7c30-4734-b404-f4c8ff308a5f" />

Sound mode selection:\
<img width="584" height="729" alt="medialarge" src="https://github.com/user-attachments/assets/8207c258-b591-4a1b-9a08-703bf8cf2619" />

Credit: The basic structure of this integration was inspired by the devialet integration
by @fwestenberg
