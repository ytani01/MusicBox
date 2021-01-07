#
# (c) 2021 Yoichi Tanibayashi
#
"""
Music Box movement class

### Class tree

MovementBase
 |
 +- Movement            : for servo motor
 +- MovementWavFile     : for wav file (15 notes)
 +- MovementWavFileFull : for wav file (full notes)


### Module Architecture (server side)

         --------------------------------------------
        |           MusicBoxWebsockServer            |
        |-------------------------------+------------|
        |             Player            |            |
        |-------------------------------|            |
This -->|            Movement           |            |
        |-------------------------------| websockets |
        |     Servo     | RotationMotor |            |
        |---------------+---------------|            |
        | ServoPCA9685  |  StepMtrTh    |            |
        |---------------+---------------|            |
        | pigpioPCA9685 |   StepMtr     |            |
         --------------------------------------------

"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

from pathlib import Path
import glob
import threading
import time
import pygame
from .my_logger import get_logger
from . import RotationMotor, Servo


class MovementBase:
    """
    Music Box movement base class

    Don't use directory.
    Use sub class

    Attributes
    ----------
    active: bool
        active flag
    """
    def __init__(self, ch_n=0, debug=False):
        """ Constructor

        Parameters
        ----------
        ch_n: int
            number of channel from SubClass.super()__init__(ch_n=..)
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
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

    def set_onoff(self, ch_, on_=False, pw_=None, tap=False,
                  conf_file=None):
        """
        on/offパラメータ設定(絶対値指定)

        実装はサブクラスでオーバーライド

        Parameters
        ----------
        ch_: int
            servo channel
        on_: bool
            True: on, False: off
        pw_: int
            pulse width
        tap: bool
            after change, execute tap()
        conf_file: str
            configuration file (path name)
        """
        self._log.debug('ch_=%s, on_=%s, pw_=%s, tap=%s, conf_file=%s',
                        ch_, on_, pw_, tap, conf_file)

    def calibrate(self, ch_, on_=False, pw_diff=0, tap=False,
                  conf_file=None):
        """
        on/offパラメータ変更(差分指定)

        実装はサブクラスでオーバーライド

        Parameters
        ----------
        ch_: int
            servo channel
        on_: bool
            True: on, False: off
        tap: bool
            after change, execute tap()
        pw_diff: int
            differenc of pulse width
        conf_file: str
            configuration file (path name)
        """
        self._log.debug(
            'ch_=%s, on_=%s, pw_diff=%s, tap=%s, conf_file=%s',
            ch_, on_, pw_diff, tap, conf_file)


class Movement(MovementBase):
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
                 push_interval=Servo.DEF_PUSH_INTERVAL,
                 pull_interval=Servo.DEF_PULL_INTERVAL,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        rotation_gpio: list of int
            GPIO pin number of rotation motor (stepper motor)
        rotation_speed: int
            speed of rotation motor (0 .. 10)
            0: don't use rotation motor
        push_interval, pull_interval: float
            interval sec
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('rotation_gpio=%s', rotation_gpio)
        self._log.debug('rotation_speed=%s', rotation_speed)

        # start rotation
        self._mtr = RotationMotor(
            rotation_gpio[0],
            rotation_gpio[1],
            rotation_gpio[2],
            rotation_gpio[3],
            debug=False)
        self._rotation_gpio = rotation_gpio
        time.sleep(1)

        # init servo
        self._servo = Servo(push_interval=push_interval,
                            pull_interval=pull_interval,
                            debug=self._dbg)

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

    def set_onoff(self, ch, on=False, pw=None, tap=False,
                  conf_file=None):
        """
        on/offパラメータ設定(絶対値指定)

        変更後 conf_file に保存する。

        Parameters
        ----------
        ch: int
            servo channel
        on: bool
            True: on
            False: off
        pw: int
            pulse width
        tap: bool
            after change, execute tap()
        conf_file: str
            configuration file (path name)
        """
        self._log.debug('ch=%s, on=%s, pw=%s, tap=%s, conf_file=%s',
                        ch, on, pw, tap, conf_file)

        self._servo.set_onoff(ch, on, pw, tap, conf_file)

    def calibrate(self, ch, on=False, pw_diff=0, tap=False,
                  conf_file=None):
        """
        on/offパラメータ変更(差分指定)

        変更後 conf_file に保存する。

        Parameters
        ----------
        ch: int
            servo channel
        on: bool
            True: on
            False: off
        pw_diff: int
            differenc of pulse width
        tap: bool
            after change, execute tap()
        conf_file: str
            configuration file (path name)
        """
        self._log.debug('ch=%s, on=%s, pw_diff=%s, tap=%s, conf_file=%s',
                        ch, on, pw_diff, tap, conf_file)

        self._servo.calibrate(ch, on, pw_diff, tap, conf_file)


