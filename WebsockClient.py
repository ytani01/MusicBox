#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
WebScok Client

### for detail and simple usage ###

$ python3 -m pydoc WebsockClient.WebsockClient


### sample program ###

$ ./WebsockClient.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from websocket import create_connection
from MyLogger import get_logger


class WebsockClient:
    """
    Description
    -----------

    Simple Usage
    ============
    ## Import

    from WebsockClient import WebsockClient

    ## Initialize

    obj = WebsockClient()

    ## send message

    obj.send(msg)

    ============

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, url, debug=False):
        """ Constructor

        Parameters
        ----------
        url: str
            URL
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)

        self._url = url

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
        print('end of %s' % __class__.__name__)
        self.__log.debug('done')

    def send(self, msg):
        """
        Description

        Parameters
        ----------
        msg: str
            message text
        """
        self.__log.debug('msg=%s', msg)

        ws = create_connection(self._url)
        ws.send(msg)
        ws.close()

        self.__log.debug('done')


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    obj: WebsockClient
        description
    """
    PROMPT_STR = '> '

    __log = get_logger(__name__, False)

    def __init__(self, url, msg, debug=False):
        """constructor

        Parameters
        ----------
        url: str
            URL
        msg: list of str
            message list
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s, msg=%s', url, msg)

        self._url = url
        self._msg = msg

        self._wsc = WebsockClient(url, debug=self._dbg)

    def main(self):
        """ main
        """
        self.__log.debug('')

        if len(self._msg) > 0:
            for msg in self._msg:
                self._wsc.send(msg)

            self.__log.debug('done')
            return

        # interactive mode
        while True:
            try:
                line1 = input(self.PROMPT_STR)
            except EOFError:
                self.__log.info('EOF')
                break

            self.__log.debug('line1=%s', line1)

            if len(line1) == 0:
                continue

            self._wsc.send(line1)

        self.__log.debug('done')

    def end(self):
        """
        Call at the end of program.
        """
        self.__log.debug('doing ..')
        self._wsc.end()
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
WebsockClient test program
''')
@click.argument('url', type=str)
@click.argument('msg', type=str, nargs=-1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(url, msg, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('url=%s', url)
    __log.debug('msg=%s', msg)

    app = SampleApp(url, msg, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
