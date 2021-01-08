#!/bin/sh
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`

WAV_SEC=0.25
WAV_RATE=44100

export PYGAME_HIDE_SUPPORT_PROMPT=hide

#
# functions
#
usage() {
    echo
    echo "  Usage: $MYNAME"
    echo
    echo "    -t  sec, default=$WAV_SEC sec"
    echo "    -r  sampling rate, default=$WAV_RATE Hz"
    echo
}

#
# main
#
while getopts ht:r: OPT; do
    case $OPT in
        t) WAV_SEC=$OPTARG; shift;;
        r) WAV_RATE=$OPTARG; shift;;
        h) usage; exit 0;;
        *) usage; exit 1;;
    esac
    shift
done

NOTE_I=0
while [ $NOTE_I -lt 128 ]; do
    NOTE_I=`expr $NOTE_I + 1000 | sed 's/^1//'`

    WAV_FNAME="note$NOTE_I.wav"
    echo $WAV_FNAME

    python -m midilib wav -t $WAV_SEC -r $WAV_RATE -m $NOTE_I -n $WAV_FNAME

    NOTE_I=`expr $NOTE_I + 1`
done
