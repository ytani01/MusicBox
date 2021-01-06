#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Web Interface for Calibration
"""
__author__ = 'Yoichi Tanibayashi'
__date__   = '2021/01'
__version__ = '0.1'

import os
import tornado.ioloop
import tornado.web
from .my_logger import get_logger


class CalibrationWebHandler(tornado.web.RequestHandler):
    """
    Web handler
    """
    CH_N = 15
    CH_CENTER = 7

    def __init__(self, app, req):
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)

        super().__init__(app, req)

    def get(self):
        """
        GET method and rendering
        """
        self._mylog.debug('request=%s', self.request)

        self.render("index.html",
                    title="Robot Music Box Calibration",
                    author="FabLab Kannai",
                    version=__version__,

                    ch_list1=['%02d' % (i) for i in range(
                        0, self.CH_CENTER)],

                    ch_list2=['%02d' % (i) for i in range(
                        self.CH_CENTER, self.CH_N)])


class CalibrationWebServer:
    """
    Web server
    """
    DEF_PORT = 10080
    DEF_WEBDIR = './web-calibration'

    def __init__(self, port=DEF_PORT, webdir=DEF_WEBDIR, debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
            port number
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.debug('port=%s, webdir=%s', port, webdir)

        self._port = port
        self._webdir = webdir

        # self._webdir = Path(__file__).resolve().parents[0]
        self._log.debug('webdir=%s', self._webdir)

        self._app = tornado.web.Application(
            [(r"/", CalibrationWebHandler), ],
            autoreload=True,
            debug=self._dbg,
            static_path=os.path.join(self._webdir, "static"),
            template_path=os.path.join(self._webdir, "templates")
        )

    def main(self):
        """ main """
        self._log.debug('')

        self._app.listen(self._port)
        self._log.info('start server: run forever ..')
        tornado.ioloop.IOLoop.current().start()

        self._log.debug('done')
