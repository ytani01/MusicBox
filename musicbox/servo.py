#
# (c) 2021 FabLab Kannai
#
"""
Rotation Motor driver for Music Box

### config file



### Architecture

 ---------------
|    Servo      |
|---------------|
| ServoPCA9685  |
|---------------|
| pigpioPCA9685 |
 ---------------

"""
__author__ = 'FabLab Kannai'
__date__   = '2021/01'

import os
import time
import pigpio
import threading
from servoPCA9685 import Servo as ServoPCA9685
from .my_logger import get_logger


class Servo:
    """
    Servo Motor for Music Box

    Attributes
    ----------
    servo_n: int
        number of servo motors
    """
    __log = get_logger(__name__, False)

    DEF_CONF_FNAME = "music-box-servo.conf"
    DEF_CONF_DIR = os.environ['HOME']
    DEF_CONFFILE = DEF_CONF_DIR + '/' + DEF_CONF_FNAME

    DEF_PUSH_INTERVAL = 0.2  # sec
    DEF_PULL_INTERVAL = 0.2  # sec

    DEF_SERVO_N = 15

    PW_CENTER = ServoPCA9685.PW_CENTER
    PW_MIN = ServoPCA9685.PW_MIN
    PW_MAX = ServoPCA9685.PW_MAX
    PW_OFF = 0
    PW_NOP = -1

    def __init__(self, conf_file=DEF_CONFFILE,
                 push_interval=DEF_PUSH_INTERVAL,
                 pull_interval=DEF_PULL_INTERVAL,
                 servo_n=DEF_SERVO_N,
                 debug=False):
        """ Constractor

        Parameters
        ----------
        conf_file: str
            configuration file name (path name)
        push_interval, pull_interval: float
            push/pull interval (sec)
        servo_n: int
            number of servo motors
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('conf_file=%s' % conf_file)
        self.__log.debug('push/pull interval=%s',
                         (push_interval, pull_interval))
        self.__log.debug('servo_n=%s', servo_n)

        self.conf_file = conf_file
        self.push_interval = push_interval
        self.pull_interval = pull_interval
        self.servo_n = servo_n

        self._pi = pigpio.pi()

        self._on = [self.PW_CENTER] * self.servo_n
        self._off = [self.PW_CENTER] * self.servo_n
        self._moving = [False] * self.servo_n
        self.__log.debug('on=%s', self._on)
        self.__log.debug('off=%s', self._off)
        self.__log.debug('moving=%s', self._moving)

        self.load_conf(self.conf_file)

        self._dev = ServoPCA9685(list(range(self.servo_n)), self._pi,
                                  debug=self._dbg)
        self.pull(list(range(self.servo_n)))

    def end(self):
        """終了処理

        プログラム終了時に呼ぶこと
        """
        self.__log.debug('doing ..')
        time.sleep(0.5)
        self._dev.end()
        time.sleep(0.5)
        self._pi.stop()
        self.__log.debug('done')

    def load_conf(self, conf_file=None):
        """設定ファイルを読み込む

        Parameters
        ----------
        conf_file: str
            設定ファイル名(フルパス)
        """
        self.__log.debug('conf_file=%s', conf_file)

        if conf_file is None:
            conf_file = self.conf_file
            self.__log.debug('conf_file=%s', conf_file)

        with open(conf_file) as f:
            lines = f.readlines()

        for line in lines:
            col = line.replace(' ', '').rstrip('\n').split(',')
            self.__log.debug('col=%s', col)

            if len(col) != 3:
                continue

            if col[0][0] == '#':
                continue

            [ch, on, off] = [int(s) for s in col]

            self._on[ch] = on
            self._off[ch] = off

        self.__log.debug('on=%s', self._on)
        self.__log.debug('off=%s', self._off)

    def save_conf(self, conf_file=None):
        """ 設定ファイルに保存する

        Parameters
        ----------
        conf_file: str
            設定ファイル名(パス名)
        """
        self.__log.debug('conf_file=%s', conf_file)

        if conf_file is None:
            conf_file = self.conf_file
            self.__log.debug('conf_file=%s', conf_file)

        lines = ['# ch,on,off .. saved by %s' % (__name__)]

        for ch in range(self.servo_n):
            lines.append('%02d,%04d,%04d' % (
                ch, self._on[ch], self._off[ch]))

        with open(conf_file, mode='w') as f:
            f.write('\n'.join(lines) + '\n')

        self.__log.debug('lines=%s', lines)

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
        self.__log.debug('ch=%s, on=%s, pw=%s, tap=%s, conf_file=%s',
                         ch, on, pw, tap, conf_file)

        if pw is None:
            self.__log.debug('pw=%s .. do nothing', pw)
            return

        if conf_file is None:
            conf_file = self.conf_file
            self.__log.debug('[fix] conf_file=%s', conf_file)

        if pw < self.PW_MIN:
            self.__log.debug('[fix] pw=%s', pw)
            pw = self.PW_MIN

        if pw > self.PW_MAX:
            self.__log.debug('[fix] pw=%s', pw)
            pw = self.PW_MAX

        if on:
            self._on[ch] = pw
        else:
            self._off[ch] = pw

        self.save_conf(conf_file)

        if tap:
            self.pull1(ch)
            time.sleep(0.5)
            self.tap1(ch)

    def change_onoff(self, ch, on=False, pw_diff=0, tap=False,
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
        self.__log.debug('ch=%s, on=%s, pw_diff=%s, tap=%s, conf_file=%s',
                         ch, on, pw_diff, tap, conf_file)

        if on:
            pw = self._on[ch]
        else:
            pw = self._off[ch]

        pw += pw_diff

        self.set_onoff(ch, on, pw, tap, conf_file)

    def tap(self, ch_list=[], push_interval=None, pull_interval=None):
        """
        指定された複数のチャンネルのピンをはじく(push and pull)

        Parameters
        ----------
        ch_list: int
            チャンネル番号: 0 .. self.servo_n-1
        push_interval, pull_interval: int
            interval sec
        """
        self.__log.debug('ch_list=%s, push_interval=%s, pull_interval=%s',
                         ch_list, push_interval, pull_interval)

        if len(ch_list) == 0:
            self.__log.warning('ch_list=%s !?', ch_list)
            return

        for ch in ch_list:
            # daemon化しないほうがいい (?)
            threading.Thread(target=self.tap1, args=(
                ch, push_interval, pull_interval),
                daemon=False).start()

    def tap1(self, ch, push_interval=None, pull_interval=None):
        """
        指定されたチャンネルのピンを弾く(push and pull)

        動作中に同じサーボを呼び出された場合は、何もしない(無視する)

        Parameters
        ----------
        ch: int
            チャンネル番号: 0 .. self.servo_n-1
        push_interval, pull_interval: int
            interval sec
        """
        self.__log.debug('ch=%s, interval=%s',
                         ch, (push_interval, pull_interval))

        if self._moving[ch]:
            self.__log.warning('ch[%s]: busy .. ignored', ch)
            return

        self._moving[ch] = True

        if push_interval is None:
            push_interval = self.push_interval
            self.__log.debug('push_interval=%s', push_interval)

        if pull_interval is None:
            pull_interval = self.pull_interval
            self.__log.debug('pull_interval=%s', pull_interval)

        self.push1(ch)
        time.sleep(push_interval)
        self.pull1(ch)
        time.sleep(pull_interval)

        self._moving[ch] = False

        self.__log.debug('ch[%s]: done', ch)

    def push_pull1(self, push_flag, ch):
        """
        指定されたチャンネルのピンを push or pull

        Parameters
        ----------
        push_flag: bool
            true:  push
            false: pull
        ch: int
            チャンネル番号: 0 .. servo_n-1
        """
        self.__log.debug('push_flag=%s, ch=%s', push_flag, ch)
        if ch < 0 or ch >= self.servo_n:
            msg = 'invalid channel number:%s.' % (ch)
            msg += ' specify 0 .. %s' % (self.servo_n - 1)
            raise ValueError(msg)

        pw = self.PW_OFF
        if push_flag:
            pw = self._on[ch]
        else:
            pw = self._off[ch]

        self.__log.debug('pw=%s', pw)
        self._dev.set_pw1(ch, pw)

    def push1(self, ch):
        """
        指定されたチャンネルのピンを押す

        Parameters
        ----------
        ch: int
            チャンネル番号: 0 .. servo_n-1
        """
        self.__log.debug('ch=%s', ch)
        self.push_pull1(True, ch)

    def pull1(self, ch):
        """
        指定されたチャンネルのピンを引く

        Parameters
        ----------
        ch: list of int
            チャンネル番号: 0 .. servo_n-1
        """
        self.__log.debug('ch=%s', ch)
        self.push_pull1(False, ch)

    def push(self, ch_list=[]):
        """
        指定された複数のチャンネルのピンを押す

        Parameters
        ----------
        ch_list: list of int
            チャンネル番号: 0 .. servo_n-1
        """
        self.__log.debug('ch_list=%s', ch_list)

        if len(ch_list) == 0:
            ch_list = list(range(self.servo_n))
            self.__log.debug('ch_list=%s', ch_list)

        for ch in ch_list:
            self.push1(ch)

    def pull(self, ch_list=[]):
        """
        指定された複数のチャンネルのピンを引く

        Parameters
        ----------
        ch_list: list of int
            チャンネル番号: 0 .. servo_n-1
        """
        self.__log.debug('ch_list=%s', ch_list)

        if len(ch_list) == 0:
            ch_list = list(range(self.servo_n))
            self.__log.debug('ch_list=%s', ch_list)

        for ch in ch_list:
            self.pull1(ch)
