#
# (c) 2020 FabLab Kannai
#
"""
Rotation Motor driver for Music Box

### Architecture

 ---------------
| RotationMotor |
|---------------|
|  StepMtrTh    |
|---------------|
|   StepMtr     |
 ---------------

"""
__author__ = 'FabLab Kannai'
__date__   = '2021/01'

from stepmtr import StepMtr, StepMtrTh
from .my_logger import get_logger


class RotationMotor:
    """オルゴール回転モーター
    """
    SPEED2INTERVAL = (None,
                      0.5,
                      0.25,
                      0.125,
                      0.06,
                      0.03,
                      0.015,
                      0.008,
                      0.004,
                      0.002,
                      0.0015)

    def __init__(self, pin1, pin2, pin3, pin4, debug=False):
        """ Constructor

        Parameters
        ----------
        pin1, pin2, pin3, pin4: int
            GPIOピン番号
        """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s', (pin1, pin2, pin3, pin4))

        self.sm_th = StepMtrTh(pin1, pin2, pin3, pin4,
                               seq=StepMtr.SEQ_FULL,
                               interval=StepMtr.DEF_INTERVAL,
                               count=0,
                               direction=StepMtr.CCW,
                               debug=self._dbg)

    def start(self):
        """スタート
        """
        self._log.debug('')
        self.sm_th.set_count(-1)

    def stop(self):
        """ストップ
        """
        self._log.debug('')
        self.sm_th.stop()

    def set_speed(self, speed):
        """スピード変更

        Parameters
        ----------
        speed: int
            速度  0:ストップ, 10:最速
        """
        self._log.debug('speed=%s', speed)

        interval = self.SPEED2INTERVAL[speed]

        if interval is None:
            self.sm_th.stop()
            return

        self.sm_th.set_interval(interval)
        self.start()

    def end(self):
        """終了処理

        プログラム終了時に呼ぶこと
        """
        self._log.debug('')
        self.sm_th.end()


"""
以下、サンプル・コード
"""


class Sample:
    """サンプル
    """
    def __init__(self, pin1, pin2, pin3, pin4, debug=False):
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s', (pin1, pin2, pin3, pin4))

        self.mtr = MusicBoxRotationMotor(pin1, pin2, pin3, pin4,
                                         debug=self._dbg)

    def main(self):
        self._log.debug('')

        self.mtr.set_speed(1)

        while True:
            prompt = '[0 <= speed <= 10 | NULL:end] '
            try:
                line1 = input(prompt)
            except Exception as e:
                self._log.error('%s:%s', type(e), e)
                continue
            self._log.debug('line1=%a', line1)

            if len(line1) == 0:
                # end
                break

            try:
                speed = int(line1)
            except Exception:
                self._log.error('invalid speed: %a', line1)
                continue
            self._log.debug('speed=%s', speed)

            if speed < 0 or speed > 10:
                self._log.error('invalid speed: %s', speed)
                continue

            self.mtr.set_speed(speed)

    def end(self):
        self._log.debug('')
        self.mtr.end()
