#!/bin/sh -x
#
# Music Box boot script
#
# (c) 2021 Yoichi Tanibayashi
#

LOGDIR=/tmp
MUSICBOX_CMD=$HOME/bin/MusicBox

#
# kill
#
sudo pkill pigpiod

PIDS=`ps x|grep python|grep musicbox|sed 's/ *//'|cut -d ' ' -f 1`
while [ ! -z "$PIDS" ]; do
    for p in $PIDS; do
        kill $p
        sleep 1
    done
    PIDS=`ps x|grep python|grep musicbox|sed 's/ *//'|cut -d ' ' -f 1`
done

if [ ! -z $1 ]; then
    # don't boot, kill only
    exit 0
fi

#
# boot
#
sudo pigpiod
sleep 2

${MUSICBOX_CMD} server -w 0 -p 8880 >> $LOGDIR/server.log 2>&1 &
sleep 2
${MUSICBOX_CMD} server -w 1 -p 8881 >> $LOGDIR/server1.log 2>&1 &
sleep 2
${MUSICBOX_CMD} server -w 2 -p 8882 >> $LOGDIR/server2.log 2>&1 &
sleep 2
${MUSICBOX_CMD} server -w 3 -p 8883 >> $LOGDIR/server3.log 2>&1 &
sleep 2
${MUSICBOX_CMD} webapp >> $LOGDIR/webapp.log 2>&1 &
sleep 2
