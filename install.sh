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

CUILIB_PKG="cuilib"
CUILIB_DIR="CuiLib"
CUILIB_GIT="${GITHUB_TOP}/${CUILIB_DIR}.git"

STEPMTR_PKG="stepmtr"
STEPMTR_DIR="StepperMotor"
STEPMTR_GIT="${GITHUB_TOP}/${STEPMTR_DIR}.git"

SERVO_PKG="servoPCA9685"
SERVO_DIR="ServoPCA9685"
SERVO_GIT="${GITHUB_TOP}/${SERVO_DIR}.git"

MUSICBOX_PKG="musicbox"

#
# fuctions
#
cd_echo() {
    cd $1
    echo "### [ `pwd` ]"
}

install_my_python_pkg() {
    _PKG=$1
    _DIR=$2
    _GIT=$3

    cd_echo $VIRTUAL_ENV

    echo "### installing $_PKG"
    echo

    if [ ! -d $_DIR ]; then
        git clone $_GIT || exit 1
    fi

    cd_echo $_DIR
    git pull
    pip install .
    echo
}

#
# main
#
cd_echo $MYDIR
MYDIR=`pwd`
echo

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
cd_echo $VIRTUAL_ENV
echo

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
echo
pip install -U pip setuptools wheel
hash -r
pip -V
echo

#
# install my python packages
#
install_my_python_pkg $MIDILIB_PKG $MIDILIB_DIR $MIDILIB_GIT
install_my_python_pkg $CUILIB_PKG $CUILIB_DIR $CUILIB_GIT
install_my_python_pkg $STEPMTR_PKG $STEPMTR_DIR $STEPMTR_GIT
install_my_python_pkg $SERVO_PKG $SERVO_DIR $SERVO_GIT
echo

#
# install musicbox package
#
cd_echo $MYDIR
pip install .

echo
echo "#################"
echo "### Completed ###"
echo "#################"
echo
