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
import time
from MyLogger import get_logger


class MusicBoxPlayer:
    """ MusicBoxPlayer

    Attributes
    ----------
    servo: MusicBoxServo
        servo motor object
    """
    _log = get_logger(__name__, False)

    def __init__(self, debug=False):
        """ Constructor

        Parameters
        ----------
        debug: bool
            debug flag
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('start')

        self._servo = MusicBoxServo(debug=self._dbg)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')

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

        self._servo.tap(ch_list)

        self._log.debug('done')


class MusicBoxPlayerWavFile:
    """ MusicBoxPlayerWavFile

    Play wav_file insted of music box.

    Attributes
    ----------
    """
    _log = get_logger(__name__, False)

    DEF_WAV_DIR = './wav'

    WAV_FILE_PREFIX = 'ch'
    WAV_FILE_SUFFIX = 'wav'

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

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')

        self._log.debug('done')

    def play(self, ch_list):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        """
        self._log.debug('ch_list=%s', ch_list)

        for ch in ch_list:
            self._sound[ch].play()

        time.sleep(0.24)  # simulate servo delay

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
    obj: MusicBoxPlayer
        description
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

        self.paper_tape_file = paper_tape_file
        self.wav_mode = wav_mode

        self.delay = self.DEF_DELAY

        self._parser = MusicBoxPaperTape(debug=self._dbg)

        if self.wav_mode:
            self._player = MusicBoxPlayerWavFile(debug=self._dbg)
        else:
            self._player = MusicBoxPlayer(debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('start')

        music_data = self._parser.parse(self.paper_tape_file)
        self._log.debug('music_data=%s', music_data)

        for data in music_data:
            ch_list = data['ch']
            delay = data['delay']
            self._log.debug("(ch_list,delay)=%s", (ch_list, delay))

            # play
            if ch_list is not None:
                self._log.info('ch_list=%s', ch_list)

                self._player.play(ch_list)

            # delay
            if delay is not None:
                self.delay = delay

            time.sleep(self.delay / 1000)

        self._log.debug('done')

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
@click.argument('paper_tape_file', type=click.Path(exists=True))
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(paper_tape_file, wav, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('paper_tape_file=%s, wav=%s', paper_tape_file, wav)

    app = SampleApp(paper_tape_file, wav, debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
