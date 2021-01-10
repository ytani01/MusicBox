#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for musicbox package
"""
import os
import json
import click
import cuilib
from . import PaperTape, Midi, RotationMotor, Servo
from . import Movement, MovementWav1, MovementWav2, MovementWav3, Player
from . import WsServer, WsClient, WsClientHostPort, WebServer
from .my_logger import get_logger

__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

DEF_WS_HOST = 'localhost'
DEF_WS_PORT = WsServer.DEF_PORT
DEF_WS_URL = 'ws://%s:%s/' % (DEF_WS_HOST, DEF_WS_PORT)

DEF_WAV_DIR = os.environ.get('MUSICBOX_WAV_DIR', './wav')

DEF_WEB_DIR = os.environ.get('MUSICBOX_WEB_DIR', './web-root')
DEF_WEB_PORT = WebServer.DEF_PORT

DEF_UPLOAD_DIR = os.environ.get('MUSICBOX_UPLOAD_DIR', '/tmp')
DEF_MUSICDATA_DIR = os.environ.get('MUSICBOX_MUSICDATA_DIR', '/tmp')


class PaperTapeApp:
    """ PaperTapeApp """
    def __init__(self, paper_tape_file, dst=(), debug=False) -> None:
        """ Constructor

        Parameters
        ----------
        paper_tape_file: str
        dst: str
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        self._paper_tape_file = paper_tape_file
        self._dst = dst

        self._parser = PaperTape(debug=self._dbg)

    def main(self):
        """ main """
        self._log.debug('')

        music_data = self._parser.parse(self._paper_tape_file)

        for dst in self._dst:
            print()
            if ':/' in dst:
                print('send music_data[%s] to %s' % (
                    len(music_data), dst))
                WsClient(dst).send_music(music_data)
                continue

            print('save music_data[%s] to %s' % (
                len(music_data), dst))
            with open(dst, mode='w') as f:
                json.dump(music_data, f, indent=4)

        print()


