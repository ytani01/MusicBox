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
    parser = MusicBoxMidi()

    ## method1
    parser.parse(arg)

    ## End of program
    parser.end()

    ============

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    DEF_NOTE_BASE = 54

    DELAY_MAX = 3000

    NOTE_BASE_MIN = 0
    NOTE_BASE_MAX = 200

    NOTE_OFFSET = [
        0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24
    ]

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

    def parse0(self, midi_data):
        """
        """
        self.__log.debug('midi_data=%s', midi_data)

        tempo = None
        delay = 0
        data = []

        for i, track in enumerate(midi_data.tracks):
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    continue

                if msg.type == 'note_on':
                    delay = mido.tick2second(
                        msg.time, self._midi.ticks_per_beat,
                        tempo) * 1000
                    if delay > self.DELAY_MAX:
                        delay = self.DELAY_MAX

                    data_ent = {
                        'midi_track': i,
                        'midi_channel': msg.channel,
                        'note': msg.note,
                        'delay': delay
                    }

                    data.append(data_ent)

        return data

    def select_track_channel(self, data0, track=1, channel=0):
        """
        """
        self.__log.debug('track=%s, channel=%s', track, channel)

        data1 = []

        for d in data0:
            if track is None and channel is None:
                data1.append(d)
                continue

            if track is None and channel is not None:
                if d['midi_channel'] == channel:
                    data1.append(d)
                    continue

            if track is not None and channel is None:
                if d['midi_track'] == track:
                    data1.append(d)
                    continue

            if d['midi_track'] == track and d['midi_channel'] == channel:
                data1.append(d)

        return data1

    def note2ch(self, note, base=DEF_NOTE_BASE):
        """
        """
        # self.__log.debug('note=%s, base=%s', note, base)

        for ch, offset in enumerate(self.NOTE_OFFSET):
            if note == base + offset:
                # self.__log.debug('ch=%s', ch)
                return ch

    def all_note2ch(self, data, base=DEF_NOTE_BASE):
        """
        """
        # self.__log.debug('base=%s', base)

        ch = []
        for d in data:
            ch.append(self.note2ch(d['note'], base))

        return ch

    def best_base(self, data,
                  base_min=NOTE_BASE_MIN, base_max=NOTE_BASE_MAX):
        """
        """
        self.__log.debug('(base_min, base_max)=%s', (base_min, base_max))

        best_base = base_min
        none_count_min = 999999
        for base in range(base_min, base_max+1):
            ch = self.all_note2ch(data, base)
            none_count = ch.count(None)
            if none_count < none_count_min:
                best_base = base
                none_count_min = none_count

            if none_count_min * 0.5 < none_count < none_count_min * 1.5:
                self.__log.info('base=%s(%s), best=%s(%s)',
                                base, none_count,
                                best_base, none_count_min)

        return best_base

    def mk_music_data(self, data, base):
        """
        """
        self.__log.debug('base=%s', base)

        music_data = []
        for d in data:
            ch = self.note2ch(d['note'], base)
            data = {'ch': [ch], 'delay': d['delay']}
            self.__log.debug('data=%s', data)
            music_data.append(data)

        return music_data

    def parse(self, track=None, channel=None, base=None):
        """
        parse MIDI data

        base が None の場合は、最適値を自動選択する。

        Parameters
        ----------
        track: int
            MIDI track
        channel: int
            MIDI channel
        base: int
            note base

        """
        self.__log.debug('track=%s, channel=%s, base=%s',
                         track, channel, base)

        data0 = self.parse0(self._midi)
        midi_track = []
        midi_channel = []
        midi_track_channel = []
        for i, d in enumerate(data0):
            midi_track.append(d['midi_track'])
            midi_track = sorted(list(set(midi_track)))

            midi_channel.append(d['midi_channel'])
            midi_channel = sorted(list(set(midi_channel)))

            midi_track_channel.append('%s %s' % (
                d['midi_track'], d['midi_channel']))
            midi_track_channel = sorted(list(set(midi_track_channel)))

        self.__log.info('midi_track=%s, midi_channel=%s',
                        midi_track, midi_channel)
        self.__log.info('midi_trank_channel=%s', midi_track_channel)

        data1 = self.select_track_channel(data0, track, channel)
        for i, d in enumerate(data1):
            self.__log.debug('%s: %s', i, d)

        if base is None:
            base  = self.best_base(data1)
            self.__log.debug('base=%s (changed)', base)

        return self.mk_music_data(data1, base)


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, base, track=1, channel=0, debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        base: int
            note base
        track: int
            MIDI track
        channel: int
            MIDI channel
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('base=%s, track=%s, channel=%s',
                         base, track, channel)

        self._midi_file = midi_file
        self._base = base
        self._track = track
        self._channel = channel

        self._parser = MusicBoxMidi(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        data = self._parser.parse(self._track, self._channel, self._base)
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
@click.option('--base', '-b', 'base', type=int, default=None,
              help='note base')
@click.option('--track', '-t', 'track', type=int, default=None,
              help='MIDI track')
@click.option('--channel', '-c', 'channel', type=int, default=None,
              help='MIDI channel')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, base, track, channel, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('base=%s, track=%s, channel=%s', base, track, channel)

    app = SampleApp(midi_file, base, track, channel, debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
