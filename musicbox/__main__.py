#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for musicbox package
"""
import json
import click
import cuilib
from . import Midi, RotationMotor, Servo
from . import Movement, MovementWav1, MovementWav2, MovementWav3
from . import Player, WsServer
from .my_logger import get_logger

__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'


class MidiApp:
    """ MidiApp """
    def __init__(self, midi_file, destination=(), channel=[],
                 debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s, channel=%s',
                         midi_file, channel)
        self.__log.debug('destination=%s', destination)

        self._midi_file = midi_file
        self._destination = destination
        self._channel = channel

        self._parser = Midi(debug=self._dbg)

    def main(self) -> None:
        """ main """
        self.__log.debug('')

        music_data = self._parser.parse(self._midi_file, self._channel)

        for dst in self._destination:
            if dst.startswith('ws:/'):
                self._parser.send_music(music_data, dst)
                continue
            
            with open(dst, mode='w') as f:
                json.dump(music_data, f, indent=4)


class RotationMotorApp:
    """ RotationMotorApp """
    def __init__(self, pin1, pin2, pin3, pin4, debug=False):
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('pins=%s', (pin1, pin2, pin3, pin4))

        self.mtr = RotationMotor(pin1, pin2, pin3, pin4,
                                 debug=self._dbg)

    def main(self):
        """ main """
        self.__log.debug('')

        self.mtr.set_speed(1)

        while True:
            prompt = '[0 <= speed <= 10 | NULL:end] '
            try:
                line1 = input(prompt)
            except EOFError:
                print('<EOF>')
                break
            except Exception as ex:
                self.__log.error('%s:%s', type(ex), ex)
                continue
            self.__log.debug('line1=%a', line1)

            if len(line1) == 0:
                # end
                break

            try:
                speed = int(line1)
            except Exception:
                self.__log.error('invalid speed: %a', line1)
                continue
            self.__log.debug('speed=%s', speed)

            if speed < 0 or speed > 10:
                self.__log.error('invalid speed: %s', speed)
                continue

            self.mtr.set_speed(speed)

    def end(self):
        """ end """
        self.__log.debug('')
        self.mtr.end()


class ServoMotorApp:
    """ ServoMotorApp """

    SERVO_KEY = '12345678qwertyu'
    QUIT_KEY = ['KEY_ESCAPE', 'KEY_ENTER', '\x04']

    def __init__(self, push_interval, pull_interval, debug=False):
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('push/pull_interval=%s',
                         (push_interval, pull_interval))

        self._servo = Servo(push_interval=push_interval,
                            pull_interval=pull_interval,
                            debug=self._dbg)

        self._cui = cuilib.Cui(debug=self._dbg)

        self._cui.add(self.SERVO_KEY, self.tap, 'tap')
        self._cui.add(self.QUIT_KEY, self.quit, 'quit')

    def tap(self, key_sym):
        """
        tap
        """
        self.__log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)
        print('ch=%s' % (ch))

        self._servo.tap([ch])

    def quit(self, key_sym):
        """ quit """
        self.__log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self.__log.debug('')

        self._cui.start()
        print('*** Start ***')
        print('%s to quit' % (self.QUIT_KEY))

        self._cui.join()

    def end(self):
        """ end """
        self.__log.debug('')
        self._servo.end()


class MovementApp:
    """ MovementApp """

    SERVO_KEY = '12345678qwertyu'
    QUIT_KEY = ['KEY_ESCAPE', 'KEY_ENTER', '\x04']

    def __init__(self, wav_mode,
                 rotation_speed,
                 push_interval, pull_interval,
                 debug=False):
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('wav_mode=%s', wav_mode)
        self.__log.debug('rotation_speed=%s', rotation_speed)
        self.__log.debug('push/pull_interval=%s',
                         (push_interval, pull_interval))

        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed

        if self._wav_mode == 1:
            self._movement = MovementWav1(debug=self._dbg)

        elif self._wav_mode == 2:
            self._movement = MovementWav2(debug=self._dbg)

        elif self._wav_mode == 3:
            self._movement = MovementWav3(debug=self._dbg)

        else:
            self._movement = Movement(rotation_speed=rotation_speed,
                                      push_interval=push_interval,
                                      pull_interval=pull_interval,
                                      debug=self._dbg)

        self._cui = cuilib.Cui(debug=self._dbg)

        self._cui.add(self.SERVO_KEY, self.single_play, 'single_play')
        self._cui.add(self.QUIT_KEY, self.quit, 'quit')

    def single_play(self, key_sym):
        """
        single_play
        """
        self.__log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)

        if self._wav_mode == 2:
            ch += 48
        if self._wav_mode == 3:
            ch += 60

        print('ch=%s' % (ch))

        self._movement.single_play([ch])

    def quit(self, key_sym):
        """ quit """
        self.__log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self.__log.debug('')

        self._movement.rotation_speed(self._rotation_speed)

        self._cui.start()
        print('*** Start ***')
        print('%s to quit' % (self.QUIT_KEY))

        self._cui.join()

    def end(self):
        """ end """
        self.__log.debug('')
        self._movement.end()


class PlayerApp:
    """ PlayerApp """

    SERVO_KEY = '12345678qwertyu'
    QUIT_KEY = ['KEY_ESCAPE', 'KEY_ENTER', '\x04']

    NOTE_BASE = {
        Player.WAVMODE_NONE: -1,
        Player.WAVMODE_PIANO: -1,
        Player.WAVMODE_PIANO_FULL: 21,
        Player.WAVMODE_MIDI_FULL: 0
    }

    NOTE_N = {
        Player.WAVMODE_NONE: -1,
        Player.WAVMODE_PIANO: -1,
        Player.WAVMODE_PIANO_FULL: 88,
        Player.WAVMODE_MIDI_FULL: 128
    }

    def __init__(self, music_file, channel,
                 wav_mode,
                 rotation_speed,
                 push_interval, pull_interval,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        music_file: list of str
        channel: list of int
        wav_mode: int
        rotation_speed: int
        push_interval, pull_interval: float

        """
        self._dbg = debug
        self.__log = get_logger(__class__.__name__, self._dbg)
        self.__log.debug('wav_mode=%s', wav_mode)
        self.__log.debug('music_file=%s, channel=%s',
                         music_file, channel)
        self.__log.debug('channel=%s', channel)
        self.__log.debug('rotation_speed=%s', rotation_speed)
        self.__log.debug('push/pull_interval=%s',
                         (push_interval, pull_interval))

        self._wav_mode = wav_mode
        self._music_file = music_file
        self._channel = channel
        self._rotation_speed = rotation_speed

        self._note_n = self.NOTE_N[self._wav_mode]
        self.__log.debug('note_n=%s', self._note_n)

        self._parser = Midi(debug=self._dbg)

        self._player = Player(self._wav_mode,
                              self._rotation_speed, debug=self._dbg)

        self._cui = cuilib.Cui(debug=self._dbg)

        self._cui.add(self.SERVO_KEY, self.single_play, 'single_play')
        self._cui.add(self.QUIT_KEY, self.quit, 'quit')

    def single_play(self, key_sym):
        """
        single_play
        """
        self.__log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)

        if self._wav_mode == Player.WAVMODE_PIANO_FULL:
            ch += 48
        if self._wav_mode == Player.WAVMODE_MIDI_FULL:
            ch += 60

        print('ch=%s' % (ch))

        self._player.single_play([ch])

    def quit(self, key_sym):
        """ quit """
        self.__log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self.__log.debug('')

        self._player.rotation_speed(self._rotation_speed)

        if self._music_file:
            music_data = self._parser.parse(
                self._music_file[0],
                self._channel,
                self.NOTE_BASE[self._wav_mode],
                self.NOTE_N[self._wav_mode])

            self._player.music_load(music_data)

        self._cui.start()
        print('*** Start ***')
        print('%s to quit' % (self.QUIT_KEY))

        self._cui.join()

    def end(self):
        """ end """
        self.__log.debug('')
        self._player.end()