class MidiApp:
    """ MidiApp """
    def __init__(self, midi_file, dst=(), channel=[],
                 note_origin=-1, no_note_offset_flag=False,
                 wav_mode=0,
                 debug=False) -> None:
        """ Constructor

        Parameters
        ----------
        midi_file: str
        dst: str
        channel: list of int
        note_origin: int
        no_note_offset_flag: bool
        wav_mode: int
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('midi_file=%s, channel=%s',
                        midi_file, channel)
        self._log.debug('dst=%s', dst)
        self._log.debug('note_origin=%s', note_origin)
        self._log.debug('no_note_offset_flag=%s', no_note_offset_flag)
        self._log.debug('wav_mode=%s', wav_mode)

        self._midi_file = midi_file
        self._dst = dst
        self._channel = channel
        self._note_origin = note_origin

        self._note_offset = Midi.NOTE_OFFSET
        if no_note_offset_flag:
            self._note_offset = []

        if wav_mode in (2, 3):
            self._note_origin = 0
            self._note_offset = []
            self._log.debug('[fix] note_origin=%s, note_offset=%s',
                            self._note_origin, self._note_offset)

        self._parser = Midi(debug=self._dbg)

    def main(self) -> None:
        """ main """
        self._log.debug('')

        music_data = self._parser.parse(
            self._midi_file, self._channel,
            self._note_origin, self._note_offset)

        for dst in self._dst:
            print()
            if ':/' in dst:
                print('send music_data[%s] to %s' % (
                    len(music_data), dst))
                WsClient(dst).send_music(music_data)
                continue

            print('save music_data[%s] to %s' % (
                len(music_data), dst))
            with open(dst, mode='w') as f:
                json.dump(music_data, f, indent=4)

        print()


class RotationMotorApp:
    """ RotationMotorApp """
    def __init__(self, pin1, pin2, pin3, pin4, debug=False):
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('pins=%s', (pin1, pin2, pin3, pin4))

        self.mtr = RotationMotor(pin1, pin2, pin3, pin4,
                                 debug=self._dbg)

    def main(self):
        """ main """
        self._log.debug('')

        self.mtr.set_speed(1)

        while True:
            prompt = '[0 <= speed <= 10 | NULL:end] '
            try:
                line1 = input(prompt)
            except EOFError:
                print('<EOF>')
                break
            except Exception as ex:
                self._log.error('%s:%s', type(ex), ex)
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
        """ end """
        self._log.debug('')
        self.mtr.end()


class ServoMotorApp:
    """ ServoMotorApp """

    SERVO_KEY = '12345678qwertyu'
    QUIT_KEY = ['KEY_ESCAPE', 'KEY_ENTER', '\x04']

    def __init__(self, push_interval, pull_interval, debug=False):
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('push/pull_interval=%s',
                        (push_interval, pull_interval))

        self._servo = Servo(push_interval=push_interval,
                            pull_interval=pull_interval,
                            debug=self._dbg)

        self._cui = cuilib.Cui(debug=self._dbg)

        self._cui.add(self.SERVO_KEY, self.tap, 'tap')
        self._cui.add(self.QUIT_KEY, self.quit, 'quit')

    def tap(self, key_sym):
        """ tap """
        self._log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)
        print('ch=%s' % (ch))

        self._servo.tap([ch])

    def quit(self, key_sym):
        """ quit """
        self._log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self._log.debug('')

        self._cui.start()
        print('*** Start ***')
        print('%s to quit' % (self.QUIT_KEY))

        self._cui.join()

    def end(self):
        """ end """
        self._log.debug('')
        self._servo.end()


class MovementApp:
    """ MovementApp """

    SERVO_KEY = '12345678qwertyu'
    QUIT_KEY = ['KEY_ESCAPE', 'KEY_ENTER', '\x04']

    def __init__(self, wav_mode,
                 rotation_speed,
                 push_interval, pull_interval,
                 wavdir,
                 debug=False):
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('rotation_speed=%s', rotation_speed)
        self._log.debug('push/pull_interval=%s',
                        (push_interval, pull_interval))
        self._log.debug('wavdir=%s', wavdir)

        self._wav_mode = wav_mode
        self._rotation_speed = rotation_speed

        if self._wav_mode == 1:
            self._movement = MovementWav1(wav_topdir=wavdir,
                                          debug=self._dbg)

        elif self._wav_mode == 2:
            self._movement = MovementWav2(wav_topdir=wavdir,
                                          debug=self._dbg)

        elif self._wav_mode == 3:
            self._movement = MovementWav3(wav_topdir=wavdir,
                                          debug=self._dbg)

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
        self._log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)

        if self._wav_mode == 2:
            ch += 48
        if self._wav_mode == 3:
            ch += 60

        print('ch=%s' % (ch))

        self._movement.single_play([ch])

    def quit(self, key_sym):
        """ quit """
        self._log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self._log.debug('')

        self._movement.rotation_speed(self._rotation_speed)

        self._cui.start()
        print('*** Start ***')
        print('%s to quit' % (self.QUIT_KEY))

        self._cui.join()

    def end(self):
        """ end """
        self._log.debug('')
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
                 wavdir,
                 debug=False):
        """ Constructor

        Parameters
        ----------
        music_file: list of str
        channel: list of int
        wav_mode: int
        rotation_speed: int
        push_interval, pull_interval: float
        wavdir: str
        """
        self._dbg = debug
        self._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('wav_mode=%s', wav_mode)
        self._log.debug('music_file=%s, channel=%s',
                        music_file, channel)
        self._log.debug('channel=%s', channel)
        self._log.debug('rotation_speed=%s', rotation_speed)
        self._log.debug('push/pull_interval=%s',
                        (push_interval, pull_interval))
        self._log.debug('wavdir=%s', wavdir)

        self._wav_mode = wav_mode
        self._music_file = music_file
        self._channel = channel
        self._rotation_speed = rotation_speed
        self._wavdir = wavdir

        self._note_n = self.NOTE_N[self._wav_mode]
        self._log.debug('note_n=%s', self._note_n)

        self._parser = Midi(debug=self._dbg)

        self._player = Player(self._wav_mode,
                              self._rotation_speed,
                              wavdir=self._wavdir,
                              debug=self._dbg)

        self._cui = cuilib.Cui(debug=self._dbg)

        self._cui.add(self.SERVO_KEY, self.single_play, 'single_play')
        self._cui.add(self.QUIT_KEY, self.quit, 'quit')

    def single_play(self, key_sym):
        """
        single_play
        """
        self._log.debug('keysym=%s', key_sym)

        ch = self.SERVO_KEY.index(key_sym)

        if self._wav_mode == Player.WAVMODE_PIANO_FULL:
            ch += 48
        if self._wav_mode == Player.WAVMODE_MIDI_FULL:
            ch += 60

        print('ch=%s' % (ch))

        self._player.single_play([ch])

    def quit(self, key_sym):
        """ quit """
        self._log.debug('keysym=%s', key_sym)
        print('*** Quit ***')
        self._cui.end()

    def main(self):
        """ main """
        self._log.debug('')

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
        self._log.debug('')
        self._player.end()


class WsServerApp:
    """ Music Box Websocket Server App """
    def __init__(self, port, wav_mode, wavdir, debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
        wav_mode: int
        wavdir: str
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        self._port = port
        self._wav_mode = wav_mode
        self._wavdir = wavdir

        self._svr = WsServer(wav_mode=self._wav_mode,
                             port=self._port, wavdir=self._wavdir,
                             debug=self._dbg)

    def main(self):
        """ main """
        self._log.debug('start')

        self._svr.main()

        self._log.debug('done')

    def end(self):
        """ end: Call at the end of usage """
        self._log.debug('doing ..')

        self._svr.end()

        self._log.debug('done')


class WsCmdApp:
    """ Music Box Websocket Client App for simple command"""
    def __init__(self, server_host, server_port, cmd, debug=False):
        """ Constructor

        Parameters
        ----------
        server_host: str
        server_port: int
        cmd: str
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('server_host:server_port=%s:%s',
                        server_host, server_port)
        self._log.debug('cmd=%s', cmd)

        self._server_host = server_host
        self._server_port = server_port
        self._cmd = cmd

        self._client = WsClientHostPort(self._server_host,
                                        self._server_port,
                                        debug=self._dbg)

    def main(self):
        """ main """
        if not self._cmd:
            print('no command !?')
            return

        cmd_name = self._cmd[0]

        msg = {'cmd': cmd_name}

        if cmd_name == 'single_play':
            msg['ch'] = [int(ch) for ch in self._cmd[1:]]
            self._client.send(msg)
            return

        if cmd_name == 'music_load':
            music_data_file = self._cmd[1]
            self._client.send_music_file(music_data_file)
            return

        if cmd_name == 'music_seek':
            msg['pos'] = float(self._cmd[1])
            self._log.debug('msg=%s', msg)
            self._client.send(msg)

        self._client.send(msg)


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help="""
Music Box Apps and Tests command
""")
@click.pass_context
def cli(ctx):
    """ command group """
    subcmd = ctx.invoked_subcommand

    if subcmd is None:
        print(ctx.get_help())


