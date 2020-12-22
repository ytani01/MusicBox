#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Web Server

### for detail and simple usage ###

$ python3 -m pydoc MusicBoxWebServer


### sample program ###

$ ./MusicBoxWebServer.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'
__version__ = '0.01'

import os
from pathlib import Path
import tornado.ioloop
import tornado.web
from MyLogger import get_logger


class MusicBoxWebHandler(tornado.web.RequestHandler):
    """
    """
    CH_N = 15
    CH_CENTER = 8

    __log = get_logger(__name__, False)

    def __init__(self, app, req):
        self._dbg = True
        self.__class__.__log = get_logger(__class__.__name__, self._dbg)

        super().__init__(app, req)

    def get(self):
        """
        GET method and rendering
        """
        self.__log.debug('')

        self.render("index.html",
                    title="Music Box Calibration",
                    author="FabLab Kannai",
                    version=__version__,
                    ch_list1=['%02d' % (i) for i in range(0,
                                                          self.CH_CENTER)],
                    ch_list2=['%02d' % (i) for i in range(self.CH_CENTER,
                                                          self.CH_N)])


class MusicBoxWebServer:
    """
    Simple Usage
    ============
    from MusicBoxWebServer import MusicBoxWebServer

    obj = MusicBoxWebServer()

    obj.main()  # run forever
    ============
    """
    DEF_PORT = 10080

    __log = get_logger(__name__, False)

    def __init__(self, port=DEF_PORT, debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
            port number
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s', port)

        self._port = port

        self._mydir = Path(__file__).resolve().parents[0]
        self._app = tornado.web.Application(
            [ (r"/", MusicBoxWebHandler), ],
            autoreload=True,
            debug=True,
            static_path=os.path.join(self._mydir, "static"),
            template_path=os.path.join(self._mydir, "templates")
        )

    def main(self):
        """
        Description
        """
        self.__log.debug('')

        self._app.listen(self._port)
        self.__log.debug('start server: run forever ..')
        tornado.ioloop.IOLoop.current().start()

        self.__log.debug('done')


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class
    """
    __log = get_logger(__name__, False)

    def __init__(self, port=MusicBoxWebServer.DEF_PORT, debug=False):
        """constructor

        Parameters
        ----------
        port: int
            port number
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('port=%s', port)

        self._port = port

        self._svr = MusicBoxWebServer(self._port, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        self._svr.main()

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MusicBoxWebServer sample program
''')
@click.option('--port', '-p', 'port', type=int,
              default=MusicBoxWebServer.DEF_PORT,
              help='port number: default=%s' % MusicBoxWebServer.DEF_PORT)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(port, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('port=%s', port)

    __debug = debug

    app = SampleApp(port, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
