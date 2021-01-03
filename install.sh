#!/bin/sh
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`

GITHUB_TOP="https://github.com/ytani01"

MIDILIB_PKG="midilib"
MIDILIB_DIR="MIDI-lib"
MIDILIB_GIT="${GITHUB_TOP}/${MIDILIB_DIR}.git"

CUILIB_PKG="curlib"
CUILIB_DIR="CuiLib"
CUILIB_GIT="${GITHUB_TOP}/${CUILIB_DIR}.git"

STEPMTR_PKG="stepmtr"
STEPMTR_DIR="StepperMotor"
STEPMTR_GIT="${GITHUB_TOP}/${STEPMTR_DIR}.git"

MUSICBOX_PKG="musicbox"

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
    if [ ! -f ../bin/activate ]; then
        echo
        echo "ERROR: Please activate Python3 Virtualenv and run again"
        echo
        exit 1
    fi
    echo "### activate venv"
    . ../bin/activate
fi
cd $VIRTUAL_ENV
echo [ `pwd` ]

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
pip install -U pip setuptools wheel
hash -r
pip -V

#
# MIDI-lib
#
cd $VIRTUAL_ENV
echo [ `pwd` ]

pip show $MIDILIB_PKG
if [ $? -ne 0 ]; then
    echo "### installing $MIDILIB_PKG .."
    
    if [ ! -d $MIDILIB_DIR ]; then
        git clone $MIDILIB_GIT || exit 1
    fi

    cd $MIDILIB_DIR
    echo [ `pwd` ]
    pip install .
fi

#
# CuiLib
#
cd $VIRTUAL_ENV
echo [ `pwd` ]

pip show $CUILIB_PKG
if [ $? -ne 0 ]; then
    echo "### installing $CUILIB_PKG .."

    if [ ! -d $CUILIB_DIR ]; then
        git clone $CUILIB_GIT || exit 1
    fi

    cd $CUILIB_DIR
    echo [ `pwd` ]
    pip install .
fi

#
# StepperMotor
#
cd $VIRTUAL_ENV
echo [ `pwd` ]

pip show $STEPMTR_PKG
if [ $? -ne 0 ]; then
    echo "### installing $STEPMTR_PKG .."

    if [ ! -d $STEPMTR_DIR ]; then
        git clone $STEPMTR_GIT || exit 1
    fi

    cd $STEPMTR_DIR
    echo [ `pwd` ]
    pip install .
fi

#
# musicbox package
#
cd $MYDIR
echo [ `pwd` ]
#pip install .

