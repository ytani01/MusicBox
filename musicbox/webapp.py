#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Web Interface for Calibration
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'

import os
import tornado.ioloop
import tornado.web
from .calibration import CalibrationWebHandler
from .my_logger import get_logger


class WebServer:
    """
    Web application server
    """
    DEF_PORT = 10080
    DEF_WEBDIR = './web-root'

    def __init__(self, port=DEF_PORT, webdir=DEF_WEBDIR, debug=False):
        """ Constructor

        Parameters
        ----------
        port: int
            port number
        """
        self._dbg = debug
        self._log = get_logger(self.__class__.__name__, self._dbg)
        self._log.info('port=%s, webdir=%s', port, webdir)

        self._port = port
        self._webdir = webdir

        self._app = tornado.web.Application(
            [
                (r"/", CalibrationWebHandler),
                (r"/calibration.*", CalibrationWebHandler),
            ],
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