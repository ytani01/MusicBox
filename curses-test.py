#!/usr/bin/env python3

import time
import curses

def main(stdscr):
    stdscr.keypad(True)

    stdscr.clear()

    while True:
        key = stdscr.getch()
        ch = chr(key).rstrip('\n')
        print('0x%x "%s"\r' % (key, ch))
        stdscr.refresh()

        if ch == 'q' or key == 0x1b:
            break

if __name__ == '__main__':
    curses.wrapper(main)
    print(key)
