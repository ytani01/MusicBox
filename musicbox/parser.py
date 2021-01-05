#
# (c) 2021 Yoichi Tanibayashi
#
"""
PaperTape library for Music Box
"""
__author__ = 'Yoichi Tanibayashi'
__data__ = '2021/01'

import json
import time
from websocket import create_connection
from .my_logger import get_logger


class Parser:
    """
    parser for Music Box
    """
    def __init__(self, debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

    def parse(self, infile):
        """
        override in sub-class

        Parameters
        ----------
        infile: str

        Returns
        -------
        music_data: list of MusicDataEnt
        """
        self._log.debug('infile=%s', infile)

        return []  # dummy

    def send_music(self, music_data, url):
        """
        Parameters
        ----------
        music_data: list of MusicDataEnt
        url: str
        """
        self._log.debug('len(music_data)=%s, url=%s',
                         len(music_data), url)

        msg = {'cmd': 'music_load', 'music_data': music_data}

        msg_json = json.dumps(msg)

        ws = create_connection(url)
        ws.send(msg_json)
        ws.close()        
