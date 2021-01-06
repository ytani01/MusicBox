#!/bin/sh -e
#
# (c) 2021 Yoichi Tanibayashi
#
MYNAME=`basename $0`
MYDIR=`dirname $0`

BINDIR="$HOME/bin"

WRAPPER_SCRIPT="MusicBox"
BOOT_SCRIPT="boot-musicbox.sh"
BIN_FILES="$WRAPPER_SCRIPT $BOOT_SCRIPT"

PKGS_TXT="pkgs.txt"
ENV_FILE="musicbox-env"
SERVO_CONF="musicbox-servo.conf"

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
    echo
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
echo "MYDIR=$MYDIR"
echo

#
# install Linux packages
#
echo "### install Linux packages"
echo
sudo apt install `cat $PKGS_TXT`
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

echo "### create $HOME/$ENV_FILE"
echo "MUSICBOX_DIR=$MYDIR" > $HOME/$ENV_FILE
echo "VENVDIR=$VIRTUAL_ENV" >> $HOME/$ENV_FILE
echo
cat $HOME/$ENV_FILE
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
echo "### install main python package"
cd_echo $MYDIR
echo
pip install .
echo

#
# copy musicbox-servo.conf
#
if [ ! -f $HOME/$SERVO_CONF ]; then
    echo "### copy $SERVO_CONF"
    echo
    cp -v sample.$SERVO_CONF $HOME/$SERVO_CONF
    echo
fi

#
# setup crontab for auto start
#
# [TBD]
echo "### setup crontab"
echo

CRONTAB_BAK=/tmp/crontab.bak
CRONTAB_OLD=/tmp/crontab.old
CRONTAB_NEW=/tmp/crontab.new
CRONTAB_SAMPLE=sample.crontab

crontab -l > $CRONTAB_BAK
echo "## backup crontab"
echo
cat $CRONTAB_BAK
echo
sleep 2

echo "## edit crontab"
echo
crontab -l | sed '/^# begin MusicBox/,/^# end MusicBox/d' > $CRONTAB_OLD
cat $CRONTAB_OLD $CRONTAB_SAMPLE > $CRONTAB_NEW
crontab $CRONTAB_NEW
crontab -l
echo
sleep 2

#
# install scripts
#
echo "### install scripts"
echo
if [ ! -d $BINDIR ]; then
    mkdir -pv $BINDIR
fi
cp -fv $BIN_FILES $BINDIR
echo

echo "### usage"
echo
$WRAPPER_SCRIPT
echo
