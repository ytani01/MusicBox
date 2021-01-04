#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Websocket Client

### Module Architecture (client side)

         ----------------------------------
        |        Music Box Apps ..         |
        |==================================|
This -->|          WsClient           |
        |----------------------------------|
        | Midi | PaperTape | WebsockClient |
        |------|           |---------------|
        | mido |           |   websocket   |
         ----------------------------------

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import time
import json
from websocket import create_connection
# from PaperTape import PaperTape
from . import Midi
from .my_logger import get_logger


class SimpleWebsocketClient:
    """ simple websocket client class """
    def __init__(self, url, debug=False):
        """ Constructor

        Parameters
        ----------
        url: str
            URL (ex. 'ws://localhost:8881')
        """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)

        self._url = url

    def send(self, msg):
        """
        Parameters
        ----------
        msg: str
        """
        self.__log.debug('msg=%s', msg)

        ws = create_connection(self._url)
        ws.send(msg)
        ws.close()

        self.__log.debug('done')


class WsClient:
    """ Music Box websocket client """
    __log = get_logger(__name__, False)

    def __init__(self, url, debug=False):
        """ Constructor

        Parameters
        ----------
        url: type
            description
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)

        self._url = url

        self._ws = SimpleWebsocketClient(self._url, debug=self._dbg)

    def end(self):
        """ end: Call at the end of program """
        self.__log.debug('done')

    def single_play(self, ch_list):
        """  single play

        Parameters
        ----------
        ch_list: list of int
            list of channel number
        """
        self.__log.debug('ch_list=%s', ch_list)

        json_str = json.dumps({'cmd': 'play', 'ch': ch_list})

        self._ws.send(json_str)

    def midi(self, midi_file, note_base, channel, delay_limit,
             note_n=0):
        """ parse MIDI file and send music data to server

        Parameters
        ----------
        midi_file: str
            name of MIDI file
        note_base: int
            base number of notes
        channel: list of int
            MIDI channel
        delay_limit: int
            delay limit (msec)
        note_n: int
            number of available notes
        """
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('note_base=%s, channel=%s',
                         note_base, channel)
        self.__log.debug('delay_limit=%s', delay_limit)
        self.__log.debug('note_n=%s', note_n)

        music_data = '{}'

        parser = Midi(debug=self._dbg)
        music_data = parser.parse(midi_file,
                                  channel, note_base, delay_limit,
                                  note_n)
        parser.end()

        cmd_data = {'cmd': 'music_load', 'music_data': music_data}
        json_str = json.dumps(cmd_data)
        self._ws.send(json_str)

    def paper_tape(self, file):
        """ parse paper tape file and send music data to server

        Parameters
        ----------
        file: str
            name of paper tape
        """
        self.__log.debug('file=%s', file)

        parser = PaperTape(debug=self._dbg)
        music_data = parser.parse(file)
        parser.end()

        cmd_data = {'cmd': 'music_load', 'music_data': music_data}
        json_str = json.dumps(cmd_data)
        self._ws.send(json_str)

    def music_start(self):
        """
        start music
        """
        self.__log.debug('')

        json_str = json.dumps({'cmd': 'music_start'})
        self._ws.send(json_str)

    def music_stop(self):
        """
        stop music
        """
        self.__log.debug('')

        json_str = json.dumps({'cmd': 'music_stop'})
        self._ws.send(json_str)

    def music_pause(self):
        """
        pause music
        """
        self.__log.debug('')

        json_str = json.dumps({'cmd': 'music_pause'})
        self._ws.send(json_str)

    def music_rewind(self):
        """
        rewind music
        """
        self.__log.debug('')

        json_str = json.dumps({'cmd': 'music_rewind'})
        self._ws.send(json_str)

    def change_onoff(self, ch, on=True, pw_diff=0, tap=False):
        """
        on/offパラメータ変更(差分指定)

        変更値はサーバ側で保存される

        Parameters
        ----------
        ch: int
            servo channel
        on: bool
            True: on
            False: off
        pw_diff: int
            differenc of pulse width
        tap: bool
            after change, execute tap()
        """
        self.__log.debug('ch=%s, on=%s, pw_diff=%s, tap=%s',
                         ch, on, pw_diff, tap)

        json_str = json.dumps({
            'cmd': 'change_onoff',
            'ch': ch,
            'on': on,
            'pw_diff': pw_diff,
            'tap': tap
        })
        self._ws.send(json_str)
