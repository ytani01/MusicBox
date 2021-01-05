#
# (c) 2021 Yoichi Tanibayashi
#
"""
MIDI library for Music Box
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import json
import time
import midilib
from websocket import create_connection
from .my_logger import get_logger


class Midi:
    """
    MIDI parser for Music Box
    """
    NOTE_OFFSET = [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19, 21, 23, 24]

    CH_N = len(NOTE_OFFSET)

    NOTE_ORIGIN_MIN = 0
    NOTE_ORIGIN_MAX = 127 - NOTE_OFFSET[-1]

    def __init__(self, debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)

        self._midilib_parser = midilib.Parser()

    def note2ch(self, note, note_origin=NOTE_ORIGIN_MIN, note_n=-1) -> int:
        """
        calculate servo ch from MIDI note

        

        Parameters
        ----------
        note: int
            MIDI note number
        note_origin: int
            origin number of note
        note_n: int

        Returns
        -------
        ch: int
            -1: unavailable
        """
        ch = -1

        if note_n <= 0:
            offset = note - note_origin

            if offset in self.NOTE_OFFSET:
                ch = self.NOTE_OFFSET.index(offset)
        else:
            ch = note - note_origin

        return ch

    def get_ch_set(self, note_data, note_origin=NOTE_ORIGIN_MIN):
        """
        Parameters
        ----------
        note_data: list of midilib.NoteInfo
        note_origin: int

        Returns
        -------
        ch_set: set of int
        """
        ch_set = set()

        for note_info in note_data:
            ch = self.note2ch(note_info.note, note_origin)
            ch_set.add(ch)

        if -1 in ch_set:
            ch_set.remove(-1)

        return ch_set

    def best_note_origin(self, note_data) -> int:
        """
        Parameters
        ----------
        note_data: list of midilib.NoteInfo
        """
        self.__log.debug('len(note_data)=%s', len(note_data))

        best_note_origin = self.NOTE_ORIGIN_MIN
        best_ch_count = 0

        for note_origin in range(self.NOTE_ORIGIN_MIN,
                               self.NOTE_ORIGIN_MAX + 1):
            ch_set = self.get_ch_set(note_data, note_origin)

            if len(ch_set) > best_ch_count:
                best_note_origin = note_origin
                best_ch_count = len(ch_set)

            if len(ch_set) >= best_ch_count * 0.8 > 6:
                self.__log.info('%s:%s (best %s:%s)',
                                note_origin, len(ch_set),
                                best_note_origin, best_ch_count)

        return best_note_origin

    def mk_music_data(self, note_data, note_origin, note_n=-1):
        """
        Parameters
        ----------
        note_data: list of midilib.NoteInfo
        note_origin: int
        note_n: int

        Returns
        -------
        music_data: list of MusicDataEnt
        """

        music_data = []

        prev_abs_time = 0
        for note_info in note_data:
            if note_info.velocity == 0:
                continue

            abs_time = note_info.abs_time
            ch = self.note2ch(note_info.note, note_origin, note_n)

            if ch < 0:
                continue

            delay = round(abs_time - prev_abs_time, 3) * 1000
            prev_abs_time = abs_time

            ent = {'abs_time': round(abs_time, 3),
                   'ch': [ch],
                   'delay': delay}

            music_data.append(ent)

        return music_data

    def merge_ch(self, in_music_data):
        """
        Parameters
        ----------
        in_music_data: list of MusicDataEnt

        Returns
        -------
        out_music_data: list of MusicDataEnt
        """
        out_music_data = []

        abs_time = -1
        for ent in in_music_data:
            print(ent)
            if ent['abs_time'] == abs_time:
                ch_set = set(out_music_data[-1]['ch'] + ent['ch'])

                out_music_data[-1]['ch'] = sorted(list(ch_set))
                continue

            ent2 = {'abs_time': ent['abs_time'],
                    'ch': ent['ch'],
                    'delay': ent['delay']}
            out_music_data.append(ent2)
            abs_time = ent['abs_time']

        return out_music_data

    def parse(self, midi_file, channel=[], note_origin=-1, note_n=-1):
        """
        Parameters
        ----------
        midi_file: str
        channel: list of int
        note_origin: int
        note_n: int

        Returns
        -------
        music_data: list of MusicDataEnt

        """
        self.__log.debug('midi_file=%s', midi_file)

        parsed_midi = self._midilib_parser.parse(midi_file, channel)

        if note_origin < 0:
            note_origin = self.best_note_origin(parsed_midi['note_info'])
        self.__log.info('best note_bas=%s', note_origin)

        music_data = self.mk_music_data(parsed_midi['note_info'],
                                        note_origin, note_n)

        music_data2 = self.merge_ch(music_data)

        return music_data2

    def send_music(self, music_data, url):
        """
        Parameters
        ----------
        music_data: list of MusicDataEnt
        url: str
        """
        self.__log.debug('len(music_data)=%s, url=%s',
                         len(music_data), url)

        msg = {'cmd': 'music_load', 'music_data': music_data}

        msg_json = json.dumps(msg)

        ws = create_connection(url)
        ws.send(msg_json)
        ws.close()
