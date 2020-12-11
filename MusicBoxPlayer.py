#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music box player class
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MusicBoxPaperTape import MusicBoxPaperTape
from MusicBoxServo import MusicBoxServo
import pygame
import glob
import threading
import queue
import time
from MyLogger import get_logger


class MusicBoxPlayer(threading.Thread):
    """ MusicBoxPlayer

    Attributes
    ----------
    active: bool
        active flag
    """
    DEF_DELAY = 500

    SOUND_END = 'END_OF_MUSIC'

    _log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """ Constructor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('')

        # public
        self.active = False  # public

        # private
        self._def_delay = self.DEF_DELAY
        self._sound_q = queue.Queue()

        super().__init__(daemon=True)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')

        while not self._sound_q.empty():
            c = self._sound_q.get()
            self._log.debug('%s: ignored', c)

        self._sound_q.put(self.SOUND_END)

        self.join()

        self._log.debug('done')

    def play_and_sleep(self, ch_list=None, delay=None):
        """ play: should be override

        ch_list=[1,2,3], delay=100}:  play and sleep delay
        ch_list=[1,2,3], delay=None}: play and sleep default delay
        ch_list=[],      delay=None}: sleep default delay
        ch_list=None,    delay=100}:  change default delay, don't sleep
        ch_list=None,    delay=None}: do nothing (comment line?)

        """
        self._log.debug('ch_list=%s, delay=%s', ch_list, delay)

        if ch_list is None:
            if delay is None:
                self._log.debug('do nothing')
            else:
                self._def_delay = delay
                self._log.debug('change default delay: %s',
                                self._def_delay)

            return

        if delay is None:
            delay = self._def_delay
            self._log.debug('delay=%s (default)', delay)

        if len(ch_list) > 0:
            self._log.debug('put queue(%s)', ch_list)
            self._sound_q.put(ch_list)

        self._log.debug('sleep %s msec', delay)
        self.sleep(delay)

        self._log.debug('done')

    def play(self, ch_list=[]):
        """ play: should be override
        """
        self._log.debug('should be override')

    def sleep(self, delay):
        """ sleep

        Parameters
        ----------
        delay: int
            delay [msec]
        """
        self._log.debug('delay=%s', delay)

        time.sleep(delay / 1000)

        self._log.debug('done')

    def end_music(self):
        """ end_music
        """
        self._log.debug('')

        self._sound_q.put(self.SOUND_END)

    def run(self):
        """ run
        """
        self._log.debug('')

        self.active = True
        while self.active:
            ch_list = self._sound_q.get()
            self._log.debug('ch_list=%s', ch_list)
            if ch_list == self.SOUND_END:
                self.active = False
                break

            self.play(ch_list)

        self._log.debug('done')


class MusicBoxPlayerServo(MusicBoxPlayer):
    """ MusicBoxPlayer

    Attributes
    ----------
    ch_n: int
        number of channels
    """
    _log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """ Constructor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('start')

        self._servo = MusicBoxServo(debug=self._dbg)

        self.ch_n = self._servo.servo_n
        self._log.debug('ch_n=%s', self.ch_n)

        super().__init__(debug=self._dbg)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._servo.end()
        self._log.debug('done')

    def play(self, ch_list):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        """
        self._log.debug('ch_list=%s', ch_list)

        if ch_list is None:
            self._log.debug('do nothing')
            return

        self._log.debug('tap channels: %s', ch_list)
        try:
            self._servo.tap(ch_list)
        except ValueError as e:
            self._log.warning('%s: %s', type(e), e)

        self._log.debug('done')


class MusicBoxPlayerWavFile(MusicBoxPlayer):
    """ MusicBoxPlayerWavFile

    Play wav_file insted of music box.
    """
    _log = get_logger(__name__, False)

    DEF_WAV_DIR = './wav'

    WAV_FILE_PREFIX = 'ch'
    WAV_FILE_SUFFIX = 'wav'

    DELAY_SERVO = 350  # msec

    def __init__(self, wav_dir=DEF_WAV_DIR, debug=False):
        """ Constructor

        Parameters
        ----------
        wav_dir: str
            directory name
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_dir=%s', wav_dir)

        self._wav_dir = wav_dir

        pygame.mixer.init()
        self._sound = self.load_wav(self._wav_dir)

        self.ch_n = len(self._sound)
        self._log.debug('ch_n=%s', self.ch_n)

        super().__init__(debug=self._dbg)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._log.debug('done')

    def play(self, ch_list):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        """
        self._log.debug('ch_list=%s', ch_list)

        if ch_list is None:
            self._log.debug('do nothing')
            return

        self._log.debug('play sounds')
        for ch in ch_list:
            if ch < 0 or ch > self.ch_n - 1:
                self._log.warning('ch=%s: invalid', ch)
                continue

            self._sound[ch].play()

        """
        # simulate servo delay
        self._log.debug('sleep %s sec (simulate servo delay)',
                        self.DELAY_SERVO)
        time.sleep(self.DELAY_SERVO / 1000)
        """

        self._log.debug('done')

    def load_wav(self, wav_dir=DEF_WAV_DIR):
        """ load wav files

        Parameters
        ----------
        wav_dir: str
            directory name
        """
        self._log.debug('wav_dir=%s', wav_dir)

        glob_pattern = "%s/%s*.%s" % (
            wav_dir,
            self.WAV_FILE_PREFIX,
            self.WAV_FILE_SUFFIX)
        self._log.debug('glob_pattern=%s', glob_pattern)
        wav_files = sorted(glob.glob(glob_pattern))
        self._log.debug('wav_files=%s', wav_files)

        return [pygame.mixer.Sound(f) for f in wav_files]


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    DEF_DELAY = 500  # msec

    _log = get_logger(__name__, False)

    def __init__(self, paper_tape_file, wav_mode=False, debug=False):
        """constructor

        Parameters
        ----------
        paper_tape_file: paper tape file name (path name)
            description
        wav_mode: bool
            wav file mode
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('paper_tape_file=%s', paper_tape_file)
        self._log.debug('wav_mode=%s', wav_mode)

        self._paper_tape_file = paper_tape_file
        self._wav_mode = wav_mode

        # parser object
        self._parser = MusicBoxPaperTape(debug=self._dbg)

        # player object
        if self._wav_mode:
            self._player = MusicBoxPlayerWavFile(debug=self._dbg)
        else:
            self._player = MusicBoxPlayerServo(debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('start')

        self._player.start()

        if len(self._paper_tape_file) > 0:
            for f in self._paper_tape_file:
                self.play_file(f)
        else:
            self._log.info('Interactive mode')
            self.play_interactive()

        while self._player.active:
            self._log.debug('wait sub threads ..')
            time.sleep(2)

        self._log.debug('done')

    def play_file(self, paper_tape_file):
        """ play_file
        """
        self._log.debug('paper_tape_file=%s', paper_tape_file)

        music_data = self._parser.parse(self._paper_tape_file[0])
        self._log.debug('music data:')
        for i, d in enumerate(music_data):
            self._log.debug('%4d: %s', i, d)
        self._log.debug('end of music_data')

        for i, d in enumerate(music_data):
            self._log.info('%4d: %s', i, d)
            self._player.play_and_sleep(d['ch'], d['delay'])

        self._log.debug('end of music')
        self._player.end_music()

    def play_interactive(self):
        """ play_interactive
        """
        self._log.debug('')

        while True:
            prompt = '[0-%s, ..]> ' % (14)

            try:
                line1 = input(prompt)
            except Exception as e:
                self._log.error('%s: %s', type(e), e)
                continue

            self._log.debug('line1=%a', line1)

            if len(line1) == 0:
                break

            ch_str = line1.replace(' ', '').split(',')
            self._log.debug('ch_str=%s', ch_str)

            try:
                ch_list = [int(c) for c in ch_str]
            except Exception as e:
                self._log.error('%s: %s', type(e), e)
                continue

            self._log.debug('ch_list=%s', ch_list)

            self._player.play(ch_list)

        self._log.info('END')
        self._player.end_music()

    def end(self):
        """end

        Call at the end of program.
        """
        self._log.debug('doing ..')

        self._player.end()

        self._log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('paper_tape_file', type=click.Path(exists=True), nargs=-1)
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(paper_tape_file, wav, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('paper_tape_file=%s', paper_tape_file)
    _log.debug('wav=%s', wav)

    app = SampleApp(paper_tape_file, wav, debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
