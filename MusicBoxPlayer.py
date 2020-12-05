#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Description
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MusicBoxPaperTape import MusicBoxPaperTape
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
    DEF_DELAY = 500  # msec

    _log = get_logger(__name__, False)

    def __init__(self, paper_tape_file, debug=False):
        """constructor

        Parameters
        ----------
        paper_tape_file: paper tape file name (path name)
            description
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('arg=%s, opt=%s')

        self.paper_tape_file = paper_tape_file

        self.delay = self.DEF_DELAY

        self.sound = []
        self.sound_base = 40

        pygame.mixer.init()

        self.load_wav()

        self.parser = MusicBoxPaperTape(debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('start')

        music_data = self.parser.parse(self.paper_tape_file)
        self._log.debug('music_data=%s', music_data)

        for data in music_data:
            ch_list = data['ch']
            delay = data['delay']
            self._log.debug("(ch_list,delay)=%s", (ch_list, delay))
            
            # play
            if ch_list is not None:
                for ch in ch_list:
                    self.sound[ch + self.sound_base].play()

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
@click.argument('paper_tape_file', type=click.Path(exists=True))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(paper_tape_file, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('paper_tape_file=%s', paper_tape_file)

    app = SampleApp(paper_tape_file, debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
