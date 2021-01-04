#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Websocket Server

### Architecture (server side)

         --------------------------------------------
This -->|                  WsServer                  |
        |-------------------------------+------------|
        |            Player             |            |
        |-------------------------------|            |
        |           Movement            |            |
        |-------------------------------| websockets |
        |     Servo     | RotationMotor |            |
        |---------------+---------------|            |
        | ServoPCA9685  |  StepMtrTh    |            |
        |---------------+---------------|            |
        | pigpioPCA9685 |   StepMtr     |            |
         --------------------------------------------

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2021/01'

import json
import asyncio
import websockets
from . import Player
from .my_logger import get_logger


class WsServer:
    """ Music Box websocket server

    Message format (JSON)
    ---------------------
    {"cmd": "single_play", "ch": [0,2,4]}  # single play

    {"cmd": "music_load",                 # load music and play
     "music_data": [ {"ch": null,"delay": 500},
                     {"ch": [0,2,4], "delay": null},
                     {"ch": [], "delay": null}       ] }

    {"cmd": "music_start"}                 # (re)start music
    {"cmd": "music_pause"}
    {"cmd": "music_rewind"}
    {"cmd": "music_stop"}

    {"cmd": "change_onff",                 # change servo param
     "ch": 5,
     "on": true,  # on:ture, off: false
     "pw_diff": -10,
     "tap": ture }


    FYI: Simple websocket client example
    ------------------------------------
    ```python3
    from websocket import create_connection
    # [Important!] 'websocket' is not 'websockets'

    ws = create_connection('ws://localhost:8881/')
    ws.send('message')
    ws.close()
    ```

    """
    DEF_PORT = 8881

    def __init__(self,
                 wav_mode=Player.WAVMODE_NONE,
                 host="0.0.0.0", port=DEF_PORT,
                 debug=False):
        """constructor

        Parameters
        ----------
        wav_mode: int
            wav file mode
        host: str
            host
        port: int
            port number
        """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)
        self.__log.debug('wav_mode=%s', wav_mode)
        self.__log.debug('host:port=%s:%s', host, port)

        self._wav_mode = wav_mode
        self._port = port
        self._host = host

        self._player = Player(wav_mode=self._wav_mode,
                                      debug=self._dbg)

        self._start_svr = websockets.serve(self.handle, host, port)
        self._loop = asyncio.get_event_loop()

    def main(self):
        """ main
        """
        self.__log.debug('')

        self.__log.info('start server ..')
        self._loop.run_until_complete(self._start_svr)

        self.__log.info('run_forever() ..')
        self._loop.run_forever()

    def end(self):
        """ Call at the end of program
        """
        self.__log.debug('doing ..')

        self._player.end()

        self.__log.debug('done')

    async def handle(self, websock, path):
        """
        request handler

        Parameters
        ----------
        websock: dict
        path: str
        """
        self.__log.debug('websock=%s:%s, path=%s',
                         websock.local_address, websock.host, path)

        msg = await websock.recv()
        self.__log.debug('msg=%s', msg)

        try:
            data = json.loads(msg)
            self.__log.debug('data=%s', data)
        except json.decoder.JSONDecodeError as ex:
            self.__log.error('%s: %s. msg=%s', type(ex), ex, msg)
            return

        self.__log.debug('data=%s', data)

        try:
            cmd = data['cmd']
        except KeyError as ex:
            self.__log.error('%s: %s. data=%s', type(ex), ex, data)
            return

        if cmd in ('single_play', 'single', 'play', 'P'):
            try:
                ch_list = data['ch']
            except KeyError as ex:
                self.__log.error('%s: %s. data=%s', type(ex), ex, data)
                return

            self._player.single_play(ch_list)
            return

        if cmd in ('music_load', 'music', 'load', 'l'):
            try:
                music_data = data['music_data']
            except KeyError as ex:
                self.__log.error('%s: %s. data=%s', type(ex), ex, data)
                return

            self._player.music_load(music_data)
            return

        if cmd in ('music_start', 'start', 's'):
            self._player.music_start()
            return

        if cmd in ('music_pause', 'pause', 'p'):
            self._player.music_pause()
            return

        if cmd in ('music_rewind', 'rewind', 'r'):
            self._player.music_rewind()
            return

        if cmd in ('music_stop', 'stop', 'S'):
            self._player.music_stop()
            return

        if cmd in ('music_wait', 'wait', 'w'):
            self._player.music_wait()
            return

        if cmd in ('change_onoff',):
            try:
                ch = int(data['ch'])
                on = data['on']
                pw_diff = data['pw_diff']
                tap = data['tap']
            except KeyError as ex:
                self.__log.error('%s: %s. data=%s', type(ex), ex, data)

            self._player.change_onoff(ch, on, pw_diff, tap)
            return
