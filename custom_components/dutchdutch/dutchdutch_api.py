"""Support for Dutch & Dutch speakers."""
from __future__ import annotations

import asyncio
import datetime
import json
import re
import uuid

import aiohttp

from .dutchdutch_const import LOGGER, INPUT_TO_SOURCE, MAXGAIN, VALID_STREAMERS


class DutchDutchApi:
    """Dutch & Dutch API class."""

    def __init__(self, host, session) -> None:
        """Initialize the Dutch & Dutch API."""

        self._host = host
        self._session = session

        self._serial = ""
        self._version = ""
        self._ws_session = None
        self._network_info = None
        self._roomdata = None
        self._volume = None
        self._muted = False
        self._extgain = True
        self._streaming = False
        self._sources = None
        self._preset = None
        self._source_list = {}
        self._presets = {}
        self._preset_ids = {}
        self._preset_list = []
        self._is_available = False
        self._selected_input = ""
        self._selected_xlr = ""

        self._task = None

        self._roomtarget = ""
        self._masterurl = ""
        self._mastertarget = ""
        self._slavetarget = ""
        self._ipre = re.compile(
            "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )


    async def getmasterurl(self):
        """Get the master speaker websocket URL from whichever speaker we were configured with.

        The master name is used as the unique serial number for the pair.
        """

        mycmd = self.buildcmd('master', {},
                              method = 'read')
        await self.ws_send_request(mycmd[0])
        data = await self.ws_receive(mycmd[1])

        try:
            self._serial = data['data']['name']
            self._version = data['data']['version']
            self._mastertarget = data['data']['target']
            # this item contains a variable length list of things, one of which
            # is an IPv4 address.
            masterip = None
            respcnt = len(data['data']['address']['ipv4'])
            for i in range(respcnt):
                myip = data['data']['address']['ipv4'][i]
                if bool(re.match(self._ipre, myip)) :
                    masterip = data['data']['address']['ipv4'][0]
            if masterip is None :
                return
            # sometimes see a 169 address during boot, ignore and wait for a real one
            if masterip[0:7] == "169.254" :
                return
            masterport = str(data['data']['address']['port_ascend'])
            self._masterurl = "ws://" + masterip + ":" + masterport

        except (KeyError, TypeError):
            return

    async def getroomid(self):
        """Get the Room ID from the master speaker."""

        mycmd = self.buildcmd('targets', {},
                              method = 'read',
                              targettype = 'room',
                              target = '*')
        await self.ws_send_request(mycmd[0])
        data = await self.ws_receive(mycmd[1])

        #
        # we expect an array of responses, one of which is a room, the
        # other two are the speakers. The room has always been the
        # first one in dumped traffic, but don't assume this.
        #
        respcnt = len(data['data'])
        for i in range(respcnt):
            if data['data'][i]['targetType'] == "room" :
                self._roomtarget = data['data'][i]['target']
            if data['data'][i]['targetType'] == "device" :
                if self._mastertarget != data['data'][i]['target'] :
                    self._slavetarget = data['data'][i]['target']

    def buildcmd(self, endpoint, datadict, method = 'update', targettype = None, target = None):
        """Build command to send in json format.

        Also return uuid in case caller wants to wait for a matching response.
        """

        myuuid = str(uuid.uuid4())
        jsoncommand = {}
        jsoncommand['meta'] = {}
        jsoncommand['meta']['id'] = myuuid
        jsoncommand['meta']['method'] = method
        jsoncommand['meta']['endpoint'] = endpoint
        if targettype is not None :
            jsoncommand['meta']['targetType'] = targettype
        if target is not None :
            jsoncommand['meta']['target'] = target
        jsoncommand['data'] = datadict
        return json.dumps(jsoncommand), myuuid

    async def async_check_valid(self) -> bool | None:
        """Check that the supplied host/IP returns something expected.

        Get the master Speaker ID here to allow Zeroconf flow to ignore the other speaker.
        """

        resp = await self.get_request("/clerkip.js")

        if resp is not None :
            # Presumably we have found a D&D device, so try to connect
            if not await self.ws_connect() :
                return False
            await self.getmasterurl()
            await self._ws_session.close()
            self._ws_session = None
            if self._masterurl != "" :
                return True
        return False

    async def async_ws_listener(self):
        """Wait for updates from the device."""

        try:
            LOGGER.debug("Async listener entry")
            while True :
                rxdata = await self.ws_receive(None)
                if rxdata is not None :
                    # Look for a notify response with some useful data in it
                    resptype = rxdata['meta']['method']
                    if resptype == "notify" :
                        if rxdata['meta']['type'] == "network" :
                            if "state" in rxdata['data'] :
                                self._network_info = rxdata
                                await self.async_update()
                else :
                    # the device went unreachable, so exit
                    LOGGER.debug("Async listener no response - exiting")
                    return

        except asyncio.CancelledError :
            LOGGER.debug("Async listener cancelled")

    def lost_connection(self) :
        """Tidy up if we lose the connection to the device."""
        LOGGER.debug("Lost connection")
        self._is_available = False
        if self._task is not None and not self._task.done():
            self._task.cancel()
        self._task = None
        self._ws_session = None

    async def async_update(self) -> bool | None:
        """Get the latest details from the device."""

        # first time through, check it's up and read required initial data. If anything
        # goes wrong here, it will try again on the next poll
        if not self._is_available:
            # HTTP get to check reachable, and find master
            if not await self.async_check_valid() :
                return False
            # WS connect to master speaker
            if not await self.ws_connect() :
                return False
            await self.getroomid()

            # most of the interesting data is in the network endpoint
            mycmd = self.buildcmd('network', {},
                                  method = 'read',
                                  targettype = 'room',
                                  target = self._roomtarget)
            await self.ws_send_request(mycmd[0])
            data = await self.ws_receive(mycmd[1])
            if data is not None and data['meta']['endpoint'] == 'network' :
                self._network_info = data
                # from now on, we just listen for change notifications
                loop = asyncio.get_running_loop()
                self._task = loop.create_task(self.async_ws_listener())
                mycmd = self.buildcmd('network', {},
                                  method = 'subscribe')
                await self.ws_send_request(mycmd[0])
                self._is_available = True

        # One of the above calls failed
        if not self._is_available:
            return True

        # If the expected data isn't there, it's a transient condition and
        # will be resolved by an overall connection success/failure soon
        try:
            self._roomdata = \
            self._network_info['data']['state'][self._roomtarget]['data']
        except KeyError:
            return True

        self._streaming = self._roomdata['streaming']
        self._sources = self._roomdata['inputModes']
        self._selected_input = self._roomdata['selectedInput']
        self._selected_xlr = self._roomdata['selectedXLR']

        self._extgain = False
        if self._selected_input == "XLR" :
            self._extgain = \
                self._roomdata['preferences']['gain'][self._selected_xlr]['external']
            if self._extgain :
                self._volume = 0
        else:
            self._volume = self._roomdata['gain']['global']

        # get the list of possible presets and create two mappings
        for prid in self._roomdata['presets'] :
            prn = self._roomdata['presets'][prid]['name']
            self._presets[prn] = prid
            self._preset_ids[prid] = prn

        self._preset = self._roomdata['lastSelectedPreset']

        return True

    @property
    def is_available(self) -> bool | None:
        """Return available."""
        return self._is_available

    @property
    def serial(self) -> str | None:
        """Return the serial."""
        try:
            return self._serial
        except (KeyError, TypeError):
            return None

    @property
    def device_name(self) -> str | None:
        """Return the device name."""
        try:
            # using these interchangeably
            return self._serial
        except (KeyError, TypeError):
            return None

    @property
    def model(self) -> str | None:
        """Return the device model."""
        try:
            return "8c"
        except (KeyError, TypeError):
            return None

    @property
    def version(self) -> str | None:
        """Return the device version."""
        try:
            return self._version
        except (KeyError, TypeError):
            return None

    @property
    def streaming(self) -> bool | None:
        """Return the streaming state."""
        return self._streaming

    @property
    def playing_state(self) -> bool | None:
        """Return the playing state of the device."""
        try:
            if not self._streaming :
                return None
            return self._roomdata['streamingInfo']['is_playing']
        except (KeyError, TypeError):
            return None

    @property
    def power_state(self) -> bool | None:
        """Return the power state of the device."""
        try:
            return not self._roomdata['sleep']
        except (KeyError, TypeError):
            return None

    @property
    def volume_level(self) -> float | None:
        """Volume level of the media player (0..1), converted from native -80 to 0 gain."""
        try:
            if self._volume >= 0 :
                return 1
            return (self._volume + 80) * 100/8000

        except (KeyError, TypeError):
            return None

    @property
    def is_volume_muted(self) -> bool | None:
        """Return boolean if volume is currently muted."""
        try:
            return self._roomdata['mute']['global']

        except (KeyError, TypeError):
            return None

    @property
    def source_list(self) -> list | None:
        """Return the list of supported input sources."""

        if self._sources is None or len(self._source_list) > 0:
            return sorted(self._source_list)

        for source in self._sources :
            for name, pretty_name in INPUT_TO_SOURCE.items():
                if name == source :
                    self._source_list[pretty_name] = name

        return sorted(self._source_list)

    @property
    def source(self) -> str | None:
        """Return the current input source."""
        try:
            if self._selected_input == "XLR" :
                return INPUT_TO_SOURCE[self._selected_xlr]
            return INPUT_TO_SOURCE[self._selected_input]
        except (KeyError, TypeError):
            return None

    @property
    def available_options(self) -> any | None:
        """Return the list of available options for this source."""
        if self._streaming :
            return ["play", "pause", "previous", "next"]
        return None

    @property
    def media_artist(self) -> str | None:
        """Artist of current playing media."""
        try:
            disp = self._roomdata['streamingInfo']['display']
            return disp[3].split("\n")[1]

        except (KeyError, TypeError, IndexError):
            return None

    @property
    def media_album_name(self) -> str | None:
        """Album name of current playing media."""
        try:
            disp = self._roomdata['streamingInfo']['display']
            return disp[3].split("\n")[2]

        except (KeyError, TypeError, IndexError):
            return None

    @property
    def media_title(self) -> str | None:
        """Return the current media title, or the XLR input."""
        try:
            disp = self._roomdata['streamingInfo']['display']
            return disp[3].split("\n")[0]

        except (KeyError, TypeError, IndexError):
            if self._selected_input == "XLR" :
                return self._selected_xlr
            return None

    @property
    def media_image_url(self) -> str | None:
        """Image url of current playing media."""
        try:
            if self._streaming :
                return self._roomdata['streamingInfo']['albumArt']['url']
            return None

        except (KeyError, TypeError):
            return None

    @property
    def media_duration(self) -> int | None:
        """Duration of current playing media in seconds."""
#        return self._media_duration
        return None

    @property
    def current_position(self) -> int | None:
        """Position of current playing media in seconds."""
#       return self._current_position
        return None

    @property
    def position_updated_at(self) -> datetime.datetime | None:
        """When was the position of the current playing media valid."""
#        return self._position_updated_at
        return None

    @property
    def preset_list(self) -> list | None:
        """Return the possible presets."""
        try:
            if self._presets is None or len(self._preset_list) > 0:
                return sorted(self._preset_list)

            for pre in self._presets :
                self._preset_list.append(pre)

            return sorted(self._preset_list)

        except (KeyError, TypeError):
            return None

    @property
    def preset(self) -> str | None:
        """Return the current preset."""
        try:
            return self._preset_ids[self._preset]

        except (KeyError, TypeError):
            return None

    async def async_get_diagnostics(self) -> any | None:
        """Return the diagnostic data."""
        return {
            "is_available": self._is_available,
            "masterUrl": self._masterurl,
            "sources": self._sources,
            "source list": self._source_list,
            "streaming": self._streaming,
            "volume": self._volume,
            "preset": self._preset,
            "network_info": self._network_info
        }

    async def async_set_volume_level(self, volume: float) -> None:
        """Set volume level, range 0..1. converted to -80..0 ."""
        if not self._extgain :
            gain = (80 * volume) - 80
            gain = min(gain, MAXGAIN)
            myreq = self.buildcmd('gain2', {'gain': gain},
                              targettype = 'room',
                              target = self._roomtarget)
            await self.ws_send_request(myreq[0])

    async def async_mute_volume(self, mute: bool) -> None:
        """Mute (true) or unmute (false) media player."""
        myreq = self.buildcmd('mute',
                              [{'mute': mute, 'positionID': 'global'}],
                              targettype = 'room',
                              target = self._roomtarget)
        await self.ws_send_request(myreq[0])

    async def async_media_play(self) -> None:
        """Play media player."""
        await self.ws_send_request(
            self.buildcmd('streaming-api',
                          {'method': 'Play', 'arguments': []},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_media_pause(self) -> None:
        """Pause media player."""
        await self.ws_send_request(
            self.buildcmd('streaming-api',
                          {'method': 'Pause', 'arguments': []},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_media_stop(self) -> None:
        """Pause media player."""
        await self.ws_send_request(
            self.buildcmd('streaming-api',
                          {'method': 'Pause', 'arguments': []},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_media_next_track(self) -> None:
        """Send the next track command."""
        await self.ws_send_request(
            self.buildcmd('streaming-api',
                          {'method': 'Next', 'arguments': []},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_media_previous_track(self) -> None:
        """Send the previous track command."""
        await self.ws_send_request(
            self.buildcmd('streaming-api',
                          {'method': 'Previous', 'arguments': []},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_select_source(self, source: str) -> None:
        """Select input source."""

        if source not in VALID_STREAMERS :
            name = "XLR"
        else :
            name = source
        await self.ws_send_request(
            self.buildcmd('selectedInput', {'input': name},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_set_preset(self, presetname: str) -> None:
        """Set the voicing and correction preset."""

        try:
            presetid = self._presets[presetname]
        except KeyError:
            LOGGER.error("Unknown preset %s selected", presetname)
            return

        await self.ws_send_request(
            self.buildcmd('preset2',
                          {'presetID': presetid},
                          method = 'select',
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_turn_off(self) -> None:
        """Turn off media player."""
        await self.ws_send_request(
            self.buildcmd('sleep', {'enable': True},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def async_turn_on(self) -> None:
        """Turn on media player."""
        await self.ws_send_request(
            self.buildcmd('sleep', {'enable': False},
                          targettype = 'room',
                          target = self._roomtarget)[0])

    async def ws_connect(self) -> bool :
        """Try to connect to the target with a websession."""

        LOGGER.debug("Try to connect WS")
        try:
            if self._masterurl != "" :
                connurl = self._masterurl
            else :
                connurl = 'ws://'+self._host+':8768'
            self._ws_session = await self._session.ws_connect(
                url=connurl,
                compress=0,
                heartbeat=30)
            LOGGER.debug("WS connected")
            return True

        except aiohttp.ClientError as conn_err:
            LOGGER.debug("Host %s: ws_connect Connection error %s",
                         self._host, str(conn_err))
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self._ws_session = None
            return False
        except Exception as whaterror:  # pylint: disable=bare-except
            LOGGER.debug("ws_connect unexpected exception occurred %s",
                         type(whaterror).__name__)
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self._ws_session = None
            return False


    async def get_request(self, suffix=str) -> any | None:
        """Get data using HTTP GET."""

        url = "http://" + self._host + str(suffix)
        try:
            async with self._session.get(
                url=url, allow_redirects=True, timeout=2
            ) as response:
                myresponse = await response.text()
                LOGGER.debug(
                    "Host %s: HTTP Response data: %s",
                    self._host,
                    myresponse,
                )

            return myresponse

        except aiohttp.ClientConnectorError as conn_err:
            LOGGER.debug("Host %s: Get Connection error %s",
                         self._host, str(conn_err))
            return None
        except asyncio.TimeoutError:
            LOGGER.debug(
                "GET connection timeout exception"
            )
            return None
        except (TypeError, json.JSONDecodeError):
            LOGGER.debug("JSON/Type error in GET")
            return None
        except Exception:  # pylint: disable=bare-except
            LOGGER.debug("GET unknown exception occurred")
            return None

    async def ws_send_request(self, wstring=str) -> bool | None:
        """Websocket Send method."""

        try:
            LOGGER.debug(
                    "Host %s: WS send: %s",
                    self._host,
                    wstring[0:120],
                )
            await self._ws_session.send_str (wstring, compress=None)

            return True

        except (aiohttp.ClientConnectionError,
                asyncio.TimeoutError) as conn_err:
            LOGGER.debug("Host %s: Send Connection error %s",
                         self._host, str(conn_err))
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self.lost_connection()
            return False
        except Exception as whaterror:  # pylint: disable=bare-except
            LOGGER.debug("ws_send unexpected exception occurred %s",
                         type(whaterror).__name__)
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self.lost_connection()
            return False


    async def ws_receive (self, myuuid=str) -> dict | None:
        """Websocket receive method.

        If uuid is specified,wait until that one arrives, throwing everything else away.
        """

        try:
            while True :
                myresponse = await self._ws_session.receive_str()
                if myresponse is not None :
                    LOGGER.debug(
                        "Host %s: WS response: %s",
                        self._host,
                        myresponse[0:120],
                    )
                    respjson = json.loads(myresponse)
                    if myuuid is None or respjson['meta']['id'] == myuuid :
                        break

            return respjson

        except (aiohttp.ClientConnectionError, asyncio.TimeoutError) as conn_err:
            LOGGER.debug("Host %s: ws_receive Connection error %s", self._host, str(conn_err))
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self.lost_connection()
            return None
        except Exception as whaterror:  # pylint: disable=bare-except
            LOGGER.debug("ws_receive unexpected exception occurred %s", type(whaterror).__name__)
            try:
                await self._ws_session.close()
            except: # pylint: disable=bare-except
                pass
            self.lost_connection()
            return None
