#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Websock Server


"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MusicBoxMovement import MusicBoxMovement, MusicBoxMovementWavFile
import asyncio
import websockets
import json
from MyLogger import get_logger


class MusicBoxWebsockServer:
    """ MusicBoxWebsockServer

    Attributes
    ----------
    """
    DEF_PORT = 8881

    __log = get_logger(__name__, False)

    def __init__(self, wav_mode=False, host="0.0.0.0", port=DEF_PORT,
                 debug=False):
        """constructor

        Parameters
        ----------
        port: int
            port number
        wav_mode: bool
            wav file mode flag
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('wav_mode=%s', wav_mode)
        self.__log.debug('host:port=%s:%s', host, port)

        self._wav_mode = wav_mode
        self._port = port
        self._host = host

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
        """end

        Call at the end of program
        """
        self.__log.debug('doing ..')
        print('end of %s' % __class__.__name__)
        self.__log.debug('done')

    async def handle(self, websock, path):
        """ handle

        Parameters
        ----------
        """
        self.__log.debug('websock=%s:%s, path=%s',
                         websock.local_address,
                         websock.host,
                         path)

        msg = await websock.recv()
        self.__log.debug('msg=%s', msg)

        data = json.loads(msg)
        self.__log.debug('data=%s', data)

        if type(data[0]) == dict:
            for d in data:
                if d['ch'] == '':
                    d['ch'] = None

                self.__log.info('ch=%s, delay=%s', d['ch'], d['delay'])

        elif type(data[0]) == list:
            for d in data:
                self.__log.info('d=%s', d)

        else:
            self.__log.info('data=%s', data)

        # await websock.send(msg)

        self.__log.debug('done')


# --- 以下、サンプル ---


class SampleApp:
    """Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, port=MusicBoxWebsockServer.DEF_PORT,
                 wav_mode=False, debug=False):
        """constructor

        Parameters
        ----------
        port: int
            port number
        wav_mode: bool
            wav mode flag
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s, wav_mode=%s', port, wav_mode)

        self._port = port
        self._wav_mode = wav_mode

        self._ws_svr = MusicBoxWebsockServer(wav_mode=self._wav_mode,
                                             port=self._port,
                                             debug=self._dbg)

    def main(self):
        """main
        """
        self.__log.debug('')

        self._ws_svr.main()

        self.__log.debug('done')

    def end(self):
        """end

        Call at the end of program.
        """
        self.__log.debug('doing ..')
        
        self._ws_svr.end()

        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.option('--port', '-p', 'port', type=int,
              default=MusicBoxWebsockServer.DEF_PORT,
              help='port number')
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(port, wav, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('port=%s, wav=%s', port, wav)

    app = SampleApp(port, wav, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
