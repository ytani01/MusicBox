#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Player class

### Architecture (server side)

         --------------------------------------------
        |                WebsockServer               |
        |--------------------------------------------|
This -->|            Player             |            |
        |-------------------------------|            |
        |           Movement            |            |
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

import threading
import copy
import time

from . import Movement, MovementWav1, MovementWav2, MovementWav3
from .my_logger import get_logger


class Player:
    """ Music Box Player class

    ## Initialize

    player = Player()

    ## Single play
    player.single_play([1,3,5])

    ## for Music
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

    player.music_play()
    player.music_pause()
    player.music_rewind()
    player.music_stop()
    player.music_wait()

    music_player.end()  # call at the end of using ``player``
    ============

    Attributes
    ----------
    ch_n: int
        number of channels
    """
    WAVMODE_NONE = 0
    WAVMODE_PIANO = 1
    WAVMODE_PIANO_FULL = 2
    WAVMODE_MIDI_FULL = 3

    DEF_DELAY = 500  # msec

    ROTATION_SPEED = 10
    ROTATION_GPIO = [5, 6, 13, 19]

    def __init__(self,
                 wav_mode=WAVMODE_NONE,
                 rotation_speed=ROTATION_SPEED,
                 rotation_gpio=ROTATION_GPIO,
                 wavdir='wav',
                 debug=False):
        """ Constructor
        initialize and start rotation

        Parameters
        ----------
        wav_mode: int
            Wav File mode
        rotation_speed: int
            speed of rotation motor (0 .. 10)
            0: stop rotation motor
        rotation_gpio: list of int
            GPIO pin number of rotation motor (stepper motor)
        wavdir: str
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('rotation_speed=%s', rotation_speed)
        self._log.debug('rotation_gpio=%s', rotation_gpio)
        self._log.debug('wavdir=%s', wavdir)

        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed
        self._rotation_gpio = rotation_gpio
        self._wavdir = wavdir

        self._def_delay = self.DEF_DELAY

        self._music_data = None
        self._music_data_i = 0
        self._music_active = False
        self._music_th = None

        if self._wav_mode == self.WAVMODE_NONE:
            self._movement = Movement(
                self._rotation_gpio, self._rotation_speed,
                debug=self._dbg)

        elif self._wav_mode == self.WAVMODE_PIANO:
            self._movement = MovementWav1(wav_topdir=self._wavdir,
                                          debug=self._dbg)

        elif self._wav_mode == self.WAVMODE_PIANO_FULL:
            self._movement = MovementWav2(wav_topdir=self._wavdir,
                                          debug=self._dbg)

        elif self._wav_mode == self.WAVMODE_MIDI_FULL:
            self._movement = MovementWav3(wav_topdir=self._wavdir,
                                          debug=self._dbg)

        else:
            msg = 'invalid wav_mode: %s' % self._wav_mode
            raise ValueError(msg)

        self.ch_n = self._movement.ch_n

        self.rotation_speed(self._rotation_speed)

    def end(self):
        """ Call at the end of program

        stop movement
        """
        self._log.debug('doing ..')

        self._movement.rotation_speed(0)
        self._movement.end()

        self._log.debug('done')

    def rotation_speed(self, speed=ROTATION_SPEED):
        """
        Parameters
        ----------
        speed: int
        """
        self._log.debug('speed=%s', speed)
        self._rotation_speed = speed
        self._movement.rotation_speed(self._rotation_speed)

    def single_play(self, ch_list=None):
        """
        Parameters
        ----------
        ch_list: list of int
            list of channel number
        """
        self._log.info('ch_list=%s', ch_list)

        self._movement.single_play(ch_list)

    def sleep_and_single_play(self, ch_list=None, delay=None):
        """ sleep and single play
        Parameters
        ----------
        ch_list: list of int
            channel list
        delay: int
            msec

        ch_list=[1,2,3], delay=500}:  sleep 500ms and play
        ch_list=[1,2,3], delay=None}: sleep(default delay) and play
        ch_list=[],      delay=None}: sleep only (default delay)
        ch_list=None,    delay=300}:  change default delay, no delay
        ch_list=None,    delay=None}: do nothing (no delay)

        """
        self._log.debug('delay=%.2f, ch_list=%s', delay, ch_list)

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

        self._log.debug('sleep %.2f msec', delay)
        time.sleep(delay / 1000)

        self.single_play(ch_list)

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
        # self._log.debug('music_data=%s', music_data)

        self._music_data = copy.deepcopy(music_data)

        self.music_stop()

        if self._music_data_i >= len(self._music_data):
            self._music_data_i = 0

        if start_flag:
            self.music_play()

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
            while self._music_active:
                if self._music_data_i >= len(self._music_data):
                    self._music_data_i = 0
                    break

                data1 = self._music_data[self._music_data_i]
                self.sleep_and_single_play(data1['ch'],
                                           data1['delay'])
                self._music_data_i += 1

            if not self._music_active:
                break

            if not repeat:
                break

            time.sleep(1)

        self._msuci_active = False

        self._log.debug('done')

    def get_music_length_sec(self):
        """
        """
        length_sec = 0

        if self._music_data:
            length_sec = self._music_data[-1]['abs_time']

        self._log.debug('length_sec=%s', length_sec)
        return length_sec

    def get_music_pos_sec(self):
        """
        music position in sec

        Returns
        -------
        pos_sec: float
            -1: not playing
        """
        if not self._music_active:
            pos_sec = -1
        else:
            pos_sec = self._music_data[self._music_data_i]['abs_time']

        self._log.debug('pos_sec_=%s', pos_sec)
        return pos_sec

    def music_play(self):
        """ start music

        This function starts sub-thread and returns immidiately
        """
        self._log.debug('music_th=%s', self._music_th)

        if self._music_th:
            if self._music_th.is_alive():
                self._log.debug('music is playing .. do nothing')
                return

        self._log.debug('music_data_i=%s', self._music_data_i)
        self._music_th = threading.Thread(target=self.music_th,
                                          args=(self._music_data_i,),
                                          daemon=True)
        self._music_th.start()

        self._log.debug('done: _music_th=%s', self._music_th)

    def music_pause(self):
        """ pause music """
        self._log.debug('')

        if type(self._music_th) == threading.Thread:
            self._music_active = False

            count = 0
            while self._music_th.is_alive():
                if count > 0:
                    self._log.info('waiting music_th to end')
                self._music_th.join(timeout=1)
                count += 1

        self._log.debug('done: music_data_i=%s', self._music_data_i)

    def music_wait(self):
        """ wait music to end
        TBD

        """
        self._log.debug('start waiting')

        if type(self._music_th) == threading.Thread:
            while self._music_th.is_alive():
                self._log.debug('waiting ..')
                time.sleep(0.5)

        self._log.debug('done')

    def music_seek(self, idx=0):
        """ seek music """
        self._log.debug('idx=%s', idx)

        if self._music_data is None:
            self._music_data = []

        self._log.debug('idx=%s/%s', idx, len(self._music_data) - 1)

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
            self.music_play()

    def music_seek_percent(self, percent: float = 0):
        """ seek percent

        Parameters
        ----------
        percent: float
        """
        self._log.debug('percent=%s', percent)

        if not self._music_data:
            self._log.error('no music data')
            return

        if percent > 100:
            percent = 100
            self._log.error('[fix] percent: %s', percent)
            return

        pos_sec = self.get_music_length_sec() * percent / 100.0
        self._log.debug('pos_sec=%s sec', pos_sec)

        idx = -1
        for idx, data in enumerate(self._music_data):
            if data['abs_time'] >= pos_sec:
                break

        if idx < 0:
            self._log.error('invalid pos:%s %%', percent)
            return

        idx = int(len(self._music_data) * percent / 100.0)
        self.music_seek(idx)

    def music_shift_percent(self, d_percent):
        """
        incremental seek
        """
        self._log.debug('d_percent=%s', d_percent)

        length_sec = self.get_music_length_sec()
        if length_sec == 0:
            return

        cur_sec = self.get_music_pos_sec()
        cur_percent = cur_sec / length_sec * 100
        new_percent = cur_percent + d_percent
        self.music_seek_percent(new_percent)

    def music_rewind(self):
        """ rewind music
        """
        self._log.debug('')
        self.music_seek(0)

    def music_stop(self):
        """ stop music

        pause and rewind
        """
        self._log.debug('')

        self.music_pause()
        self.music_rewind()

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
            True: on, False: off
        pw: int
            pulse width
        tap: bool
            after change, execute tap()
        conf_file: str
            configuration file (path name)
        """
        self._log.debug('ch=%s, on=%s, pw=%s, tap=%s, conf_file=%s',
                        ch, on, pw, tap, conf_file)

        self._movement.set_onoff(ch, on, pw, tap, conf_file)

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

        self._movement.calibrate(ch, on, pw_diff, tap, conf_file)