class MovementWav1(MovementBase):
    """
    Play wav_file insted of music box movement.

    Music Boxと同じ音階
    """
    _log = get_logger(__name__, False)

    DEF_WAV_TOPDIR = 'wav'
    DEF_WAV_SUBDIR = 'piano'

    WAV_FILE_PREFIX = 'ch'
    WAV_FILE_SUFFIX = '.wav'

    NOTE_ORIGIN = 0

    def __init__(self,
                 wav_topdir=DEF_WAV_TOPDIR, wav_subdir=DEF_WAV_SUBDIR,
                 wav_prefix=WAV_FILE_PREFIX,
                 wav_suffix=WAV_FILE_SUFFIX,
                 note_origin=NOTE_ORIGIN,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        wav_topdir: str
        wav_subdir: str
            directory name
        wav_prefix: str
        wav_suffix: str
        note_origin: int
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('wav_topdir=%s, wav_subdir=%s',
                        wav_topdir, wav_subdir)
        self._log.debug('wav_prefix=%s, wav_suffix=%s',
                        wav_prefix, wav_suffix)
        self._log.debug('note_origin=%s', note_origin)

        self._wav_topdir = wav_topdir
        self._wav_subdir = wav_subdir
        self._wav_prefix = wav_prefix
        self._wav_suffix = wav_suffix
        self._note_origin = note_origin

        wav_path = Path('%s/%s' % (self._wav_topdir, self._wav_subdir))
        self._wav_dir = str(wav_path.expanduser())
        self._log.debug('wav_dir=%s', self._wav_dir)

        pygame.mixer.init()
        self._sound = self.load_wav(self._wav_dir,
                                    self._wav_prefix, self._wav_suffix)

        if not self._sound:
            msg = 'no wav file'
            self._log.error(msg)
            raise RuntimeError(msg)

        super().__init__(ch_n=len(self._sound), debug=self._dbg)

    def end(self):
        """
        Call at the end of program
        """
        self._log.debug('doing ..')
        super().end()

        self._log.debug('done')

    def load_wav(self, wav_dir,
                 wav_prefix=WAV_FILE_PREFIX,
                 wav_suffix=WAV_FILE_SUFFIX):
        """
        load wav files

        Parameters
        ----------
        wav_dir: str
            directory name
        wav_prefix: str
        wav_suffix: str
        """
        glob_pattern = "%s/%s*%s" % (
            wav_dir, wav_prefix, wav_suffix)
        self._log.debug('glob_pattern=%s', glob_pattern)

        wav_files = sorted(glob.glob(glob_pattern))
        self._log.debug('wav_files=%s', wav_files)

        return [pygame.mixer.Sound(f) for f in wav_files]

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

        if type(ch_list) != list:
            self._log.debug('invalid ch_list: %s', ch_list)
            return

        self._log.debug('play sounds')
        for ch_ in ch_list:
            if ch_ is None:
                self._log.warning('ch_=%s: ignored', ch_)
                continue

            if ch_ < 0 or ch_ > self.ch_n - 1:
                self._log.warning('ch_=%s: ignored', ch_)
                continue

            snd_i = ch_ - self._note_origin
            self._log.debug('snd_i=%s', snd_i)

            snd = self._sound[snd_i]
            snd.set_volume(0.2)   # 音割れ軽減
            # snd.play(fade_ms=50)  # fade_time: ブツブツ音軽減
            # 早いテンポに対応するには、``maxtime``を制限した方がいいが、
            # 音が不自然になる
            snd.play(fade_ms=50, maxtime=400)

        self._log.debug('done')


class MovementWav2(MovementWav1):
    """
    ピアノの音階 (21 .. 108)
    """
    DEF_WAV_TOPDIR = 'wav'
    DEF_WAV_SUBDIR = 'piano'
    WAV_FILE_PREFIX = 'piano'
    WAV_FILE_SUFFIX = '.wav'

    NOTE_ORIGIN = 21

    def __init__(self,
                 wav_topdir=DEF_WAV_TOPDIR, wav_subdir=DEF_WAV_SUBDIR,
                 debug=False):
        super().__init__(wav_topdir=wav_topdir, wav_subdir=wav_subdir,
                         wav_prefix=self.WAV_FILE_PREFIX,
                         wav_suffix=self.WAV_FILE_SUFFIX,
                         note_origin=self.NOTE_ORIGIN,
                         debug=debug)


class MovementWav3(MovementWav1):
    """
    MIDIの全音階 (0 .. 127)
    """
    DEF_WAV_TOPDIR = 'wav'
    DEF_WAV_SUBDIR = 'midi'
    WAV_FILE_PREFIX = 'note'
    WAV_FILE_SUFFIX = '.wav'

    NOTE_ORIGIN = 0

    def __init__(self,
                 wav_topdir=DEF_WAV_TOPDIR, wav_subdir=DEF_WAV_SUBDIR,
                 debug=False):
        super().__init__(wav_topdir=wav_topdir, wav_subdir=wav_subdir,
                         wav_prefix=self.WAV_FILE_PREFIX,
                         wav_suffix=self.WAV_FILE_SUFFIX,
                         note_origin=self.NOTE_ORIGIN,
                         debug=debug)
