#!/bin/sh
#
# Music Box boot script
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`

MUSICBOX_CMD=$HOME/bin/MusicBox

ENV_FILE=$HOME/musicbox-env
. $ENV_FILE

LOGDIR=$MUSICBOX_LOG_DIR

BOOT_FLAG=1
DEBUG_FLAG=

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
    echo "  Usage: $MYNAME [-h] [-k] [-d]"
    echo
    echo "    -k   kill only"
    echo "    -d   debug flag"
    echo "    -h   show this usage"
    echo
}

get_musicbox_pid() {
    echo `ps x | grep python | sed -n '/musicbox/s/ *//p' | cut -d ' ' -f 1`
}

#
# main
#
while getopts hkd OPT; do
    case $OPT in
        h) usage; exit 0;;
        k) BOOT_FLAG=0;;
        d) DEBUG_FLAG="-d";;
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
sleep 2

if [ $BOOT_FLAG -eq 0 ]; then
    # don't boot, kill only
    exit 0
fi

#
# boot
#
echo_do "sudo pigpiod"
sleep 1

echo_do "${MUSICBOX_CMD} webapp $DEBUG_FLAG >> $LOGDIR/webapp.log 2>&1 &"
sleep 1

echo_do "${MUSICBOX_CMD} server -w 0 -p 8880 $DEBUG_FLAG >> $LOGDIR/server0.log 2>&1 &"
sleep 2
echo_do "${MUSICBOX_CMD} server -w 1 -p 8881 $DEBUG_FLAG >> $LOGDIR/server1.log 2>&1 &"
sleep 2
echo_do "${MUSICBOX_CMD} server -w 2 -p 8882 $DEBUG_FLAG >> $LOGDIR/server2.log 2>&1 &"
sleep 2
echo_do "${MUSICBOX_CMD} server -w 3 -p 8883 $DEBUG_FLAG >> $LOGDIR/server3.log 2>&1 &"

sleep 5

echo_do "${MUSICBOX_CMD} send -p 8882 single_play 69"
echo_do "${MUSICBOX_CMD} send -p 8882 single_play 73"
echo_do "${MUSICBOX_CMD} send -p 8882 single_play 76"
echo_do "${MUSICBOX_CMD} send -p 8882 single_play 69 73 76"
