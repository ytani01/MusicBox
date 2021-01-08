#!/bin/sh
#
# Music Box boot script
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`

LOGDIR=/tmp
MUSICBOX_CMD=$HOME/bin/MusicBox

BOOT_FLAG=1

#
# functions
#
echo_do() {
    _TS=`date +'%F %T'`
    echo "$_TS $*"
    eval "$*"
    return $?
}

usage() {
    echo
    echo "  Music Box boot script"
    echo
    echo "  Usage: $MYNAME [-h] [-k]"
    echo
    echo "    -k   kill only"
    echo "    -h   show this usage"
    echo
}

get_musicbox_pid() {
    echo `ps x | grep python | sed '/musicbox/s/ *//' | cut -d ' ' -f 1`
}

#
# main
#
while getopts hk OPT; do
    case $OPT in
        h) usage; exit 0;;
        k) BOOT_FLAG=0;;
        *) usage; exit 1;;
    esac
    shift
done

#
# kill
#
echo_do "sudo pkill pigpiod"
sleep 1

PIDS=`get_musicbox_pid`
while [ ! -z "$PIDS" ]; do
    echo_do "kill $PIDS"
    sleep 1
    PIDS=`get_musicbox_pid`
done

if [ $BOOT_FLAG -eq 0 ]; then
    # don't boot, kill only
    exit 0
fi

#
# boot
#
echo_do "sudo pigpiod"
sleep 1

echo_do "${MUSICBOX_CMD} webapp >> $LOGDIR/webapp.log 2>&1 &"
sleep 1

echo_do "${MUSICBOX_CMD} server -w 0 -p 8880 >> $LOGDIR/server.log 2>&1 &"
sleep 1
echo_do "${MUSICBOX_CMD} server -w 1 -p 8881 >> $LOGDIR/server1.log 2>&1 &"
sleep 1
echo_do "${MUSICBOX_CMD} server -w 2 -p 8882 >> $LOGDIR/server2.log 2>&1 &"
sleep 1
echo_do "${MUSICBOX_CMD} server -w 3 -p 8883 >> $LOGDIR/server3.log 2>&1 &"
sleep 1