class WsServerApp:
    """ Music Box Websocket Server App """
    def __init__(self, port, wav_mode, debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
        wav_mode: int
        """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)

        self._port = port
        self._wav_mode = wav_mode

        self._svr = WsServer(wav_mode=self._wav_mode,
                             port=self._port, debug=self._dbg)

    def main(self):
        """ main """
        self.__log.debug('start')

        self._svr.main()

        self.__log.debug('done')

    def end(self):
        """ end: Call at the end of usage """
        self.__log.debug('doing ..')

        self._svr.end()

        self.__log.debug('done')


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help='''
Music Box Apps and Tests
''')
@click.pass_context
def cli(ctx):
    """ click group """
    subcmd = ctx.invoked_subcommand

    if subcmd is None:
        print()
        print('Please specify subcommand')
        print()
        print(ctx.get_help())
    else:
        print('==========')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
MIDI parser

  DESTINATION: file name or websock URL
""")
@click.argument('midi_file', type=click.Path(exists=True))
@click.argument('destination', type=str, nargs=-1)
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def midi(midi_file, destination, channel, dbg) -> None:
    """ parser main """
    log = get_logger(__name__, dbg)

    app = MidiApp(midi_file, destination, channel, debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
Rotation motor test
""")
@click.argument('pin1', type=int)
@click.argument('pin2', type=int)
@click.argument('pin3', type=int)
@click.argument('pin4', type=int)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def rotation(pin1, pin2, pin3, pin4, debug):
    """ rotation_motor """
    log = get_logger(__name__, debug)
    log.debug('pins=%s', (pin1, pin2, pin3, pin4))

    app = RotationMotorApp(pin1, pin2, pin3, pin4, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
Servo motor test
""")
@click.option('--push', '-p', 'push_interval', type=float,
              default=Servo.DEF_PUSH_INTERVAL,
              help='push interaval, default=%s sec' % (
                  Servo.DEF_PUSH_INTERVAL))
