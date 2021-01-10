#!/usr/bin/env python3
#
# (c) 2020 Yoichi Tanibayashi
#
"""
Music Box Web Interface for Upload
"""
__author__ = 'Yoichi Tanibayashi'
__date__ = '2021/01'
__version__ = '0.1'

import time
import tornado.web
from .my_logger import get_logger


class UploadWebHandler(tornado.web.RequestHandler):
    """
    Web handler
    """
    HTML_FILE = 'upload.html'

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

        if msg == '':
            msg = 'ファイルを選択して下さい'

        self.render(self.HTML_FILE,
                    title="Robot Music Box <Upload>",
                    author="FabLab Kannai",
                    version=__version__,
                    msg=msg )

    def post(self):
        """
        POST method
        """
        self._mylog.debug('request=%s', self.request)

        try:
            upfile = self.request.files['file1'][0]
        except KeyError:
            self._mylog.warning('no file')
            self.get(msg='ファイルを指定して下さい')
            return

        upfilename = upfile['filename']
        self._mylog.debug('upfilename=%s', upfilename)

        with open('/tmp/' + upfilename, mode='wb') as f:
            f.write(upfile['body'])

        self.get(msg='「%s」をアップロードしました' % (upfilename))

        #self.write('Content-Type: text/html\n')
        #self.finish('「%s」をアップロードしました' % (upfilename))
        #self.redirect('/')
