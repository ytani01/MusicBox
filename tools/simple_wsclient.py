#!/usr/bin/env python3
#
# (c) 2021 Yoichi Tanibayashi
#
from websocket import create_connection
from musicbox import WsServer

port = WsServer.DEF_PORT
url = 'ws://localhost:%s' % (port)


while True:
    try:
        line = input('> ')
    except EOFError:
        print('[EOF]')
        break

    if not line:
        break

    ws = create_connection(url)
    ws.send(line)
    ws.close()
