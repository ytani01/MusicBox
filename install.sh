#!/bin/sh
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`

MIDILIB_PKG_NAME="midilib"
MIDILIB_DIR="MIDI-lib"
MIDILIB_GIT="https://github.com/ytani01/${MIDIRLIB_DIR}.git"

STEPMTR_PKG_NAME="stepmtr"
STEPMTR_DIR="StepperMotor"
STEPMTR_GIT="https://github.com/ytani01/${STEPMTR_DIR}.git"

#
# main
#
cd $MYDIR
MYDIR=`pwd`
echo [ $MYDIR ]

#
# venv
#
if [ -z $VIRTUAL_ENV ]; then
    echo
    echo "ERROR: Please activate Python3 Virtualenv and run again"
    echo
    exit 1
fi
cd $VIRTUAL_ENV
echo '[' `pwd` ']'

#
# update pip
#
pip install -U pip
hash -r
pip -V

#
# MIDI-lib
#
pip show $MIDILIB_PKG_NAME
if [ $? -ne 0 ]; then
    if [ ! -d $MIDILIB_DIR ]; then
        git clone $MIDILIB_GIT
    fi

    cd $MIDILIB_DIR
    pip install .
fi
