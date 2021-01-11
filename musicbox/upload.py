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

import os
import time
import json
import tornado.web
from . import WsClient, Midi, PaperTape
from .my_logger import get_logger


class UploadWebHandler(tornado.web.RequestHandler):
    """
    Web handler
    """
    HTML_FILE = 'upload.html'

    SVR_LIST={
        8880: 'Music Box',
        8881: 'Wav File Mode',
        8882: 'Piano',
        8883: 'Full MIDI notes'
    }

    def __init__(self, app, req):
        """ Constructor """
        self._dbg = app.settings.get('debug')
        self._mylog = get_logger(__class__.__name__, self._dbg)
        self._mylog.debug('debug=%s', self._dbg)
        self._mylog.debug('req=%s', req)

        self._upload_dir = app.settings.get('upload_dir')
        self._musicdata_dir = app.settings.get('musicdata_dir')

        self._mylog.debug('upload_dir=%s, musicdata_dir=%s',
                          self._upload_dir, self._musicdata_dir)

        super().__init__(app, req)

    def get(self, svr_port=8880, msg=''):
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
                    svr_port=svr_port,
                    svr_list=self.SVR_LIST,
                    msg=msg )

    def post(self):
        """
        [TBD] ``wav_mode``の判断

        POST method
        """
        self._mylog.debug('request=%s', self.request.__dict__)

        svr_port = int(self.request.body_arguments['svr_port'][0])
        self._mylog.debug('svr_port=%s', svr_port)

        ws_url = 'ws://localhost:%d/' % svr_port
        self._mylog.debug('ws_url=%s', ws_url)

        try:
            upfile = self.request.files['file1'][0]
        except KeyError:
            self._mylog.warning('no file')
            self.get(msg='ファイルを指定して下さい')
            return

        upfilename = upfile['filename']
        upfile_ext = str.lower(os.path.splitext(upfilename)[-1][1:])
        self._mylog.debug('upfilename=%s, upfile_ext=%s',
                          upfilename, upfile_ext)

        upload_path_name = '%s/%s' % (self._upload_dir, upfilename)
        musicdata_path = '%s/%s-%s.%s' % (
            self._musicdata_dir, upfilename, svr_port, 'json')

        # [TBD] musicdata_pathの存在を確認し、パージング処理を省略？

        with open(upload_path_name, mode='wb') as f:
            f.write(upfile['body'])

        ws = WsClient(url=ws_url, debug=self._dbg)

        parsed_data = None
        
        if upfile_ext in ('mid', 'midi'):
            parser = Midi(debug=self._dbg)

            note_origin = -1
            note_offset = Midi.NOTE_OFFSET
            if svr_port in (8882, 8883):
                note_origin = 0
                note_offset = []

            parsed_data = parser.parse(upload_path_name,
                                       note_origin=note_origin,
                                       note_offset=note_offset)
 
        if upfile_ext in ('txt',):
            parser = PaperTape(debug=self._dbg)
            parsed_data = parser.parse(upload_path_name)
            
        if parsed_data is None:
            self.get(svr_port=svr_port,
                     msg='対応してないファイルです')
            return

        if parsed_data == []:
            self.get(svr_port=svr_port,
                     msg='データがありません')
            return

        # save parsed data and send it to Music Box server
        with open(musicdata_path, mode='w') as f:
            json.dump(parsed_data, f, indent=4)

        try:
            ws.send_music_file(musicdata_path)
        except ConnectionRefusedError:
            self.get(svr_port=svr_port,
                     msg='メイン・サーバと通信できません')
            return

        self.get(svr_port=svr_port,
                 msg='%s' % (upfilename))
