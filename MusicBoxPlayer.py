#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Player class

##### Simple usage and detail

$ python3 -m pydoc MusicBoxPlayer.MusicBoxPlayer


##### sample program (interactive demo) usage

$ ./MusicBoxPlayer.py -h

"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import threading
import copy
import time

from MusicBoxMovement import MusicBoxMovement, MusicBoxMovementWavFile
from MusicBoxPaperTape import MusicBoxPaperTape

from MyLogger import get_logger


class MusicBoxPlayer:
    """ Music Box Player class

    Simple Usage
    ============
    ## Import

    from MusicBoxPlayer import MusicBoxMusicPlayer

    ## Initialize

    music_player = MusicBoxMusicPlayer()

    ## Single play

    player.single_play([1,3,5])

    ## Load and Start music
    #
    #   music_data example:
    #      [
    #        {'ch':None,  'delay': 500},  # change default delay (500ms)
    #        {'ch':[1,2], 'delay': None}, # play and sleep (default delay)
    #        {'ch':[2,5], 'delay': 1000}, # play and sleep (1000ms)
    #        {'ch':[],    'delay': None}, # sleep (default delay)
    #        {'ch':None,  'delay': None}, # do nothing (no delay)
    #      ]
    #

    player.music_load(music_data)

    ## (Re)start music

    player.music_start()

    ## Pause music: next music_start() play music from this point

    player.music_pause()

    ## Rewind music

    player.music_rewind()

    ## Stop music: puase and rewind

    player.music_stop()

    ## Wait for the music to end

    player.music_wait()

    ## End of program

    music_player.end()
    ============

    Attributes
    ----------
    ch_n: int
        number of channels
    """
    DEF_DELAY = 500  # msec

    ROTATION_SPEED = 10
    ROTATION_GPIO = [5, 6, 13, 19]

    _log = get_logger(__name__, False)

    def __init__(self,
                 wav_mode=False,
                 rotation_speed=ROTATION_SPEED,
                 rotation_gpio=ROTATION_GPIO,
                 debug=False):
        """ Constructor
        initialize and start rotation

        Parameters
        ----------
        wav_mode: bool
            wav-mode flag
        rotation_speed: int
            speed of rotation motor (0 .. 10)
            0: stop rotation motor
        rotation_gpio: list of int
            GPIO pin number of rotation motor (stepper motor)
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('rotation_speed=%s', rotation_speed)
        self._log.debug('rotation_gpio=%s', rotation_gpio)

        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed
        self._rotation_gpio = rotation_gpio

        self._def_delay = self.DEF_DELAY

        self._music_data = None
        self._music_data_i = 0
        self._music_active = False
        self._music_th = None

        if self._wav_mode:
            self._movement = MusicBoxMovementWavFile(debug=self._dbg)
        else:
            self._movement = MusicBoxMovement(
                self._rotation_gpio, self._rotation_speed,
                debug=self._dbg)

        # public valiables
        self.ch_n = self._movement.ch_n

        # start rotation
        self.rotation_speed(self._rotation_speed)

    def end(self):
        """ Call at the end of program

        stop rotation and so on ...
        """
        self._log.debug('doing ..')

        self._movement.rotation_speed(0)
        self._movement.end()

        self._log.debug('done')

    def rotation_speed(self, speed=ROTATION_SPEED):
        """ set rotation speed
        """
        self._log.debug('speed=%s', speed)
        self._rotation_speed = speed
        self._movement.rotation_speed(self._rotation_speed)

    def single_play(self, ch_list=None):
        """ single play

        Parameters
        ----------
        ch_list: list of int
            list of channel number
        """
        self._log.debug('ch_list=%s', ch_list)

        self._movement.single_play(ch_list)

    def single_play_and_sleep(self, ch_list=None, delay=None):
        """ single play and sleep
        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            msec

        ch_list=[1,2,3], delay=500}:  play and sleep 500ms
        ch_list=[1,2,3], delay=None}: play and sleep (default delay)
        ch_list=[],      delay=None}: sleep only (default delay)
        ch_list=None,    delay=300}:  change default delay, no delay
        ch_list=None,    delay=None}: do nothing (no delay)

        """
        self._log.debug('ch=list=%s, delay=%s', ch_list, delay)

        if ch_list is None:
            if delay is None:
                self._log.debug('do nothing')
            else:
                self._def_delay = delay
                self._log.debug('change default delay: %s',
                                self._def_delay)

            return  # no delay

        if delay is None:
            delay = self._def_delay
            self._log.debug('delay=%s (default)', delay)

        self.single_play(ch_list)

        self._log.debug('sleep %s msec', delay)
        time.sleep(delay / 1000)

        self._log.debug('done')

    def music_load(self, music_data, start_flag=True):
        """ load music data

        Parameters
        ----------
        music_data: list of {'ch': ch_list, 'delay': delay_msec}
            ch_list: list of int
            delay_msec: int
        start_flag: bool
            start music or not

          music_data ex.
          [
            {'ch':None,  'delay': 500},  # change default delay (no delay)
            {'ch':[2,5], 'delay': 1000}, # play and sleep 1000ms
            {'ch':[1,2], 'delay': None}, # play and sleep (default delay)
            {'ch':[],    'delay': None}, # sleep (default delay)
            {'ch':None,  'delay': None}, # do nothing (no delay)
               :
               :
          ]
        """
        self._log.debug('music_data=%s', music_data)

        self.music_stop()

        self._music_data = copy.deepcopy(music_data)
        if self._music_data_i >= len(self._music_data):
            self._music_data_i = 0

        if start_flag:
            self.music_start()

    def music_th(self, music_data_i, repeat=True):
        """ music thread function

        Parameters
        ----------
        music_data_i:
            index of music data
        repeat: bool
            repeat flag
        """
        self._log.debug('music_data_i=%s', music_data_i)

        if self._music_data is None:
            self._log.warning('music_data=%s', self._music_data)
            return

        if len(self._music_data) == 0:
            self._log.warning('music_data=%s', self._music_data)
            return

        self._music_data_i = music_data_i
        self._music_active = True

        while True:
            while self._music_active and \
                  self._music_data_i < len(self._music_data):

                data1 = self._music_data[self._music_data_i]
                self.single_play_and_sleep(data1['ch'], data1['delay'])
                self._music_data_i += 1

            if self._music_data_i >= len(self._music_data):
                self._music_data_i = 0

            if not self._music_active:
                break

            if repeat:
                time.sleep(1)
                continue
            else:
                break
                
        self._msuci_active = False

        self._log.debug('done')

    def music_start(self):
        """ start music

        This function starts sub-thread and returns immidiately
        """
        self._log.debug('')

        if self._music_th is not None:
            if self._music_th.is_alive():
                self.music_stop()

        self._log.debug('music_data_i=%s', self._music_data_i)
        self._music_th = threading.Thread(target=self.music_th,
                                          args=(self._music_data_i,),
                                          daemon=True)
        self._music_th.start()

        self._log.debug('done: _music_th=%s', self._music_th)

    def music_wait(self):
        """ wait music to end
        """
        self._log.debug('start waiting')

        if type(self._music_th) == threading.Thread:
            while self._music_th.is_alive():
                self._log.debug('waiting ..')
                time.sleep(0.5)

        self._log.debug('done')

    def music_pause(self):
        """ pause music
        """
        self._log.debug('')

        if type(self._music_th) == threading.Thread:
            self._music_active = False
            self._music_th.join()

        self._log.debug('done: music_data_i=%s', self._music_data_i)

    def music_seek(self, idx=0):
        """ seek music
        """
        self._log.debug('idx=%s', idx)

        if self._music_data is None:
            self._log.warning('_music_data=%s', self._music_data)
            self._music_data_i = 0
            return

        active = self._music_active
        self.music_pause()
        
        if idx > len(self._music_data) - 1:
            idx = len(self._music_data) - 1
            self._log.debug('fix idx=%s', idx)

        self._music_data_i = idx

        if active:
            self.music_start()

    def music_rewind(self):
        """ rewind music
        """
        self.music_seek(0)

    def music_stop(self):
        """ stop music

        pause and rewind
        """
        self._log.debug('')

        self.music_pause()
        self.music_rewind()


# --- 以下、サンプル ---


class SampleApp:
    """ Sample application class

    Attributes
    ----------
    """
    PROMPT_STR = '['
    PROMPT_STR += '(s)tart|'
    PROMPT_STR += '(S)top|'
    PROMPT_STR += '(p)ause|'
    PROMPT_STR += '(r)wind|'
    PROMPT_STR += '(n)ext|'
    PROMPT_STR += '(p)rev|'
    PROMPT_STR += '(w)ait|'
    PROMPT_STR += '0, ..|'
    PROMPT_STR += '[Ctrl]-[D]:END] '

    _log = get_logger(__name__, False)

    def __init__(self, infile,
                 wav_mode,
                 rotation_speed,
                 rotation_gpio,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        infile: list of str
            入力ファイル
        wav_mode: bool
            wav-mode flag
        rotation_speed: int
            speed of rotation motor
        rotation_gpio: list of int
            GPIO pin number for rotation motor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('infile=%s', infile)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('rotation_speed=%s', rotation_speed)
        self._log.debug('rotation_gpio=%s', rotation_gpio)

        self._infile = infile
        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed
        self._rotation_gpio = rotation_gpio

        self._cur_file = None
        if len(self._infile) > 0:
            self._cur_file = 0

        self._player = MusicBoxPlayer(
            self._wav_mode,
            self._rotation_speed, self._rotation_gpio,
            debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('')

        if len(self._infile) > 0:
            self._log.info('File:%s', self._infile[self._cur_file])
            self.load(self._infile[self._cur_file])
            self._player.music_start()

        while True:
            try:
                line1 = input(self.PROMPT_STR)
            except EOFError:
                self._log.info('EOF')
                break

            self._log.debug('line1=%s', line1)

            if len(line1) == 0:
                continue

            if line1 in ('start', 's'):
                self._log.info('File:%s', self._infile[self._cur_file])
                self.load(self._infile[self._cur_file])
                self._player.music_start()
                continue

            if line1 in ('stop', 'S'):
                self._player.music_stop()
                continue

            if line1 in ('pause', 'p'):
                self._player.music_pause()
                continue

            if line1 in ('rewind', 'r'):
                self._player.music_rewind()
                continue

            if line1 in ('wait', 'w'):
                self._player.music_wait()
                continue

            if line1 in ('next', 'n'):
                self._player.music_stop()

                self._cur_file += 1
                if self._cur_file >= len(self._infile):
                    self._cur_file = 0

                self._log.info('File:%s', self._infile[self._cur_file])
                self.load(self._infile[self._cur_file])
                self._player.music_start()
                continue

            if line1 in ('prev', 'P'):
                self._player.music_stop()

                self._cur_file -= 1
                if self._cur_file < 0:
                    self._cur_file = len(self._infile) - 1

                self._log.info('File:%s', self._infile[self._cur_file])
                self.load(self._infile[self._cur_file])
                self._player.music_start()
                continue

            ch_str = line1.replace(' ', '').split(',')
            self._log.debug('ch_str=%s', ch_str)

            try:
                ch_list = [int(c) for c in ch_str]
            except Exception as err:
                self._log.error('%s:%s .. ignored', type(err), err)
                continue

            self._log.debug('ch_list=%s', ch_list)
            self._player.single_play(ch_list)

        self._log.debug('done')

    def end(self):
        """
        Call at the end of program.
        """
        self._log.debug('doing ..')

        self._player.music_stop()
        self._player.end()

        self._log.debug('done')

    def load(self, infile):
        """
        load music file

        Parameters
        ----------
        infile: str
            input file name
        """
        self._log.debug('infile=%s', infile)

        parser = MusicBoxPaperTape(debug=False)
        music_data = parser.parse(infile)
        self._player.music_load(music_data)
        parser.end()


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
MusicBoxPlayer class test program (interactive demo)
''')
@click.argument('infile', type=click.Path(exists=True), nargs=-1)
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode: default=OFF')
@click.option('--speed', '-s', 'speed', type=int,
              default=MusicBoxPlayer.ROTATION_SPEED,
              help='rotation speed (0: stop): default=%s' %
              MusicBoxPlayer.ROTATION_SPEED)
@click.option('--pin1', '-p1', 'pin1', type=int,
              default=MusicBoxPlayer.ROTATION_GPIO[0],
              help='GPIO pin1 of rotation motor: default=%s' %
              MusicBoxPlayer.ROTATION_GPIO[0])
@click.option('--pin2', '-p2', 'pin2', type=int,
              default=MusicBoxPlayer.ROTATION_GPIO[1],
              help='GPIO pin2 of rotation motor: default=%s' %
              MusicBoxPlayer.ROTATION_GPIO[1])
@click.option('--pin3', '-p3', 'pin3', type=int,
              default=MusicBoxPlayer.ROTATION_GPIO[2],
              help='GPIO pin3 of rotation motor: default=%s' %
              MusicBoxPlayer.ROTATION_GPIO[2])
@click.option('--pin4', '-p4', 'pin4', type=int,
              default=MusicBoxPlayer.ROTATION_GPIO[3],
              help='GPIO pin4 of rotation motor: default=%s' %
              MusicBoxPlayer.ROTATION_GPIO[3])
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(infile, wav, speed, pin1, pin2, pin3, pin4, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('infile=%s', infile)
    _log.debug('wav=%s', wav)
    _log.debug('speed=%s', speed)
    _log.debug('pins:%s', (pin1, pin2, pin3, pin4))

    app = SampleApp(
        infile, wav, speed, (pin1, pin2, pin3, pin4),
        debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