@click.option('--pull', '-P', 'pull_interval', type=float,
              default=Servo.DEF_PULL_INTERVAL,
              help='pull interaval, default=%s sec' % (
                  Servo.DEF_PULL_INTERVAL))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def servo(push_interval, pull_interval, debug):
    """ servo_motor """
    log = get_logger(__name__, debug)

    app = ServoMotorApp(push_interval, pull_interval, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
Movement test
""")
@click.option('--wav_mode', '-w', 'wav_mode', type=int,
              default=0,
              help='Wav file mode')
@click.option('--speed', '-s', 'speed', type=int,
              default=Movement.ROTATION_SPEED,
              help='rotation speed')
@click.option('--push', '-p', 'push_interval', type=float,
              default=Servo.DEF_PUSH_INTERVAL,
              help='push interaval, default=%s sec' % (
                  Servo.DEF_PUSH_INTERVAL))
@click.option('--pull', '-P', 'pull_interval', type=float,
              default=Servo.DEF_PULL_INTERVAL,
              help='pull interaval, default=%s sec' % (
                  Servo.DEF_PULL_INTERVAL))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def movement(wav_mode, push_interval, pull_interval, speed, debug):
    """ movement """
    log = get_logger(__name__, debug)

    app = MovementApp(wav_mode, speed,
                      push_interval, pull_interval, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
Player test
""")
@click.argument('music_file', type=click.Path(exists=True), nargs=-1)
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--wav_mode', '-w', 'wav_mode', type=int,
              default=0,
              help='Wav file mode')
@click.option('--speed', '-s', 'speed', type=int,
              default=Player.ROTATION_SPEED,
              help='rotation speed')
@click.option('--push', '-p', 'push_interval', type=float,
              default=Servo.DEF_PUSH_INTERVAL,
              help='push interaval, default=%s sec' % (
                  Servo.DEF_PUSH_INTERVAL))
@click.option('--pull', '-P', 'pull_interval', type=float,
              default=Servo.DEF_PULL_INTERVAL,
              help='pull interaval, default=%s sec' % (
                  Servo.DEF_PULL_INTERVAL))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def player(music_file, channel, wav_mode,
           speed, push_interval, pull_interval, debug):
    """ player """
    log = get_logger(__name__, debug)

    app = PlayerApp(music_file, channel, wav_mode, speed,
                    push_interval, pull_interval, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
Music Box Websocket Server
""")
@click.option('--port', '-p', 'port', type=int,
              default=WsServer.DEF_PORT,
              help='port number, default=%s' % (
                  WsServer.DEF_PORT))
@click.option('--wav_mode', '-w', 'wav_mode', type=int,
              default=Player.WAVMODE_NONE,
              help='Wav file mode, default=%s' % (
                  Player.WAVMODE_NONE))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def wsserver(port, wav_mode, debug):
    """ wsserver """
    log = get_logger(__name__, debug)

    app = WsServerApp(port, wav_mode, debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


if __name__ == '__main__':
    cli(prog_name='python3 -m musicbox')  # pylint: disable=no-value-for-parameter
