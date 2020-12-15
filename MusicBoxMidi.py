#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser

### for detail and simple usage ###

$ python3 -m pydoc MusicBoxMidi.MusicBoxMidi


### sample program ###

$ ./MusicBoxMidi.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import json
import operator
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
        abs_time = 0
        data = []

        cur_track = 0
        cur_channel = 0

        for i, track in enumerate(midi_data.tracks):
            for msg in track:
                if i != cur_track:
                    cur_track = i
                    abs_time = 0

                if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    continue

                if msg.type == 'note_on':
                    if msg.channel != cur_channel:
                        cur_channel = msg.channel
                        abs_time = 0

                    delay = mido.tick2second(
                        msg.time, self._midi.ticks_per_beat,
                        tempo) * 1000
                    if delay > self.DELAY_MAX:
                        delay = self.DELAY_MAX

                    data_ent = {
                        'midi_track': i,
                        'midi_channel': msg.channel,
                        'note': [msg.note],
                        'abs_time': abs_time,
                        'delay': delay
                    }

                    data.append(data_ent)

                    abs_time += delay

        return data

    def mix_track_channecl(self, data):
        """
        Parameters
        ----------
        data: list of dict
            parse0 result
        """
        # self.__log.debug('data=%s', data)

        if len(data) == 0:
            return []

        mixed_data = sorted(data, key=operator.itemgetter('abs_time'))

        d0 = mixed_data.pop(0)
        prev_d = d0

        for d in mixed_data:
            delay = d['abs_time'] - prev_d['abs_time']
            prev_d['delay'] = delay
            prev_d = d

        mixed_data.insert(0, d0)
        return mixed_data

    def select_track_channel(self, data0, track=[], channel=[]):
        """
        Parameters
        ----------
        data0: list of data
            result of parse0()
        track: list of int
            MIDI track
        channel: list of int
            MIDI channel
        """
        self.__log.debug('track=%s, channel=%s', track, channel)

        data1 = []

        for d in data0:
            if len(track) == 0 and len(channel) == 0:
                data1.append(d)
                continue

            if len(track) == 0 and len(channel) > 0:
                if d['midi_channel'] in channel:
                    data1.append(d)
                    continue

            if len(track) > 0 and len(channel) == 0:
                if d['midi_track'] in track:
                    data1.append(d)
                    continue

            if d['midi_track'] in track and d['midi_channel'] in channel:
                data1.append(d)

        return data1

    def note2ch(self, note, base=DEF_NOTE_BASE):
        """
        Parameters
        ----------
        note: list of int
            note number list

        Returns
        -------
        ch_list: list of int
            Music Box ch list
        """
        # self.__log.debug('note=%s, base=%s', note, base)

        ch_list = []
        for n in note:
            for ch, offset in enumerate(self.NOTE_OFFSET):
                if n == base + offset:
                    ch_list.append(ch)

        # self.__log.debug('ch_list=%s', ch_list)

        return ch_list

    def all_note2ch(self, data, base=DEF_NOTE_BASE):
        """
        Parameters
        ----------
        data: list of dict

        base: int
            base note number

        Returns
        -------
        ch_list: list of int
            Music Box ch list
        """
        # self.__log.debug('base=%s', base)

        ch_list = []
        for d in data:
            ch_list += self.note2ch(d['note'], base)

        return ch_list

    def best_base(self, data,
                  base_min=NOTE_BASE_MIN, base_max=NOTE_BASE_MAX):
        """
        """
        self.__log.debug('(base_min, base_max)=%s', (base_min, base_max))

        best_base = base_min
        ch_len_max = 0

        for base in range(base_min, base_max+1):
            ch = self.all_note2ch(data, base)
            if len(ch) > ch_len_max:
                best_base = base
                ch_len_max = len(ch)

            if len(ch) > ch_len_max * 0.6:
                self.__log.info('base=%s (%s / %.2f), best=%s (%.2f)',
                                base, len(ch), len(ch) / len(data),
                                best_base, ch_len_max / len(data) )

        return best_base

    def mk_music_data(self, data, base):
        """
        make music_data from MIDI data

        Parameters
        ----------
        data: list of dict
            MIDI data

        Returns
        -------
        music_data: list of dict
            music_data for Music Box
        """
        self.__log.debug('base=%s', base)

        music_data = []

        for d in data:
            ch_list = self.note2ch(d['note'], base)
            data_ent = {'ch': ch_list, 'delay': d['delay']}
            music_data.append(data_ent)

        return music_data

    def join_ch_list(self, music_data):
        """
        join ch_list
        
        Parameters
        ----------
        music_data: list of dict

        Returns
        -------
        music_data2: list of dict
        """
        music_data2 = []
        ch_list = []
        delay = 0
        for d in music_data:
            if d['delay'] == 0:
                ch_list += d['ch']
                delay = d['delay']
                continue

            d['ch'] += ch_list
            d['ch'] = sorted(list(set(d['ch'])))
            music_data2.append(d)

            ch_list = []
            delay = 0

        if len(ch_list) > 0:
            data_ent = {'ch': ch_list, 'delay': delay}
            self.__log.debug('data_ent=%s', data_ent)
            music_data2.append(data_ent)

        return music_data2

    def parse(self, track=None, channel=None, base=None):
        """
        parse MIDI data

        base が None の場合は、最適値を自動選択する。

        Parameters
        ----------
        track: list of int
            MIDI track
        channel: list of int
            MIDI channel
        base: int
            note base

        """
        self.__log.debug('track=%s, channel=%s, base=%s',
                         track, channel, base)

        data0 = self.parse0(self._midi)

        midi_track_channel = []

        for i, d in enumerate(data0):
            midi_track_channel.append(
                (d['midi_track'], d['midi_channel']))
            midi_track_channel = sorted(list(set(midi_track_channel)))

        self.__log.info('midi_trank_channel=%s', midi_track_channel)

        data1 = self.select_track_channel(data0, track, channel)
        for i, d in enumerate(data1):
            self.__log.debug('%s: %s', i, d)

        mixed_data = self.mix_track_channecl(data1)
        """
        for i, d in enumerate(mixed_data):
            self.__log.debug('%6d:%s', i, d)
        """

        if base is None:
            base  = self.best_base(mixed_data)
            self.__log.debug('base=%s (changed)', base)

        music_data = self.mk_music_data(mixed_data, base)
        for i, d in enumerate(music_data):
            self.__log.debug('%6d: %s', i, d)

        music_data2 = self.join_ch_list(music_data)
        for i, d in enumerate(music_data2):
            self.__log.debug('%6d: %s', i, d)

        return music_data2


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, base, track=[], channel=[],
                 debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        base: int
            note base
        track: list of int
            MIDI track
        channel: list of int
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
        for d in data:
            print('%a' % (json.dumps(d)))

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
@click.option('--track', '-t', 'track', type=int, multiple=True,
              help='MIDI track')
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
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
