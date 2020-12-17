#!/usr/bin/env python3
#
# (c) 2020 FabLab Kannai
#
"""
Rotation Motor driver for Music Box


### Simple Usage (1): single thread
------------------------------------------------------------
from MusicBoxServo import MusicBoxServo
 :
servo = MusicBoxServo()
 :
servo.tap([0, 2, 4])  # list of channel numbers
 :
servo.end()
------------------------------------------------------------
"""
__author__ = 'FabLab Kannai'
__date__   = '2020/12'

import pigpio
import time
import threading
from ServoPCA9685 import ServoPCA9685
from MyLogger import get_logger


class MusicBoxServo:
    """
    Servo Motor for Music Box

    Attributes
    ----------
    servo_n: int
        number of servo motors
    """
    __log = get_logger(__name__, False)

    DEF_CONF_FNAME = "music-box-servo.conf"
    DEF_CONF_DIR = "/home/pi"
    DEF_CONFFILE = DEF_CONF_DIR + '/' + DEF_CONF_FNAME

    DEF_PUSH_INTERVAL = 0.2  # sec
    DEF_PULL_INTERVAL = 0.2  # sec

    DEF_SERVO_N = 15

    PW_CENTER = 1500
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
        push_interval: float
            ON interval (sec)
        pull_interval: float
            OFF interval (sec)
        servo_n: int
            number of servo motors
        """
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('conf_file=%s' % conf_file)
        self.__log.debug('push_interval=%s, pull_interval=%s',
                         push_interval, pull_interval)
        self.__log.debug('servo_n=%s', servo_n)

        self.conf_file = conf_file
        self.push_interval = push_interval
        self.pull_interval = pull_interval
        self.servo_n = servo_n

        self.pi = pigpio.pi()

        self.on = [self.PW_CENTER] * self.servo_n
        self.off = [self.PW_CENTER] * self.servo_n
        self.moving = [False] * self.servo_n
        self.__log.debug('on=%s', self.on)
        self.__log.debug('off=%s', self.off)
        self.__log.debug('moving=%s', self.moving)

        self.load_conf(self.conf_file)

        self.dev = ServoPCA9685(list(range(self.servo_n)), self.pi,
                                  debug=self._dbg)
        self.pull(list(range(self.servo_n)))

    def end(self):
        """終了処理

        プログラム終了時に呼ぶこと
        """
        self.__log.debug('doing ..')
        time.sleep(0.5)
        self.dev.end()
        time.sleep(0.5)
        self.pi.stop()
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

            self.on[ch] = on
            self.off[ch] = off

        self.__log.debug('on=%s', self.on)
        self.__log.debug('off=%s', self.off)

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
            ch_list = list(range(self.servo_n))
            self.__log.debug('ch_list=%s', ch_list)

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

        if self.moving[ch]:
            self.__log.warning('ch[%s]: busy .. skipped', ch)
            return

        self.moving[ch] = True

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

        self.moving[ch] = False

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
            pw = self.on[ch]
        else:
            pw = self.off[ch]

        self.__log.debug('pw=%s', pw)
        self.dev.set_pw1(ch, pw)

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


""" 以下、サンプル・コード """


class Sample:
    """サンプル
    """
    __log = get_logger(__name__, False)

    def __init__(self, conf_file,
                 push_interval, pull_interval,
                 servo_n,
                 debug=False):
        self._dbg = debug
        __class__.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('conf_file=%s', conf_file)
        self.__log.debug('push_interval=%s, off_interaval=%s',
                         push_interval, pull_interval)
        self.__log.debug('servo_n=%s', servo_n)

        self.servo = MusicBoxServo(conf_file, push_interval, pull_interval,
                                   servo_n,
                                   debug=self._dbg)

    def main(self):
        self.__log.debug('')

        prompt = '[0-%s ..|sleep sec]> ' % (self.servo.servo_n - 1)

        while True:
            try:
                line1 = input(prompt)
            except EOFError:
                self.__log.info('EOF')
                break
            except Exception as ex:
                self.__log.error('%s:%s', type(ex), ex)
                continue
            self.__log.debug('line1=%a', line1)

            if len(line1) == 0:
                continue

            ch_str = line1.split()
            self.__log.debug('ch_str=%s', ch_str)

            if ch_str[0] in ('sleep', 's'):
                try:
                    sleep_sec = float(ch_str[1])
                except ValueError as ex:
                    self.__log.error('%s: %s: Invalid sleep_sec',
                                     type(ex).__name__, ex)
                    continue
                except IndexError:
                    self.__log.error('specify sleep_sec')
                    continue

                try:
                    time.sleep(sleep_sec)
                except ValueError as ex:
                    self.__log.error('%s: %s', type(ex).__name__, ex)

                continue

            try:
                ch = [int(s) for s in ch_str]
            except Exception as ex:
                self.__log.error('%s: %s .. ignored', type(ex), ex)
                continue

            self.__log.debug('ch=%s', ch)

            try:
                self.servo.tap(ch)
            except ValueError as ex:
                self.__log.error("%s: %s .. ignored", type(ex), ex)

    def end(self):
        self.__log.debug('')
        self.servo.end()


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help="""
MusicBoxServo class test program
""")
@click.option('--conf', '-f', '-c', 'conf_file',
              type=click.Path(exists=True),
              default=MusicBoxServo.DEF_CONFFILE,
              help='configuration file')
@click.option('--push_interval', '-p', 'push_interval', type=float,
              default=MusicBoxServo.DEF_PUSH_INTERVAL,
              help='on interval[sec]')
@click.option('--pull_interval', '-P', 'pull_interval', type=float,
              default=MusicBoxServo.DEF_PULL_INTERVAL,
              help='off interval[sec]')
@click.option('--servo_n', '-s', 'servo_n', type=int,
              default=MusicBoxServo.DEF_SERVO_N,
              help='number of servo')
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(conf_file, push_interval, pull_interval, servo_n, debug):
    """ サンプル起動用メイン関数
    """
    log = get_logger(__name__, debug)
    log.debug('conf_file=%s', conf_file)
    log.debug('push_interval=%s, pull_interval=%s',
              push_interval, pull_interval)
    log.debug('servo_n=%s', servo_n)

    app = Sample(conf_file, push_interval, pull_interval,
                 servo_n, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


if __name__ == '__main__':
    main()
