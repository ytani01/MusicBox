#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser

### for detail and simple usage ###

$ python3 -m pydoc MusicBoxMidi.MusicBoxMidi


### sample program ###

$ ./MidiParser.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import json
from MyLogger import get_logger


class MusicBoxMidi:
    """
    Description
    -----------

    Simple Usage
    ============
    ## Import

    from MusicBoxMidi import MusicBoxMidi

    ## Initialize

    obj = MusicBoxMidi()


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
    DEF_NOTE_BASE = 54

    NOTE_LIST = [0, 2, 4, 5, 7, 9, 11,
                 12, 14, 16, 17, 19, 21, 23,
                 24]

    __log = get_logger(__name__, False)

    def __init__(self, midi_file, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)

        self._midi_file = midi_file
        self._midi = mido.MidiFile(self._midi_file)
        self.__log.debug('ticks_per_beet=%s', self._midi.ticks_per_beat)

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')

    def note2ch(self, note, note_base=DEF_NOTE_BASE):
        """
        """
        self.__log.debug('note=%s, note_base=%s', note, note_base)

        for ch, offset in enumerate(self.NOTE_LIST):
            if note == note_base + offset:
                self.__log.debug('ch=%s', ch)
                return ch

    def parse(self, note_base=DEF_NOTE_BASE, channel=0):
        """
        Description

        Parameters
        ----------
        note_base: int

        channel: int
        """
        self.__log.debug('note_base=%s, channel=%s', note_base, channel)

        tempo = None
        delay = 0
        music_data = []

        for i, track in enumerate(self._midi.tracks):
            self.__log.debug('Track %s:%s', i, track.name)


            for msg in track:
                self.__log.debug('msg=%s', msg)

                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    self.__log.debug('tempo=%s', tempo)

                if msg.time > 0:
                    delay = mido.tick2second(
                        msg.time, self._midi.ticks_per_beat,
                        tempo) * 1000

                    if delay > 2000:
                        delay = 2000
                else:
                    delay = 0

                self.__log.debug('delay=%s', delay)

                if msg.type == 'note_on' and msg.channel == channel:
                    self.__log.debug('msg.note=%s', msg.note)
                    ch = self.note2ch(msg.note, note_base)

                    data = {'ch': [ch], 'delay': delay}
                    self.__log.info('data=%s', data)

                    music_data.append(data)

        self.__log.debug('done')
        return music_data


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, base, channel, debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        base: int
            note base
        channel: int
            MIDI channel
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('base=%s, channel=%s', base, channel)

        self._midi_file = midi_file
        self._base = base
        self._channel = channel

        self._parser = MusicBoxMidi(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        data = self._parser.parse(self._base, self._channel)
        print(json.dumps(data))

        self.__log.debug('done')

    def end(self):
        """ Call at the end of program.
        """
        self.__log.debug('doing ..')
        self._parser.end()
        self.__log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MusicBoxMidi sample program
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--base', '-b', 'base', type=int,
              default=MusicBoxMidi.DEF_NOTE_BASE,
              help='note base')
@click.option('--channel', '-c', 'channel', type=int, default=0,
              help='MIDI channel')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, base, channel, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('base=%s, channel=%s', base, channel)

    app = SampleApp(midi_file, base, channel, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
