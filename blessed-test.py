#!/usr/bin/env python3
from blessed import Terminal

t = Terminal()

with t.cbreak():
    while True:
        k = t.inkey(timeout=None)

        if not k:
            continue

        if k.is_sequence:
            print('k.name=%s' % (k.name))
            continue

        print('k=%s' % (k))
