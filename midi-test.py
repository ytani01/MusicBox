#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Description
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import mido
import pygame
import glob
import time
from MyLogger import get_logger


class ClassA:
    """ClassA

    Attributes
    ----------
    attr1: type(int|str|list of str ..)
        description
    """
    _log = get_logger(__name__, False)

    def __init__(self, opt, debug=False):
        """constructor

        Parameters
        ----------
        opt: type
            description
        debug: bool
            debug flag
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('opt=%s')

        self._opt = opt

    def end(self):
        """end

        Call at the end of program
        """
        self._log.debug('doing ..')
        print('end of ClassA')
        self._log.debug('done')

    def method1(self, arg):
        """method1

        Parameters
        ----------
        arg: str
            description
        """
        self._log.debug('arg=%s', arg)

        print('%s:%s' % (arg, self._opt))

        self._log.debug('done')


# --- 以下、サンプル ---


class SampleApp:
    """Sample application class

    Attributes
    ----------
    obj: ClassA
        description
    """
    _log = get_logger(__name__, False)

    def __init__(self, midi_file, debug=False):
        """constructor

        Parameters
        ----------
        midi_file: MIDI file name (path name)
            description
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('arg=%s, opt=%s')

        self.midi_file = midi_file

        self.midi = None
        self.tempo = None
        self.sound = []
        self.sound_base = 20
        self.note_base = 45

        pygame.mixer.init()

        self.load_wav()

    def main(self):
        """main
        """
        self._log.debug('start')

        self.midi = mido.MidiFile(self.midi_file)
        self._log.info('ticks_per_beat=%s', self.midi.ticks_per_beat)

        for i, track in enumerate(self.midi.tracks):
            print('Track %s|%s|' % (i, track.name))

            for msg in track:
                self._log.debug('msg=%s', msg)
                #print('type:%s' % (msg.type))

                if msg.type == 'set_tempo':
                    self.tempo = msg.tempo
                    self._log.debug('tempo=%s', self.tempo)

                if msg.time > 0:
                    delay = mido.tick2second(msg.time,
                                             self.midi.ticks_per_beat,
                                             self.tempo)
                else:
                    delay = 0

                self._log.debug('delay=%s', delay)

                if msg.type == 'note_on':
                    note_i = msg.note - self.note_base

                    self._log.debug('note_i=%s', note_i)

                   
                    """
                    while note_i < 0:
                        note_i += 15

                    while note_i > 15:
                        note_i -= 15

                    self._log.debug('note_i=%s', note_i)
                    """
                    
                    """
                    if 0 < note_i < 15:
                        self.sound[note_i + self.sound_base].play()
                    """
                    self.sound[note_i + self.sound_base].play(loops=0)

                    time.sleep(delay)

        self._log.debug('done')

    def end(self):
        """end

        Call at the end of program.
        """
        self._log.debug('doing ..')

        self._log.debug('done')

    def load_wav(self, dir="./wav"):
        """load wav files
        """
        self._log.debug('dir=%s', dir)

        wav_files = sorted(glob.glob(dir + '/*'))
        self._log.debug('wav_files=%s', wav_files)

        self.sound = [pygame.mixer.Sound(f) for f in wav_files]


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(midi_file, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('midi_file=%s', midi_file)

    app = SampleApp(midi_file, debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