@cli.command(help="""
Paper Tape Text format parser
(send music_data to Music Box Server and/or save music_data to file)
""")
@click.argument('paper_tape_file', type=click.Path(exists=True))
@click.argument('out_file_or_ws_url', type=str, nargs=-1)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def ptt(paper_tape_file, out_file_or_ws_url, debug):
    """ papertape """
    log = get_logger(__name__, debug)

    app = PaperTapeApp(paper_tape_file, out_file_or_ws_url,
                       debug)
    try:
        app.main()
    finally:
        log.debug('done')


@cli.command(help="""
MIDI parser
(send music_data to Music Box Server and/or save music_data to file)
""")
@click.argument('midi_file', type=click.Path(exists=True))
@click.argument('out_file_or_ws_url', type=str, nargs=-1)
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--note_origin', '--origin', '-o', 'note_origin',
              type=int, default=-1,
              help='Note origin, default=-1')
@click.option('--no_note_offset', '-n', 'no_note_offset_flag',
              is_flag=True, default=False,
              help='No note offset flag, default=False(use offset)')
@click.option('--wav_mode', '-w', 'wav_mode', type=int, default=0,
              help="""Wav file mode, default=0\n
0: Real Music Box\n
1: Simulate Music Box with wav file\n
2: Piano sound (note: 21 .. 108)\n
3: Full notes""")
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def midi(midi_file, out_file_or_ws_url, channel,
         note_origin, no_note_offset_flag,
         wav_mode,
         dbg) -> None:
    """ midi """
    log = get_logger(__name__, dbg)

    app = MidiApp(midi_file, out_file_or_ws_url, channel,
                  note_origin, no_note_offset_flag,
                  wav_mode, debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')


@cli.command(help="""
Test Rotation motor
""")
@click.argument('pin1', type=int)
@click.argument('pin2', type=int)
@click.argument('pin3', type=int)
@click.argument('pin4', type=int)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def z_rotation(pin1, pin2, pin3, pin4, debug):
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


@cli.command(help="""
Test Servo motors
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
def z_servo(push_interval, pull_interval, debug):
    """ servo_motor """
    log = get_logger(__name__, debug)

    app = ServoMotorApp(push_interval, pull_interval, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(help="""
Test Movement
""")
@click.option('--wav_mode', '-w', 'wav_mode', type=int, default=0,
              help="""Wav file mode, default=0\n
0: Real Music Box\n
1: Simulate Music Box with wav file\n
2: Piano sound (note: 21 .. 108)\n
3: Full notes""")
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
@click.option('--wavdir', '-D', 'wavdir', type=click.Path(exists=True),
              default=DEF_WAV_DIR,
              help='wav file directory, default=%a' % DEF_WAV_DIR)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def z_movement(wav_mode, push_interval, pull_interval, speed,
               wavdir, debug):
    """ movement """
    log = get_logger(__name__, debug)

    app = MovementApp(wav_mode, speed,
                      push_interval, pull_interval, wavdir, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(help="""
Test Player
""")
@click.argument('music_file', type=click.Path(exists=True), nargs=-1)
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--wav_mode', '-w', 'wav_mode', type=int, default=0,
              help="""Wav file mode, default=0\n
0: Real Music Box\n
1: Simulate Music Box with wav file\n
2: Piano sound (note: 21 .. 108)\n
3: Full notes""")
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
@click.option('--wavdir', '-D', 'wavdir', type=click.Path(exists=True),
              default=DEF_WAV_DIR,
              help='wav file directory, default=%a' % DEF_WAV_DIR)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def z_player(music_file, channel, wav_mode,
             speed, push_interval, pull_interval, wavdir, debug):
    """ player """
    log = get_logger(__name__, debug)

    app = PlayerApp(music_file, channel, wav_mode, speed,
                    push_interval, pull_interval, wavdir, debug=debug)

    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(help="""
Music Box Server
""")
@click.option('--port', '-p', 'port', type=int,
              default=WsServer.DEF_PORT,
              help='port number, default=%s' % (
                  WsServer.DEF_PORT))
@click.option('--wav_mode', '-w', 'wav_mode', type=int, default=0,
              help="""Wav file mode, default=0\n
0: Real Music Box\n
1: Simulate Music Box with wav file\n
2: Piano sound (note: 21 .. 108)\n
3: Full notes""")
@click.option('--wavdir', '-D', 'wavdir', type=click.Path(exists=True),
              default=DEF_WAV_DIR,
              help='wav file directory, default=%a' % DEF_WAV_DIR)
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def server(port, wav_mode, wavdir, debug):
    """ websocket server """
    log = get_logger(__name__, debug)

    app = WsServerApp(port, wav_mode, wavdir, debug=debug)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()
        log.info('end')


@cli.command(help="""
Send a command to Music Box Server

ex. `music_play`, `single_play 0 2 4`, etc ...
""")
@click.argument('cmd', type=str, nargs=-1)
@click.option('--server', '-s', 'server_host', type=str,
              default=DEF_WS_HOST,
              help='%s, default=%s' % (
                  'hostname or IP address of Music Box server',
                  DEF_WS_HOST))
@click.option('--port', '-p', 'server_port', type=int,
              default=DEF_WS_PORT,
              help='port number of Music Box server, default=%s' % (
                  DEF_WS_PORT))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def send(cmd, server_host, server_port, debug):
    """ send a cmd to server """
    log = get_logger(__name__, debug)

    app = WsCmdApp(server_host, server_port, cmd, debug=debug)
    try:
        app.main()
    finally:
        log.debug('done')


@cli.command(help="""
Web application
""")
@click.option('--port', '-p', 'port', type=int,
              default=WebServer.DEF_PORT,
              help='port number, default=%s' % (
                  WebServer.DEF_PORT))
@click.option('--webdir', '-w', 'webdir', type=click.Path(exists=True),
              default=DEF_WEB_DIR,
              help='Web directory, default=%a' % (DEF_WEB_DIR))
@click.option('--upload_dir', '-u', 'upload_dir',
              type=click.Path(exists=True), default=DEF_UPLOAD_DIR,
              help='upload files directory, default=%a' % (
                  DEF_UPLOAD_DIR))
@click.option('--data_dir', '-D', 'data_dir',
              type=click.Path(exists=True), default=DEF_MUSICDATA_DIR,
              help='parsed files directory, default=%a' % (
                  DEF_MUSICDATA_DIR))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def webapp(port, webdir, upload_dir, data_dir, debug):
    """ webapp """
    log = get_logger(__name__, debug)

    app = WebServer(port, webdir, upload_dir, data_dir, debug=debug)
    try:
        app.main()
    finally:
        log.debug('done')


if __name__ == '__main__':
    cli(prog_name='MusicBox')
