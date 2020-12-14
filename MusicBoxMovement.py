#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box movement class

### for detail ###

$ python3 -m pydoc MusicBoxMovement.MusicBoxMovement


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
#   複数のプログラム(プロセス、スレッド)で実行すると、
#   正常に動作しないので注意
#
movement.rotation_speed(10)

# 単発で音を鳴らす
movement.single_play([0,2,4])

# プログラム終了時
movement.end()

---
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

import glob
import threading
import time
import pygame

from MusicBoxRotationMotor import MusicBoxRotationMotor
from MusicBoxServo import MusicBoxServo

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
        self._log.debug('%s: doing ..', __class__.__name__)
        self._log.debug('%s: done.', __class__.__name__)

    def single_play(self, ch_list):
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
    ROTATION_GPIO = [5, 6, 13, 19]

    _log = get_logger(__name__, False)

    def __init__(self,
                 rotation_gpio=ROTATION_GPIO,
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
        self._log.debug('rotation_gpio=%s', rotation_gpio)
        self._log.debug('rotation_speed=%s', rotation_speed)

        # start rotation
        self._mtr = MusicBoxRotationMotor(
            rotation_gpio[0],
            rotation_gpio[1],
            rotation_gpio[2],
            rotation_gpio[3],
            debug=False)
        self._rotation_gpio = rotation_gpio
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
        except ValueError as err:
            self._log.warning('%s: %s', type(err), err)

        self._log.debug('done')

    def rotation_speed(self, speed=0):
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
                self._log.error('ch=%s: invalid', ch)
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
    _log = get_logger(__name__, False)

    def __init__(self,
                 wav_mode=False,
                 rotation_gpio=MusicBoxMovement.ROTATION_GPIO,
                 rotation_speed=MusicBoxMovement.ROTATION_SPEED,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        wav_mode: bool
            wav file mode
        rotation_gpio: list of int
            GPIO pin number of rotation motor(stepper motor)
        rotation_speed: int
            speed of rotation motor
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('rotation_gpio=%s', rotation_gpio)
        self._log.debug('rotation_speed=%s', rotation_speed)

        self._wav_mode = wav_mode
        self._rotation_gpio = rotation_gpio
        self._rotation_speed = rotation_speed

        if self._wav_mode:
            self._movement = MusicBoxMovementWavFile(debug=self._dbg)
        else:
            self._movement = MusicBoxMovement(
                self._rotation_gpio, self._rotation_speed,
                debug=self._dbg)

    def main(self):
        """
        main routine
        """
        self._log.debug('start')

        self._movement.rotation_speed(self._rotation_speed)
        self.play_interactive()

        self._log.debug('done')

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
            except Exception as err:
                self._log.error('%s: %s .. ignored', type(err), err)
                continue

            self._log.debug('ch_list=%s', ch_list)

            self._movement.single_play(ch_list)

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
@click.option('--wav', '-w', 'wav', is_flag=True, default=False,
              help='wav file mode')
@click.option('--speed', '-s', 'speed', type=int,
              default=MusicBoxMovement.ROTATION_SPEED,
              help='rotation speed (0: don\'t use rotation motor')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(wav, speed, debug):
    """
    サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('wav=%s, speed=%s', wav, speed)

    app = SampleApp(wav, rotation_speed=speed,
                    debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
