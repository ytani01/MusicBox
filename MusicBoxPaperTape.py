#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Description
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2020'

from MyLogger import get_logger


class MusicBoxPaperTape:
    """MusicBoxPaperTape

    Attributes
    ----------
    infile: str
        input file name (path)
    """
    _log = get_logger(__name__, False)

    COMMENT_CHR = '#'

    ON_CHR  = 'oO*'
    OFF_CHR = '-_'

    def __init__(self, infile=None, debug=False):
        """constructor

        Parameters
        ----------
        infile: str
            input file name
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('infile=%s', infile)

        self.infile = infile

    def end(self):
        """end

        Call at the end of program
        """
        self._log.debug('doing ..')
        print('end of MusicBoxPaperTape')
        self._log.debug('done')

    def parse1(self, line):
        """parse1

        Parameters
        ----------
        line: line
            paper tape line

        Returns
        -------
        data: dict {'ch': [int, ..], 'delay': int}
           ch: servo ch number (0..14)
           delay: delay (msec)

           None: Error (something is wrong)
           {'ch': None, 'delay': None}: no data (ex. comment line)
           {'ch': None, 'delay': 500}: delay only
           {'ch': [1,3,5], 'delay': None}: play and default delay
           {'ch': [], 'delay': 500}: sleep 500msec
        """
        self._log.debug('line=%a', line)

        # remove comment
        comment_i = None
        try:
            comment_i = line.index(self.COMMENT_CHR)
        except ValueError as e:
            self._log.debug('%s:%s', type(e), e)

        if comment_i is not None:
            line = line[0:comment_i]

        self._log.debug('line=%a', line)

        word = line.split()
        self._log.debug('word=%s', word)

        if len(word) == 0:
            return dict(ch=None, delay=None)

        delay = None

        try:
            delay = int(word[-1])
            word.pop()
        except ValueError as e:
            self._log.debug('%s:%s.. ignored', type(e), e)

        self._log.debug('word=%s, delay=%s', word, delay)

        if len(word) == 0:
            return dict(ch=None, delay=delay)

        ch = []

        for i, c in enumerate(list(word[0])):
            if c in self.ON_CHR:
                ch.append(i)

        return dict(ch=ch, delay=delay)

    def parse(self, infile):
        """parse input file

        入力ファイル全体をパースする。
        何もしない行(None, {ch: None, delay: None})は無視をする。

        Parameters
        ----------
        infile: str
            input file name

        Returns
        -------
        result: list of dict(list of int, in)
          ex. [
                {'ch': None, 'delay': 600'},
                {'ch': [1, 3, 5], 'delay': None},
                {'ch': [], 'delay': 2000}
              ]
        """
        self._log.debug('infile=%s', infile)

        with open(infile) as f:
            lines = f.readlines()

        res = []
        for line in lines:
            res1 = self.parse1(line)

            if res1 is None:
                continue

            if res1['ch'] is None and res1['delay'] is None:
                continue

            res.append(res1)

        return res


# --- 以下、サンプル ---


class SampleApp:
    """Sample application class

    Attributes
    ----------
    """
    _log = get_logger(__name__, False)

    def __init__(self, paper_tape_file, debug=False):
        """constructor

        Parameters
        ----------
        paper_tape_file: str
            入力ファイル
        """
        self._dbg = debug
        __class__._log = get_logger(__class__.__name__, self._dbg)
        self._log.debug('paper_tape_file=%s', paper_tape_file)

        self.paper_tape_file = paper_tape_file

        self.obj = MusicBoxPaperTape(debug=self._dbg)

    def main(self):
        """main
        """
        self._log.debug('')

        with open(self.paper_tape_file) as f:
            lines = f.readlines()

        for line in lines:
            res = self.obj.parse1(line)
            print('res=%s' % (res))

        print()

        res = self.obj.parse(self.paper_tape_file)
        print('res=%s' % (res))

        self._log.debug('done')

    def end(self):
        """end

        Call at the end of program.
        """
        self._log.debug('doing ..')
        self.obj.end()
        self._log.debug('done')


import click
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.command(context_settings=CONTEXT_SETTINGS, help='''
Description
''')
@click.argument('paper_tape_file', type=click.Path(exists=True))
@click.option('--debug', '-d', 'debug', is_flag=True, default=False,
              help='debug flag')
def main(paper_tape_file, debug):
    """サンプル起動用メイン関数
    """
    _log = get_logger(__name__, debug)
    _log.debug('paper_tape_file=%s', paper_tape_file)

    app = SampleApp(paper_tape_file, debug=debug)
    try:
        app.main()
    finally:
        _log.debug('finally')
        app.end()


if __name__ == '__main__':
    main()
