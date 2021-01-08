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
__date__ = '2021/01'

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
     "music_data": [ {"ch": null,"delay": 500},.. ]


    {"cmd": "music_start"}                 # (re)start music
    {"cmd": "music_pause"}
    {"cmd": "music_rewind"}
    {"cmd": "music_stop"}

    {"cmd": "calibrate",                # change servo param
     "ch": 5,
     "on": true,  # on:ture, off: false
     "pw_diff": -10,
     "tap": ture }


    Simple client example(1)
    ---------------------------------------
    ```python3
    from musicbox import WsClientHostPort

    msg = {'cmd': ...}

    client = WsClientHostPort('localhost', 8880)
    client.send(msg)
    ```

    [FYI]
    Simple websocket client example(2)
    ----------------------------------
    ```python3
    # [Important!] 'websocket' is not 'websockets'

    import json
    from websocket import create_connection

    msg = {'cmd': ...}
    msg_json = json.dumps(msg)

    ws = create_connection('ws://localhost:8880/')
    ws.send(msg_json)
    ws.close()
    ```

    """
    DEF_PORT = 8880

    def __init__(self,
                 wav_mode=Player.WAVMODE_NONE,
                 host="0.0.0.0", port=DEF_PORT,
                 wavdir='wav',
                 debug=False):
        """ Constructor

        Parameters
        ----------
        wav_mode: int
            wav file mode
        host: str
            host
        port: int
            port number
        wavdir: str
            wav file directory
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.info('host:port=%s:%s', host, port)
        self._log.debug('wavdir=%s', wavdir)

        self._wav_mode = wav_mode
        self._port = port
        self._host = host
        self._wavdir = wavdir

        self._player = Player(wav_mode=self._wav_mode,
                              wavdir=self._wavdir, debug=self._dbg)

        self._start_svr = websockets.serve(self.handle, host, port)
        self._loop = asyncio.get_event_loop()

    def main(self):
        """ main
        """
        self._log.debug('')

        self._log.debug('start server ..')
        self._loop.run_until_complete(self._start_svr)

        self._log.info('run_forever() ..')
        self._loop.run_forever()

    def end(self):
        """ Call at the end of program
        """
        self._log.debug('doing ..')

        self._player.end()

        self._log.debug('done')

    async def handle(self, websock, path):
        """
        request handler

        Parameters
        ----------
        websock: dict
        path: str
        """
        self._log.debug('websock=%s:%s, path=%s',
                        websock.local_address, websock.host, path)

        msg = await websock.recv()
        self._log.info('msg=%s', msg)

        try:
            data = json.loads(msg)
            self._log.debug('data=%s', data)
        except json.decoder.JSONDecodeError as ex:
            self._log.error('%s: %s. msg=%s', type(ex), ex, msg)
            return

        self._log.debug('received command: %a', data['cmd'])
        self._log.debug('data=%s', data)

        try:
            cmd = data['cmd']
        except KeyError as ex:
            self._log.error('%s: %s. data=%s', type(ex), ex, data)
            return

        if cmd in ('single_play', 'single', 'play', 'P'):
            try:
                ch_list = data['ch']
            except KeyError as ex:
                self._log.error('%s: %s. data=%s', type(ex), ex, data)
                return

            self._player.single_play(ch_list)
            return

        if cmd in ('music_load', 'music', 'load', 'l'):
            try:
                music_data = data['music_data']
            except KeyError as ex:
                self._log.error('%s: %s. data=%s', type(ex), ex, data)
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

        if cmd in ('calibrate',):
            try:
                ch = int(data['ch'])
                on = data['on']
                pw_diff = data['pw_diff']
                tap = data['tap']
            except KeyError as ex:
                self._log.error('%s: %s. data=%s', type(ex), ex, data)

            self._player.calibrate(ch, on, pw_diff, tap)
            return
