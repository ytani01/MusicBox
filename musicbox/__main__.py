#
# (c) 2020 Yoichi Tanibayashi
#
"""
main for midi_tools
"""
import json
import click
from . import Parser
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


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True,
             context_settings=CONTEXT_SETTINGS, help='''
python3 -m midi_tools COMMAND [OPTIONS] [ARGS] ...
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
        print('midi_tools command = %s' % subcmd)
        print()


@cli.command(context_settings=CONTEXT_SETTINGS, help='''
MIDI parser for Music Box
''')
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


if __name__ == '__main__':
    cli()  # pylint: disable=no-value-for-parameter
