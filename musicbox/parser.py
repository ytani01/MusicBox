#
# (c) 2021 Yoichi Tanibayashi
#
"""
PaperTape library for Music Box
"""
__author__ = 'Yoichi Tanibayashi'
__data__ = '2021/01'

from .my_logger import get_logger


class Parser:
    """
    parser for Music Box
    """
    def __init__(self, debug=False) -> None:
        """ Constructor """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)

    def parse(self, infile):
        """
        override in sub-class

        Parameters
        ----------
        infile: str

        Returns
        -------
        music_data: list of MusicDataEnt
        """
        self._log.debug('infile=%s', infile)

        return []  # dummy
