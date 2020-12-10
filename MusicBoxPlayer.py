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
    """
    DEF_DELAY = 500

    CMD_END = 'END_OF_DATA'

    _log = get_logger(__name__, False)

    def __init__(self, cmd_q, debug=False):
        """ Constructor

        Parameters
        ----------
        cmd_q: queue.Queue of {'ch':ch_list, 'delay':delay_msec}
            command queue

            ch_list: list of int
                channel list
            delay_msec: int
                delay [msec]
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('start')

        self._cmd_q = cmd_q

        self._def_delay = self.DEF_DELAY
        self._active = False

        super().__init__(daemon=True)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')

        while not self._cmd_q.empty():
            c = self._cmd_q.get()
            self._log.debug('%s: ignored', c)

        self._cmd_q.put(self.CMD_END)
        self._active = False

        self.join()

        self._log.debug('done')

    def is_active(self):
        return self._active

    def play(self, ch_list, delay):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            delay msec
        """
        self._log.debug('ch_list=%s, delay=%s', ch_list, delay)

        if ch_list is None and delay is not None:
            self._def_delay = delay

        if delay is None:
            delay = self._def_delay
            self._log.debug('delay=%s', delay)

        if delay is not None:
            delay_sec = delay / 1000
            self._log.debug('delay=%s ..', delay_sec)
            time.sleep(delay_sec)
        self._log.debug('done')

    def run(self):
        """ run
        """
        self._log.debug('')

        self._active = True
        while self._active:
            cmd = self._cmd_q.get()
            self._log.debug('cmd=%s', cmd)
            if cmd == self.CMD_END:
                self._active = False
                break

            self._log.debug('cmd=%s', cmd)
            self.play(cmd['ch'], cmd['delay'])

        self._log.debug('done')


class MusicBoxPlayerServo(MusicBoxPlayer):
    """ MusicBoxPlayer

    Attributes
    ----------
    servo: MusicBoxServo
        servo motor object
    """
    _log = get_logger(__name__, False)

    def __init__(self, cmd_q, debug=False):
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

        super().__init__(cmd_q, debug=self._dbg)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._servo.end()
        self._log.debug('done')

    def play(self, ch_list, delay):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            delay msec
        """
        self._log.debug('ch_list=%s', ch_list)

        if ch_list is not None:
            self._servo.tap(ch_list)

        super().play(ch_list, delay)
        self._log.debug('done')


class MusicBoxPlayerWavFile(MusicBoxPlayer):
    """ MusicBoxPlayerWavFile

    Play wav_file insted of music box.

    Attributes
    ----------
    """
    _log = get_logger(__name__, False)

    DEF_WAV_DIR = './wav'

    WAV_FILE_PREFIX = 'ch'
    WAV_FILE_SUFFIX = 'wav'

    DELAY_SERVO = 0.35


    def __init__(self, cmd_q, wav_dir=DEF_WAV_DIR, debug=False):
        """ Constructor

        Parameters
        ----------
        wav_dir: str
            directory name
        cmd_q:
            command queue
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_dir=%s', wav_dir)

        self._wav_dir = wav_dir

        pygame.mixer.init()
        self._sound = self.load_wav(self._wav_dir)

        super().__init__(cmd_q, debug=self._dbg)

    def end(self):
        """ end

        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._log.debug('done')

    def play(self, ch_list, delay):
        """ play

        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            delay msec
        """
        self._log.debug('ch_list=%s', ch_list)

        if ch_list is not None:
            for ch in ch_list:
                self._sound[ch].play()

        self._log.debug('sleep %s sec', self.DELAY_SERVO)
        time.sleep(self.DELAY_SERVO)  # simulate servo delay

        super().play(ch_list, delay)
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

        self._parser = MusicBoxPaperTape(debug=self._dbg)

        self._cmd_q_servo = queue.Queue()
        self._player_servo = MusicBoxPlayerServo(self._cmd_q_servo,
                                                 debug=self._dbg)

        self._cmd_q_wav = queue.Queue()
        self._player_wav = MusicBoxPlayerWavFile(self._cmd_q_wav,
                                                 debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('start')

        self._player_servo.start()
        self._player_wav.start()

        music_data = self._parser.parse(self._paper_tape_file)
        self._log.debug('music_data=%s', music_data)

        for data in music_data:
            ch_list = data['ch']
            delay = data['delay']
            self._log.debug("(ch_list,delay)=%s", (ch_list, delay))

            cmd = dict(ch=ch_list, delay=delay)

            if self._wav_mode:
                self._cmd_q_wav.put(cmd)
            else:
                self._cmd_q_servo.put(cmd)

            # play
            if ch_list is not None:
                self._log.info('ch_list=%s', ch_list)

        self._log.debug('data end')
        self._cmd_q_wav.put(MusicBoxPlayer.CMD_END)
        self._cmd_q_servo.put(MusicBoxPlayer.CMD_END)

        while self._player_servo.is_active() or self._player_wav.is_active():
            self._log.debug('wait sub threads ..')
            time.sleep(2)

        self._log.debug('done')

    def end(self):
        """end

        Call at the end of program.
        """
        self._log.debug('doing ..')

        self._player_wav.end()
        self._player_servo.end()

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
