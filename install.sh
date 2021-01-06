#!/bin/sh
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`

BINDIR="$HOME/bin"

WRAPPER_SCRIPT="MusicBox"

SERVO_CONF="musicbox-servo.conf"
VENVDIR_FILE="musicbox-venvdir"

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
        echo "ERROR: Please create and activate Python3 Virtualenv(venv) and run again"
        echo
        echo "\$ cd ~"
        echo "\$ python -m venv env1"
        echo "\$ . ~/env1/bin/activate"
        echo
        exit 1
    fi
    echo "### activate venv"
    . ../bin/activate
fi
cd_echo $VIRTUAL_ENV

echo "### create $HOME/$VENVDIR_FILE"
echo $VIRTUAL_ENV > $HOME/$VENVDIR_FILE
echo

#
# update pip, setuptools, and wheel
#
echo "### insall/update pip etc. .."
echo
pip install -U pip setuptools wheel
hash -r
echo
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

#
# copy musicbox-servo.conf
#
if [ ! -f $HOME/$SERVO_CONF ]; then
    echo "### copy $SERVO_CONF"
    cp -v sample.$SERVO_CONF $HOME/$SERVO_CONF
    echo
fi

#
# install wrapper shell script
#
if [ ! -d $BINDIR ]; then
    mkdir -pv $BINDIR
fi
cp -fv $WRAPPER_SCRIPT $BINDIR
echo

echo "### Completed"
echo
