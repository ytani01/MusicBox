#!/bin/sh

PIANOWAV_DIR=./piano_wav
PREFIX=ch

NOTE_BASE=$1

if [ ! -d $PIANOWAV_DIR ]; then
    echo "ERROR: no such directory: $PIANOWAV_DIR"
    exit 1
fi

cd $PIANOWAV_DIR

CH_I=0
for i in 0 2 4 5 7 9 11 12 14 16 17 19 21 23 24; do
    CH_I=`expr $CH_I + 100 | sed 's/^1//'`
    PIANO_I=`expr $i + $NOTE_BASE + 1000 | sed 's/^1//'`

    ln -sfv piano${PIANO_I}.wav ch${CH_I}.wav

    CH_I=`expr $CH_I + 1`
done
