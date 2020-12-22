#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Python3 template

### for detail and simple usage ###

$ python3 -m pydoc TemplateA.ClassA


### sample program ###

$ ./TemplateA.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import os
from pathlib import Path
import json
import tornado.ioloop
import tornado.web
from MusicBoxWebsockClient import MusicBoxWebsockClient
from MyLogger import get_logger


class MusicBoxHandler(tornado.web.RequestHandler):
    """
    Description
    -----------

    """
    WS_URL='ws://localhost:8881/'

    __dbg = True
    __log = get_logger('MusicBoxHandler', __dbg)

    def get(self):
        """
        GET method and base rendering routine
        """
        self.render("index.html",
                    title="Music Box Calibrator",
                    author="FabLab Kannai",
                    version="0.01",
                    ch_list1=['%02d' % (i) for i in range(0, 8)],
                    ch_list2=['%02d' % (i) for i in range(8, 15)])

    def post(self):
        """
        POST method
        """
        args1 = self.get_arguments('msg')
        args2 = self.get_arguments('cmdline')
        self.__log.debug('args1=%s, args2=%s', args1, args2)

        if len(args1) > 0:
            json_str = args1[0].replace('\'', '"')
            self.__log.debug('json_str=%s', json_str)

            msg = json.loads(json_str)
            self.__log.debug('msg=%s', msg)

            ws = MusicBoxWebsockClient(self.WS_URL, debug=self.__dbg)
            if msg['cmd'] == 'single_play':
                ws.single_play(msg['ch'])

        if len(args2) > 0:
            cmdline = args2[0]
            self.__log.debug('cmdline=%s', cmdline)

            self.exec_cmd(cmdline)

        self.get()

    def exec_cmd(self, cmdline):
        """
        execute command line trext from form
        """
        self.__log.debug('cmdline=%s', cmdline)

        args = cmdline.split()
        self.__log.debug('args=%s', args)

        cl = MusicBoxWebsockClient(self.WS_URL, debug=self.__dbg)

        if args[0] == 'single_play':
            ch_list = [int(ch) for ch in args[1:]]

            cl.single_play(ch_list)
            return

        if args[0] == 'change_onoff':
            ch = int(args[1])
            on = args[2] == 'on'
            pw_diff = int(args[3])
            tap = args[4] == 'on' or args[4] == 'tap'

            cl.change_onoff(ch, on, pw_diff, tap)
            return


class SinglePlay(MusicBoxHandler):
    """
    """
    __dbg = True
    __log = get_logger('SinglePlay', __dbg)

    def get(self):
        """
        """
        self.render("index.html",
                    title="Music Box",
                    author="FabLab Kannai",
                    version="0.01",
                    test1='world')

    def post(self):
        """
        """
        work = self.get_arguments('ch')
        self.__log.debug('work=%s', work)

        if len(work) == 0:
            self.get()
            return

        ch_list = [int(ch) for ch in work[0].split()]

        cl = MusicBoxWebsockClient(self.WS_URL, debug=True)
        cl.single_play(ch_list)

        self.get()


class MusicBoxWebServer:
    """
    Description
    -----------

    Simple Usage
    ============
    ## Import

    from TemplateA import MusicBoxWebServer

    ## Initialize

    obj = MusicBoxWebServer()


    ## method1

    obj.method1(arg)


    ## End of program

    obj.end()

    ============

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
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
            [ (r"/", MusicBoxHandler),
              (r"/single_play",SinglePlay) ],
            static_path=os.path.join(self._mydir, "static"),
            template_path=os.path.join(self._mydir, "templates")
        )

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
        print('end of %s' % __class__.__name__)
        self.__log.debug('done')

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

    Attributes
    ----------
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
        self._svr.end()
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

    app = SampleApp(port, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
