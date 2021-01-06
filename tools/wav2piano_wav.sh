#!/bin/sh

SRCWAV_DIR=./wav
PIANOWAV_DIR=./piano_wav

NOTE_BASE=$1

NOTE=$NOTE_BASE
for f in $SRCWAV_DIR/39*.wav; do

    n2=`expr $NOTE + 1000 | sed 's/^1//'`
    DST_FILE="piano${n2}.wav"
    # echo $DST_FILE $f

    cp -fv $f $PIANOWAV_DIR/$DST_FILE

    NOTE=`expr $NOTE + 1`
done
