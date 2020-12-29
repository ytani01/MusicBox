#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
MIDI parser for Music Box

### for detail and simple usage
$ python3 -m pydoc MusicBoxMidi.MusicBoxMidi


### API
see comment of ``MusicBoxMidi`` class


### sample program

$ ./MusicBoxMidi.py file.mid


### Module Architecture (client side)

         --------------------------------------------------
        |                 Music Box Apps ..                |
        |==================================================|
        |              MusicBoxWebsockClient               |
        |--------------------------------------------------|
This -->| MusicBoxMidi | MusicBoxPaperTape | WebsockClient |
        |--------------|                   |---------------|
        |     mido     |                   |   websocket   |
         --------------------------------------------------

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import json
import operator
from MyLogger import get_logger


class MusicBoxMidi:
    """
    MIDI parser for Music Box

    * トラック/チャンネルを選択することができる。

    * 音程のキーを自動調節して、Music Box で
      なるべく多くの音を再生できるようにする。


    Simple Usage
    ------------
    ============================================================
    from MusicBoxMidi import MusicBoxMidi

    parser = MusicBoxMidi(midi_file)

    music_data = parser.parse()

    # [Optional] JSON format
    music_data_json = json.dumps(music_data)

    parser.end()  # end of the program
    ============================================================

    """
    DEF_NOTE_BASE = 54

    NOTE_OFFSET = [
        0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24
    ]

    NOTE_BASE_MIN = 0
    NOTE_BASE_MAX = 200

    DEF_DELAY_LIMIT = 10

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
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi_data:
            MIDI data

        Returns
        -------
        data: list of data_ent
            data_ent: ex.
            {'midi_track': 3, 'midi_channecl': 5, 'note': 65,
             'abs_time': 500, 'delay': 300}

        """
        self.__log.debug('midi_data=%s', midi_data)

        cur_tempo = 0
        abs_time = 0
        data = []

        merged_track = mido.merge_tracks(midi_data.tracks)
        for msg in merged_track:
            delay = 0
            try:
                delay = mido.tick2second(
                    msg.time, self._midi.ticks_per_beat,
                    cur_tempo) * 1000

                abs_time += delay
            except KeyError:
                pass

            self.__log.debug('msg=%s', msg)

            if msg.type == 'end_of_track':
                continue

            if msg.type == 'set_tempo':
                cur_tempo = msg.tempo
                continue

            if msg.type == 'note_on':
                if msg.velocity == 0:
                    # 'note_on and velocity == 0' is 'note_off'
                    continue

                data_ent = {
                    'midi_channel': msg.channel,
                    'note': [msg.note],
                    'abs_time': abs_time,
                }

                data.append(data_ent)

        return data

    def select_channel(self, data0, channel=[]):
        """
        指定されたトラック/チャンネルだけを抽出

        Parameters
        ----------
        data0: list of data_ent

        channel: list of int
            MIDI channel

        Returns
        -------
        data1: list of data_ent

        """
        self.__log.debug('channel=%s', channel)

        data1 = []

        for d in data0:
            if len(channel) == 0:
                data1.append(d)
                continue

            if d['midi_channel'] in channel:
                data1.append(d)

        return data1

    def note2ch(self, note, base=DEF_NOTE_BASE, full_midi=False):
        """
        Parameters
        ----------
        note: list of int
            list of note number

        Returns
        -------
        ch_list: list of int
            list of Music Box ch
        """
        # self.__log.debug('note=%s, base=%s', note, base)

        ch_list = []
        for n in note:
            if full_midi:
                ch = n - base
                if 0 <= ch < 88:
                    ch_list.append(n - base)
            else:
                for ch, offset in enumerate(self.NOTE_OFFSET):
                    if n == base + offset:
                        ch_list.append(ch)

        # self.__log.debug('ch_list=%s', ch_list)

        return ch_list

    def all_note2ch(self, midi_data, base=DEF_NOTE_BASE, full_midi=False):
        """
        Parameters
        ----------
        midi_data: list of midi_data_ent
            MIDI data
        base: int
            base note number

        Returns
        -------
        ch_list: list of int
            Music Box ch list

        """
        # self.__log.debug('base=%s', base)

        ch_list = []
        for d in midi_data:
            ch_list += self.note2ch(d['note'], base, full_midi)

        return ch_list

    def best_base(self, midi_data,
                  base_min=NOTE_BASE_MIN, base_max=NOTE_BASE_MAX,
                  full_midi=False):
        """
        Parameters
        ----------
        midi_data: list of midi_data_ent
            MIDI data
        base_min: int
            default: NOTE_BASE_MIN
        base_max: int
            default: NOtE_BASE_MAX

        Returns
        -------
        best_base: int
            selected base note number

        """
        self.__log.debug('(base_min, base_max)=%s', (base_min, base_max))
        self.__log.debug('full_midi=%s', full_midi)

        note_list = []
        for ent in midi_data:
            note_list += ent['note']
        note_set = set(note_list)

        best_base = base_min
        best_ch_set = []
        ch_len_max = 0
        for base in range(base_min, base_max+1):
            ch_set = set(self.all_note2ch(midi_data, base, full_midi))
            if len(ch_set) > ch_len_max:
                best_base = base
                ch_len_max = len(ch_set)
                best_ch_set = ch_set

            if len(ch_set) > ch_len_max * 0.6:
                self.__log.info('base=%s (%s/%s/%s), best=%s',
                                base,
                                len(ch_set), ch_len_max, len(note_set),
                                best_base)

        self.__log.info('note_set=   %s', note_set)
        self.__log.info('best_ch_set=%s', best_ch_set)

        return best_base

    def mk_music_data(self, data, base, full_midi=False):
        """
        make music_data from MIDI data

        Parameters
        ----------
        data: list of data_ent
            MIDI data

        Returns
        -------
        music_data: list of dict
            music_data for Music Box
        """
        self.__log.debug('base=%s', base)
        self.__log.debug('full_midi=%s', full_midi)

        music_data = []

        prev_abs_time = 0
        for d in data:
            ch_list = self.note2ch(d['note'], base, full_midi)

            delay = d['abs_time'] - prev_abs_time
            self.__log.debug('note=%s, ch_list=%s delay=%s',
                             d['note'], ch_list, delay)

            prev_abs_time = d['abs_time']

            data_ent = {'ch': ch_list, 'delay': delay}
            music_data.append(data_ent)

        return music_data

    def join_ch_list(self, music_data, delay_limit=DEF_DELAY_LIMIT):
        """
        join ch_list

        Parameters
        ----------
        music_data: list of dict

        delay_limit: int

        Returns
        -------
        music_data2: list of dict

        """
        music_data2 = []
        ch_list = []
        delay = 0
        for d in music_data:
            if d['delay'] <= delay_limit:
                ch_list += d['ch']
                delay += d['delay']
                continue

            data_ent = {'ch': sorted(list(set(ch_list))), 'delay': delay}
            music_data2.append(data_ent)

            ch_list = d['ch']
            delay = d['delay']

        if len(ch_list) > 0:
            data_ent = {'ch': ch_list, 'delay': delay}
            self.__log.debug('data_ent=%s', data_ent)
            music_data2.append(data_ent)

        return music_data2

    def parse(self, channel=None, base=None,
              delay_limit=DEF_DELAY_LIMIT, full_midi=False):
        """
        parse MIDI data

        base が None の場合は、最適値を自動選択する。

        Parameters
        ----------
        channel: list of int or None for all channels
            MIDI channel
        base: int or None
            note base
        delay_limit: int
            delay limit (msec)

        Returns
        -------
        music_data: list of dict

        """
        self.__log.debug('channel=%s, base=%s delay_limit=%s',
                         channel, base, delay_limit)
        self.__log.debug('full_midi=%s', full_midi)

        # 1st step of parsing
        midi_data0 = self.parse0(self._midi)

        # get channel pairs
        midi_channel = []

        for i, d in enumerate(midi_data0):
            midi_channel.append(d['midi_channel'])

        midi_channel = sorted(list(set(midi_channel)))
        self.__log.debug('midi_channel=%s', midi_channel)

        # select MIDI track/channel
        midi_data1 = self.select_channel(midi_data0, channel)
        for i, d in enumerate(midi_data1):
            self.__log.debug('%s: %s', i, d)

        if base is None:
            base  = self.best_base(midi_data1, full_midi=full_midi)
            self.__log.info('base=%s (selected automatically)', base)

        # make ``music_data``
        music_data = self.mk_music_data(midi_data1, base,
                                        full_midi=full_midi)

        # join ``ch_list`` in ``music_data``
        music_data2 = self.join_ch_list(music_data, delay_limit)        
        for i, d in enumerate(music_data2):
            self.__log.debug('%6d: %s', i, d)

        self.__log.info('midi_channel=%s', midi_channel)

        return music_data2


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, base, channel=[],
                 delay_limit=MusicBoxMidi.DEF_DELAY_LIMIT,
                 full_midi=False,
                 debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        base: int
            note base
        channel: list of int
            MIDI channel
        delay_limit: int
            delay limit
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('base=%s', base)
        self.__log.debug('channel=%s', channel)
        self.__log.debug('delay_limit=%s', delay_limit)
        self.__log.debug('full_midi=%s', full_midi)

        self._midi_file = midi_file
        self._base = base
        self._channel = channel
        self._delay_limit = delay_limit
        self._full_midi = full_midi

        self._parser = MusicBoxMidi(self._midi_file, debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        music_data = self._parser.parse(self._channel,
                                        self._base, self._delay_limit,
                                        self._full_midi)
        print('music_data = [')
        for i, d in enumerate(music_data):
            print('  %s' % (d), end='')
            if i < len(music_data) - 1:
                print(',')
            else:
                print('')

        print(']')

        print('music_data_json = %s' % json.dumps(music_data))

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
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--delay_limit', '-dl', 'delay_limit', type=int,
              default=MusicBoxMidi.DEF_DELAY_LIMIT,
              help='delay limit')
@click.option('--full_midi', '-f', 'full_midi', is_flag=True,
              default=False,
              help='Full MIDI mode')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, base, channel, delay_limit, full_midi, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('base=%s, channel=%s', base, channel)
    __log.debug('delay_limit=%s', delay_limit)
    __log.debug('full_midi=%s', full_midi)

    app = SampleApp(midi_file, base, channel, delay_limit,
                    full_midi,
                    debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
