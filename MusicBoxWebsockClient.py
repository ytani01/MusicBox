#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Websock Client

### for detail and simple usage ###

$ python3 -m pydoc MusicBoxWebsockClient.MusicBoxWebsockClient


### sample program ###

$ ./MusicBoxWebsockClient.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import json
from WebsockClient import WebsockClient
from MyLogger import get_logger


class MusicBoxWebsockClient:
    """
    Description
    -----------

    Simple Usage
    ============
    ## Import

    from MusicBoxWebsockClient import MusicBoxWebsockClient


    ## Initialize

    cl = MusicBoxWebsockClient('ws://ipaddr:port/')


    ## send commands

    cl.single_play([0,1, ..])

    cl.music_load(music_data)

    cl.music_start()

    cl.music_pause()

    cl.music_rewind()

    cl.music_stop()


    ## End of program

    cl.end()

    ============

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    __log = get_logger(__name__, False)

    def __init__(self, url, debug=False):
        """ Constructor

        Parameters
        ----------
        url: type
            description
        debug: bool
            debug flag
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)

        self._url = url

        self._ws = WebsockClient(self._url, debug=self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
        print('end of %s' % __class__.__name__)
        self.__log.debug('done')

    def single_play(self, ch_list):
        """  single play

        Parameters
        ----------
        ch_list: list of int
            channel number list
        """
        self.__log.debug('ch_list=%s', ch_list)

        json_str = json.dumps({'cmd': 'play', 'ch':ch_list})

        self._ws.send(json_str)

    def paper_tape(self, file):
        """ parse and send paper tape file
        
        Parameters
        ----------
        file: str
            file name of paper tape
        """
        self.__log.debug('file=%s', file)

        with open(file) as f:
            


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, url, cmd, args, debug=False):
        """constructor

        Parameters
        ----------
        url: str
            URL
        cmd: str
            command
        args: list of str
            arguments
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)
        self.__log.debug('cmd=%s', cmd)
        self.__log.debug('args=%s', args)

        self._url = url
        self._cmd = cmd
        self._args = args

        self._cl = MusicBoxWebsockClient(url, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        if self._cmd in ('sigle_play', 'play', 'p'):
            ch_list = [int(num) for num in self._args]

            self._cl.single_play(ch_list)

        else:
            self._cl.send_cmd(self._cmd, arg_data)

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self._cl.end()
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MusicBoxWebsockClient sample program
''')
@click.argument('url', type=str)
@click.argument('cmd', type=str)
@click.argument('args', type=str, nargs=-1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(url, cmd, args, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('url=%s, cmd=%s, args=%s', url, cmd, args)

    app = SampleApp(url, cmd, args, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
