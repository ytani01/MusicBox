#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Web Interface for Calibration
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'
__version__ = '0.2'

import tornado.web
from .my_logger import get_logger


class CalibrationWebHandler(tornado.web.RequestHandler):
    """
    Web handler
    """
    HTML_FILE = 'calibration.html'

    CH_N = 15
    CH_CENTER = 7

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('req=%s', req)

        super().__init__(app, req)

    def get(self, msg=''):
        """
        GET method and rendering
        """
        self._mylog.debug('request=%s', self.request)

        self.render(self.HTML_FILE,
                    title="Robot Music Box <Calibration>",
                    author="FabLab Kannai",
                    version=__version__,
                    msg=msg,
                    ch_list1=['%02d' % (i) for i in range(
                        0, self.CH_CENTER)],

                    ch_list2=['%02d' % (i) for i in range(
                        self.CH_CENTER, self.CH_N)])
