#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box movement class

### for detail ###

$  pydoc3 MusicBoxMovement.MusicBoxMovement


### class tree ###

MusicBoxMovementBase
 |
 +- MusicBoxMovement: servo
 +- MusicBoxMovementWavFile: wav file


### Simple usage ###
---
# import
from MusicBoxMovement import MusicBoxMovement

# 初期設定
movement = MusicBoxMovement()

# ローテーション・モーター始動
#   複数のプログラムで実行すると、正常に動作しないので注意
#
movement.rotation_speed(10)

##
# 単発で音を鳴らす
movement.play([0,2,4])

##
# 以下、音楽再生関連: 一連の(パージング後の)データを続けて演奏
#   [重要] スレッドで動作するので、関数はすぐリターンする。
#
# music_data形式: [{'ch': ch_list, 'delay': msec}, ... ]
#   ch_list: チャンネルリスト ex [0,2,4]
#   msec:    音を鳴らした後の遅延(msec)
#

# 音楽データのロード
movement.music_load([
    {'ch':None,    'delay':500},   # change default delay
    {'ch':[1],     'delay':None},
    {'ch':[1,3,5], 'delay':None},
       :
    {'ch':[0,2],   'delay':1000}
])

# 演奏開始
movement.music_play()

# 演奏を中断
movement.music_stop()

# 演奏終了まで待つ
movement.music_wait()

# プログラム終了時
#   演奏は強制終了
movement.end()
---
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MusicBoxPaperTape import MusicBoxPaperTape
from MusicBoxRotationMotor import MusicBoxRotationMotor
from MusicBoxServo import MusicBoxServo
import pygame
import glob
import threading
import copy
import time
from MyLogger import get_logger


