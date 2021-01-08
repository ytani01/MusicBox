#
# (c) 2021 Yoichi Tanibayashi
#
"""
Music Box websocket client
"""
import json
from websocket import create_connection
from . import WsServer
from .my_logger import get_logger


class WsClient:
    """
    websocket client for Music Box (URL)
    """
    DEF_HOST = 'localhost'
    DEF_PORT = WsServer.DEF_PORT

    DEF_URL = 'ws://%s:%d/' % (DEF_HOST, DEF_PORT)

    def __init__(self, url=DEF_URL, debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        self._url = url

    def ws_url(self, host_or_ip, port):
        """
        Parameters
        ----------
        host_or_ip: str
        port: int
        """
        url = 'ws://%s:%d/' % (host_or_ip, port)
        return url

    def send(self, msg):
        """
        Parameters
        ----------
        msg: object
        """
        self._log.debug('msg.keys()=%s', list(msg.keys()))
        self._log.debug('msg[\'cmd\']=%s', msg['cmd'])
        
        msg_json = json.dumps(msg)

        ws = create_connection(self._url)
        ws.send(msg_json)
        ws.close()

    def send_music(self, music_data):
        """
        Parameters
        ----------
        music_data: list of MusicDataEnt
        """
        msg = {'cmd': 'music_load', 'music_data': music_data}

        self.send(msg)

    def send_music_file(self, music_data_file):
        """
        Parameters
        ----------
        music_data_file: str
        """
        music_data = []
        with open(music_data_file) as f:
            music_data = json.load(f)

        self.send_music(music_data)


class WsClientHostPort(WsClient):
    """
    websocket client for Music Box (host, port)
    """
    DEF_HOST = 'localhost'
    DEF_PORT = WsServer.DEF_PORT

    def __init__(self, host=DEF_HOST, port=DEF_PORT, debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        super().__init__(self.ws_url(host, port), debug=self._dbg)
