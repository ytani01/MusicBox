#
# (c) 2021 Yoichi Tanibayashi
#
"""
PaperTape library for Music Box
"""
__author__ = 'Yoichi Tanibayashi'
__data__ = '2021/01'

from .parser import Parser
from .my_logger import get_logger


class PaperTape(Parser):
    """
    PaperTape parser for Music Box
    """
    COMMENT_CHR = '#'

    ON_CHR = 'oO*'
    OFF_CHR = '-_'

    def __init__(self, debug=False):
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

        super().__init__(debug=self._dbg)

    def parse(self, infile):
        """
        Parameters
        ----------
        infile: str

        Returns
        -------
        music_data: list of MusicDataEnt
        """
        self._log.debug('infile=%s', infile)

        with open(infile) as f:
            lines = f.readlines()

        music_data = []
        delay_unit_msec = 0
        delay_msec = 0
        abs_time_sec = 0
        for line in lines:

            # remove comment
            comment_i = None
            try:
                comment_i = line.index(self.COMMENT_CHR)
            except ValueError:
                pass  # ignore

            if comment_i is not None:
                line = line[0:comment_i]

            word = line.split()

            if not word:
                # comment or empty line
                continue

            try:
                delay_unit_msec = int(word[0])
                self._log.debug('delay_unit_msec=%s', delay_unit_msec)
                continue
            except ValueError:
                pass

            ch = []
            for i, c in enumerate(list(word[0])):
                if c in self.ON_CHR:
                    ch.append(i)

            if ch:
                ent = {'abs_time': round(abs_time_sec, 3),
                       'delay': round(delay_msec, 1),
                       'ch': ch}
                music_data.append(ent)
                print(ent)

                delay_msec = 0

            delay_msec += delay_unit_msec
            abs_time_sec += delay_unit_msec / 1000

        ent = {'abs_time': round(abs_time_sec, 3),
               'delay': round(delay_msec, 1),
               'ch': []}
        music_data.append(ent)
        print(ent)

        return music_data
