#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Websock Client

### for detail and simple usage ###

$ python3 -m pydoc MusicBoxWebsockClient.MusicBoxWebsockClient


### usage of sample program ###

$ ./MusicBoxWebsockClient.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import json
import copy
from WebsockClient import WebsockClient
from MusicBoxPaperTape import MusicBoxPaperTape
from MusicBoxMidi import MusicBoxMidi
from MyLogger import get_logger


class MusicBoxWebsockClient:
    """
    Description
    -----------
    Music Box Websock Client

    Simple Usage
    ------------
    from MusicBoxWebsockClient import MusicBoxWebsockClient

    cl = MusicBoxWebsockClient('ws://ipaddr:port/')

    cl.single_play([0,1, ..])
    cl.midi(filename)           # TBD
    cl.paper_tape(filename)
    cl.music_start()
    cl.music_pause()
    cl.music_rewind()
    cl.music_stop()

    cl.end()     # Call at the end of program
    ============
    """
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

        self._ws = WebsockClient(self._url, debug=self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
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

    def midi(self, file, note_base, track, channel):
        """ parse MIDI file and send music data to server

        Parameters
        ----------
        file: str
            name of MIDI file
        note_base: int

        track: int

        channel: int
        """
        self.__log.debug('file=%s', file)
        self.__log.debug('note_base=%s, track=%s, channel=%s',
                         note_base, track, channel)

        music_data = '{}'

        parser = MusicBoxMidi(file, debug=self._dbg)
        music_data = parser.parse(track, channel, note_base)
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

        parser = MusicBoxPaperTape(debug=self._dbg)
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


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    PROMPT_STR = '> '

    ALIASES = [
        ['single_play', 'single', 'play', 'P'],
        ['music_start', 'start', 's'],
        ['music_stop', 'stop', 'S'],
        ['music_pause', 'pause', 'p'],
        ['music_rewind', 'rewind', 'r'],
        ['midi', 'm', 'M'],
        ['paper_tape', 'tape', 'paper', 'pt', 't', 'T'],
        ['help', 'h', 'H', '?']
    ]

    __log = get_logger(__name__, False)

    def __init__(self, url, cmd, note_base=None, track=None, channel=None,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        url: str
            URL
        cmd: list of str
            command line
        note_base: int
            note number
        track: int
            track number
        channel: int
            channel number
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('url=%s', url)
        self.__log.debug('cmd=%s', cmd)
        self.__log.debug('note_base=%s, track=%s, channel=%s',
                         note_base, track, channel)

        self._url = url
        self._cmd = cmd
        self._note_base = note_base
        self._track = track
        self._channel = channel

        self._cl = MusicBoxWebsockClient(url, debug=self._dbg)

    def aliases2cmd(self, cmd_str):
        """ search command aliseses
        """
        self.__log.debug('cmd_str=%s', cmd_str)

        for i, alias in enumerate(self.ALIASES):
            self.__log.debug('%s:%s.', i, alias)

            if cmd_str in alias:
                return alias[0]

        return None

    def cmd_func(self, args):
        """
        Parameters
        ----------
        args: list of str
            command line
        """
        self.__log.debug('args=%s', args)

        if len(args) == 0:
            return

        args = list(args)
        arg0 = args.pop(0)

        try:
            int(arg0)
            args.insert(0, arg0)
            arg0 = 'single_play'
        except ValueError:
            pass

        cmd = self.aliases2cmd(arg0)
        if cmd is None:
            self.__log.error('%s: no such command', cmd)
            return

        if cmd == 'help':
            for a in self.ALIASES:
                print('%s' % a)

            return

        if cmd == 'single_play':
            ch_list = [int(num) for num in args]

            self._cl.single_play(ch_list)
            return

        if cmd == 'midi':
            file = args[0]

            self._cl.midi(file, self._note_base,
                          self._track, self._channel)
            return

        if cmd == 'paper_tape':
            file = args[0]

            self._cl.paper_tape(file)
            return

        if cmd == 'music_start':
            self._cl.music_start()
            return

        if cmd == 'music_stop':
            self._cl.music_stop()
            return

        if cmd == 'music_pause':
            self._cl.music_pause()
            return

        if cmd == 'music_rewind':
            self._cl.music_rewind()
            return

        self.__log.error('%s %s: invalid command line', cmd, args)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        if len(self._cmd) == 0:
            self.interactive()
            return

        self.cmd_func(self._cmd)

    def interactive(self):
        """ interactive mode
        """
        self.__log.debug('')

        while True:
            try:
                line1 = input(self.PROMPT_STR)
            except EOFError:
                self.__log.info('EOF')
                break

            self.__log.debug('line1=%s', line1)

            args = line1.split()
            self.__log.debug('args=%s', args)

            self.cmd_func(args)

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
@click.argument('cmd', type=str, nargs=-1)
@click.option('--note_base', '-b', 'note_base', type=int, default=None,
              help='MIDI note base')
@click.option('--track', '-t', 'track', type=int, default=None,
              help='MIDI track')
@click.option('--channel', '-c', 'channel', type=int, default=None,
              help='MIDI channel')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(url, cmd, note_base, track, channel, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('url=%s, cmd=%s', url, cmd)
    __log.debug('note_base=%s, track=%s, channel=%s',
                note_base, track, channel)

    app = SampleApp(url, cmd, note_base, track, channel, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
