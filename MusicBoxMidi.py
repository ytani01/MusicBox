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

    def __init__(self, debug=False):
        """ Constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self.__log.debug('doing ..')
        self.__log.debug('done')

    def parse0(self, midi):
        """
        parse MIDI format simply for subsequent parsing step

        Parameters
        ----------
        midi:
            MIDI data from mido.MidiFile(..)

        Returns
        -------
        data: list of data_ent
            data_ent: ex.
            {'midi_track': 3, 'midi_channecl': 5, 'note': 65,
             'abs_time': 500, 'delay': 300}

        """
        self.__log.debug('midi=%s', midi)

        cur_tempo = 0
        abs_time = 0
        data = []

        merged_track = mido.merge_tracks(midi.tracks)
        for msg in merged_track:
            delay = 0
            try:
                delay = mido.tick2second(
                    msg.time, midi.ticks_per_beat,
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

    def select_channel(self, data0, channel=None):
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
            if channel is None or len(channel) == 0:
                data1.append(d)
                continue

            if d['midi_channel'] in channel:
                data1.append(d)

        return data1

    def note2ch(self, note, note_base=DEF_NOTE_BASE, note_n=0):
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
        # self.__log.debug('note=%s, note_base=%s', note, note_base)

        ch_list = []
        for n in note:
            if note_n > 0:
                ch = n - note_base
                if 0 <= ch < note_n:
                    ch_list.append(n - note_base)
            else:
                for ch, offset in enumerate(self.NOTE_OFFSET):
                    if n == note_base + offset:
                        ch_list.append(ch)

        # self.__log.debug('ch_list=%s', ch_list)

        return ch_list

    def all_note2ch(self, midi_data, note_base=DEF_NOTE_BASE,
                    note_n=0):
        """
        Parameters
        ----------
        midi_data: list of midi_data_ent
            MIDI data
        note_base: int
            note base number
        note_n: int
            number of available notes

        Returns
        -------
        ch_list: list of int
            Music Box ch list

        """
        # self.__log.debug('note_base=%s', note_base)

        ch_list = []
        for d in midi_data:
            ch_list += self.note2ch(d['note'], note_base, note_n)

        return ch_list

    def best_note_base(self, midi_data,
                       note_base_min=NOTE_BASE_MIN,
                       note_base_max=NOTE_BASE_MAX,
                       note_n=0):
        """
        Parameters
        ----------
        midi_data: list of midi_data_ent
            MIDI data
        note_base_min: int
            default: NOTE_BASE_MIN
        note_base_max: int
            default: NOtE_BASE_MAX
        note_n: int
            number of available notes

        Returns
        -------
        best_note_base: int
            selected note base
        """
        self.__log.debug('(note_base_min, note_base_max)=%s',
                         (note_base_min, note_base_max))
        self.__log.debug('note_n=%s', note_n)

        note_list = []
        for ent in midi_data:
            note_list += ent['note']
        note_set = set(note_list)

        best_note_base = note_base_min
        best_ch_set = []
        ch_len_max = 0
        for note_base in range(note_base_min, note_base_max+1):
            ch_set = set(self.all_note2ch(midi_data, note_base,
                                          note_n))
            if len(ch_set) > ch_len_max:
                best_note_base = note_base
                ch_len_max = len(ch_set)
                best_ch_set = ch_set

            if len(ch_set) > ch_len_max * 0.8:
                self.__log.info('note_base=%s (%s/%s/%s), best=%s',
                                note_base,
                                len(ch_set), ch_len_max, len(note_set),
                                best_note_base)

        self.__log.info('note_set=   %s', sorted(list(note_set)))
        self.__log.info('best_ch_set=%s', sorted(list(best_ch_set)))

        return best_note_base

    def mk_music_data(self, data, note_base, note_n=0):
        """
        make music_data from MIDI data

        Parameters
        ----------
        data: list of data_ent
            MIDI data
        note_base: int
        note_n: int

        Returns
        -------
        music_data: list of dict
            music_data for Music Box
        """
        self.__log.debug('note_base=%s, note_n=%s', note_base, note_n)

        music_data = []

        prev_abs_time = 0
        for d in data:
            ch_list = self.note2ch(d['note'], note_base, note_n)

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
            if len(data_ent['ch']) != 0 and data_ent['delay'] != 0:
                music_data2.append(data_ent)

            ch_list = d['ch']
            delay = d['delay']

        if len(ch_list) > 0:
            data_ent = {'ch': ch_list, 'delay': delay}
            self.__log.debug('data_ent=%s', data_ent)
            music_data2.append(data_ent)

        return music_data2

    def parse(self, midi_file, channel=None, note_base=None,
              delay_limit=DEF_DELAY_LIMIT, note_n=0):
        """
        parse MIDI data

        note_base が None の場合は、最適値を自動選択する。

        Parameters
        ----------
        midi_file: str
            MIDI file name
        channel: list of int or None for all channels
            MIDI channel
        note_base: int or None
            note base
        delay_limit: int
            delay limit (msec)
        note_n: int

        Returns
        -------
        music_data: list of dict

        """
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('channel=%s, note_base=%s delay_limit=%s',
                         channel, note_base, delay_limit)
        self.__log.debug('note_n=%s', note_n)

        # load midi_file
        midi = mido.MidiFile(midi_file)
        self.__log.debug('ticks_per_beet=%s', midi.ticks_per_beat)

        # 1st step of parsing
        midi_data0 = self.parse0(midi)

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

        if note_base is None:
            note_base  = self.best_note_base(midi_data1, note_n=note_n)
            self.__log.info('note_base=%s (selected automatically)',
                            note_base)

        # make ``music_data``
        music_data = self.mk_music_data(midi_data1, note_base,
                                        note_n=note_n)

        # join ``ch_list`` in ``music_data``
        music_data2 = self.join_ch_list(music_data, delay_limit)

        if music_data2[0]['delay'] > 2000:
            music_data2[0]['delay'] = 2000

        for i, d in enumerate(music_data2):
            self.__log.debug('%6d: %s', i, d)

        self.__log.info('midi_channel=%s', midi_channel)
        self.__log.info('selectied channel=%s', channel)

        return music_data2


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    __log = get_logger(__name__, False)

    def __init__(self, midi_file, note_base, channel=[],
                 delay_limit=MusicBoxMidi.DEF_DELAY_LIMIT,
                 note_n=0,
                 debug=False):
        """constructor

        Parameters
        ----------
        midi_file: str
            file name of MIDI file
        note_base: int
            note base
        channel: list of int
            MIDI channel
        delay_limit: int
            delay limit
        note_n: int
            number of available notes
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s', midi_file)
        self.__log.debug('note_base=%s', note_base)
        self.__log.debug('channel=%s', channel)
        self.__log.debug('delay_limit=%s', delay_limit)
        self.__log.debug('note_n=%s', note_n)

        self._midi_file = midi_file
        self._note_base = note_base
        self._channel = channel
        self._delay_limit = delay_limit
        self._note_n = note_n

        self._parser = MusicBoxMidi(debug=self._dbg)

    def main(self):
        """ main routine
        """
        self.__log.debug('')

        music_data = self._parser.parse(self._midi_file,
                                        self._channel,
                                        self._note_base,
                                        self._delay_limit,
                                        self._note_n)
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
@click.option('--note_base', '-b', 'note_base', type=int, default=None,
              help='note base')
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--delay_limit', '-dl', 'delay_limit', type=int,
              default=MusicBoxMidi.DEF_DELAY_LIMIT,
              help='delay limit')
@click.option('--note_n', '-n', 'note_n', type=int, default=0,
              help='number of available notes')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, note_base, channel, delay_limit, note_n, debug):
    """サンプル起動用メイン関数
    """
    __log = get_logger(__name__, debug)
    __log.debug('midi_file=%s', midi_file)
    __log.debug('note_base=%s, channel=%s', note_base, channel)
    __log.debug('delay_limit=%s', delay_limit)
    __log.debug('note_n=%s', note_n)

    app = SampleApp(midi_file, note_base, channel, delay_limit, note_n,
                    debug=debug)
    try:
        app.main()
    finally:
        __log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