class MusicBoxMovementBase:
    """
    Music Box movement base class

    Don't use directory.
    Use sub class

    Attributes
    ----------
    active: bool
        active flag
    """
    DEF_DELAY = 500
    MOVEMENT_END = 'End Movement'

    _log = get_logger(__name__, False)

    def __init__(self, ch_n=0, debug=False):
        """ Constructor

        Parameters
        ----------
        ch_n: int
            number of channel from SubClass.super()__init__(ch_n=..)
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('ch_n=%s', ch_n)

         # public
        self.ch_n = ch_n

        # private
        self._def_delay = self.DEF_DELAY

        self._music_data = None
        self._music_active = False
        self._music_data_i = 0
        self._music_th = threading.Thread(target=self.music_th,
                                          args=(self._music_data_i,),
                                          daemon=True)

    def rotation_speed(self, speed=0):
        """
        set rotation speed
        default: 0 (stop)
        """
        self._log.debug('*** do nothing *** (speed=%s)', speed)

    def end(self):
        """
        Call at the end of program
        """
        self._log.debug('doing ..')

        self.music_stop()

        if type(self._music_th) == threading.Thread:
            self._music_th.join()

        self._log.debug('done')

    def music_th(self, music_data_i):
        """
        Parameters
        ----------
        music_data_i: int
            index of self._music_data
        """
        self._log.debug('music_data_i=%s', music_data_i)

        if self._music_data is None:
            return

        if len(self._music_data) == 0:
            return

        self._music_active = True
        self._music_data_i = music_data_i

        while self._music_active and \
              self._music_data_i < len(self._music_data):

            data1 = self._music_data[self._music_data_i]
            self.play_and_sleep(data1['ch'], data1['delay'])
            self._music_data_i += 1

        if self._music_data_i >= len(self._music_data):
            self._music_data_i = 0
        self._music_active = False

        self._log.debug('done.')

    def music_load(self, music_data):
        """
        Parameters
        ----------
        music_data: list of {'ch':[0,1,2..], 'delay':300}
            music data
        """
        self._log.debug('music_data=%s', music_data)

        self._music_data = copy.deepcopy(music_data)

    def music_start(self):
        """
        start music
        """
        self._log.debug('')

        if self._music_th.is_alive():
            self.music_stop()

        self._music_th = threading.Thread(target=self.music_th,
                                          args=(self._music_data_i,),
                                          daemon=True)
        self._music_th.start()

        self._log.debug('done')

    def music_stop(self):
        """
        stop music
        """
        self._log.debug('')

        self.music_pause()

        self._music_data_i = 0

    def music_pause(self):
        """
        pause music
        """
        self._log.debug('')
        self._music_active = False

        if type(self._music_th) != threading.Thread:
            return

        while self._music_th.is_alive():
            time.sleep(0.1)

    def music_wait(self):
        """
        wait music
        """
        self._log.debug('')

        while self._music_th.is_alive():
            self._log.debug('waiting end of music ..')
            time.sleep(1)

        self._log.debug('done')

    def play_and_sleep(self, ch_list=None, delay=None):
        """
        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            msec

        ch_list=[1,2,3], delay=100}:  play and sleep
        ch_list=[1,2,3], delay=None}: play and sleep (default delay)
        ch_list=[],      delay=None}: sleep only (default delay)
        ch_list=None,    delay=100}:  change default delay, don't sleep
        ch_list=None,    delay=None}: do nothing (don't sleep)

        """
        self._log.debug('ch_list=%s, delay=%s', ch_list, delay)

        if ch_list is None:
            if delay is None:
                self._log.debug('do nothing')
            else:
                self._def_delay = delay
                self._log.debug('change default delay: %s',
                                self._def_delay)

            return  # don't play

        if delay is None:
            delay = self._def_delay
            self._log.debug('delay=%s (default)', delay)

        self.play(ch_list)

        self._log.debug('sleep %s msec', delay)
        self.sleep(delay)

        self._log.debug('done')

    def play(self, ch_list):
        """
        play One sound (in thread)
        """
        self._log.debug('ch_list=%s', ch_list)

        # self.play_sound(ch_list)
        threading.Thread(target=self.play_sound,
                         args=(ch_list,)).start()

    def play_sound(self, ch_list):
        """
        Must be overridden
        """
        self._log.debug('ch_list=%s', ch_list)
        self._log.error('*** This method must be overridden ***')

    def sleep(self, delay):
        """
        Parameters
        ----------
        delay: int
            delay [msec]
        """
        self._log.debug('delay=%s', delay)

        time.sleep(delay / 1000)

        self._log.debug('done')


class MusicBoxMovement(MusicBoxMovementBase):
    """
    Music Box Movement Class

    多重起動すると、ローテーション・モータの制御で
    衝突が起こり、正常に回転しなくなるので注意！

    2つめ以降のインスタンス生成時に
    ``rotation_speed=0``とすること。

    Attributes
    ----------
    ch_n: int
        number of channels
    """
    ROTATION_SPEED = 10
    ROTATION_PIN1 = 5
    ROTATION_PIN2 = 6
    ROTATION_PIN3 = 13
    ROTATION_PIN4 = 19

    _log = get_logger(__name__, False)

    def __init__(self,
                 pin1=ROTATION_PIN1,
                 pin2=ROTATION_PIN2,
                 pin3=ROTATION_PIN3,
                 pin4=ROTATION_PIN4,
                 rotation_speed=ROTATION_SPEED,
                 debug=False):
        """ Constructor
        pin1, pin2, pin3, pin4: int
            GPIO pin number of rotation motor (stepper motor)
        rotation_speed: int
            speed of rotation motor (0 .. 10)
            0: don't use rotation motor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s', (pin1, pin2, pin3, pin4))
        self._log.debug('rotation_speed=%s', rotation_speed)

        # start rotation
        self._mtr = MusicBoxRotationMotor(pin1, pin2, pin3, pin4,
                                          debug=False)
        time.sleep(2)

        # init servo
        self._servo = MusicBoxServo(debug=False)

        super().__init__(ch_n=self._servo.servo_n, debug=self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._servo.end()
        self._mtr.end()
        self._log.debug('done')

    def play_sound(self, ch_list):
        """
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

    def rotation_speed(self, speed):
        self._log.debug('speed=%s', speed)
        self._mtr.set_speed(speed)


class MusicBoxMovementWavFile(MusicBoxMovementBase):
    """ MusicBoxMovementWavFile

    Play wav_file insted of music box movement.
    """
    _log = get_logger(__name__, False)

    DEF_WAV_DIR = './wav'

    WAV_FILE_PREFIX = 'ch'
    WAV_FILE_SUFFIX = 'wav'

    SERVO_DELAY = 350  # msec

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

        super().__init__(ch_n=len(self._sound), debug=self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._log.debug('done')

    def play_sound(self, ch_list):
        """
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
                        self.SERVO_DELAY)
        time.sleep(self.SERVO_DELAY / 1000)
        """

        self._log.debug('done')

    def load_wav(self, wav_dir=DEF_WAV_DIR):
        """
        load wav files

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
    """
    Sample application class
    """
    DEF_DELAY = 500  # msec

    _log = get_logger(__name__, False)

    def __init__(self,
                 paper_tape_file, wav_mode=False,
                 pin1=MusicBoxMovement.ROTATION_PIN1,
                 pin2=MusicBoxMovement.ROTATION_PIN2,
                 pin3=MusicBoxMovement.ROTATION_PIN3,
                 pin4=MusicBoxMovement.ROTATION_PIN4,
                 rotation_speed=MusicBoxMovement.ROTATION_SPEED,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        paper_tape_file: paper tape file name (path name)
            description
        wav_mode: bool
            wav file mode
        pin1, pin2, pin3, pin4: int
            GPIO pin number of rotation motor(stepper motor)
        rotation_speed: int
            speed of rotation motor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('paper_tape_file=%s', paper_tape_file)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('pins=%s', (pin1, pin2, pin3, pin4))
        self._log.debug('rotation_speed=%s', rotation_speed)

        self._paper_tape_file = paper_tape_file
        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed

        # parser object
        self._parser = MusicBoxPaperTape(debug=self._dbg)

        # movement object
        if self._wav_mode:
            self._movement = MusicBoxMovementWavFile(debug=self._dbg)
        else:
            self._movement = MusicBoxMovement(pin1, pin2, pin3, pin4,
                                              self._rotation_speed,
                                              debug=self._dbg)

    def main(self):
        """
        main routine
        """
        self._log.debug('start')

        self._movement.rotation_speed(self._rotation_speed)

        if len(self._paper_tape_file) > 0:
            for f in self._paper_tape_file:
                self._log.info('f=%s', f)
                self.play_file(f)
                self._log.info('%s .. end', f)

        else:
            self._log.info('Interactive mode')
            self.play_interactive()

        self._log.debug('done')

    def play_file(self, paper_tape_file):
        """
        parse paper tape file and play
        """
        self._log.debug('paper_tape_file=%s', paper_tape_file)

        music_data = self._parser.parse(paper_tape_file)
        self._log.debug('music data:')
        for i, d in enumerate(music_data):
            self._log.debug('%4d: %s', i, d)
        self._log.debug('end of music_data')

        self._movement.music_load(music_data)
        self._movement.music_start()

        while True:
            prompt = '[start|stop|pause|wait|next|0, ..] '

            try:
                line1 = input(prompt)
            except EOFError:
                self._log.info('EOF')
                break

            self._log.debug('line1=%a', line1)

            if len(line1) == 0:
                continue

            if line1 == 'start':
                self._movement.music_start()
                continue

            if line1 == 'stop':
                self._movement.music_stop()
                continue

            if line1 == 'pause':
                self._movement.music_pause()
                continue

            if line1 == 'wait':
                self._movement.music_wait()
                break

            if line1 == 'next':
                self._movement.music_stop()
                break

            ch_str = line1.replace(' ', '').split(',')
            self._log.debug('ch_str=%s', ch_str)

            try:
                ch_list = [int(c) for c in ch_str]
            except Exception as e:
                self._log.error('%s: %s .. ignored', type(e), e)
                continue

            self._log.debug('ch_list=%s', ch_list)

            self._movement.play(ch_list)

    def play_interactive(self):
        """
        interactive play
        """
        self._log.debug('')

        while True:
            prompt = '[0-%s, ..]> ' % (14)

            try:
                line1 = input(prompt)
            except EOFError:
                self._log.info('EOF')
                break
            except Exception as e:
                self._log.error('%s: %s .. ignored', type(e), e)
                continue

            self._log.debug('line1=%a', line1)

            if len(line1) == 0:
                break

            ch_str = line1.replace(' ', '').split(',')
            self._log.debug('ch_str=%s', ch_str)

            try:
                ch_list = [int(c) for c in ch_str]
            except Exception as e:
                self._log.error('%s: %s .. ignored', type(e), e)
                continue

            self._log.debug('ch_list=%s', ch_list)

            self._movement.play(ch_list)

        self._log.info('END')

    def end(self):
        """
        Call at the end of program.
        """
        self._log.debug('doing ..')

        self._movement.end()

        self._log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('paper_tape_file', type=click.Path(exists=True), nargs=-1)
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode')
@click.option('--speed', '-s', 'speed', type=int,
              default=MusicBoxMovement.ROTATION_SPEED,
              help='rotation speed (0: don\'t use rotation motor')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(paper_tape_file, wav, speed, debug):
    """
    サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('paper_tape_file=%s', paper_tape_file)
    _log.debug('wav=%s, speed=%s', wav, speed)

    app = SampleApp(paper_tape_file, wav, rotation_speed=speed,
                    debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
