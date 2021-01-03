#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for midi_tools
"""
import json
import click
from . import Parser, RotationMotor
from .my_logger import get_logger

__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'


class ParseApp:
    """ MidiApp """
    def __init__(self, midi_file, channel=[], debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self.__log = get_logger(self.__class__.__name__, self._dbg)
        self.__log.debug('midi_file=%s, channel=%s',
                         midi_file, channel)

        self._midi_file = midi_file
        self._channel = channel

        self._parser = Parser(debug=self._dbg)

    def main(self) -> None:
        """ main """
        self.__log.debug('')

        music_data = self._parser.parse(self._midi_file, self._channel)

        print('music_data = %s' % (json.dumps(music_data, indent=4)))

    def end(self) -> None:
        """ end: do nothing """


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
            except EOFError as ex:
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


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help='''
<< Music Box Test >>

Usage: python3 -m musicbox [OPTIONS] COMMAND [OPTIONS] [ARGS] ...
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
        print()
        print('sub-command = %s' % subcmd)
        print()


@cli.command(context_settings=CONTEXT_SETTINGS, help="""
MIDI parser test
""")
@click.argument('midi_file', type=click.Path(exists=True))
@click.option('--channel', '-c', 'channel', type=int, multiple=True,
              help='MIDI channel')
@click.option('--debug', '-d', 'dbg', is_flag=True, default=False,
              help='debug flag')
def parse(midi_file, channel, dbg) -> None:
    """ parser main """
    log = get_logger(__name__, dbg)

    app = ParseApp(midi_file, channel, debug=dbg)
    try:
        app.main()
    finally:
        log.debug('finally')
        app.end()


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


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
