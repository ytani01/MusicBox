#!/bin/sh
#
# Music Box boot script
#
# (c) 2021 Yoichi Tanibayashi
#

LOGDIR=/tmp
MUSICBOX_CMD=$HOME/bin/MusicBox

pkill python
sleep 5

sudo pigpiod
sleep 2

${MUSICBOX_CMD} svr >> $LOGDIR/svr.log 2>&1 &
${MUSICBOX_CMD} svr -w 1 -p 8881 >> $LOGDIR/svr1.log 2>&1 &
${MUSICBOX_CMD} svr -w 2 -p 8882 >> $LOGDIR/svr2.log 2>&1 &
${MUSICBOX_CMD} svr -w 3 -p 8883 >> $LOGDIR/svr3.log 2>&1 &
${MUSICBOX_CMD} calibration >> $LOGDIR/calibraion.log 2>&1 &
