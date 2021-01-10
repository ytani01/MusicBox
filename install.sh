#!/bin/sh -e
#
# Robot Music Box install script
#
#   (c) 2021 Yoichi Tanibayashi
#
############################################################
help() {
    cat <<'END'

[インストール後のディレクトリ構造]

 $HOME/ ... ホームディレクトリ
    |
    +- bin/ ... シェルスクリプトなど
    |   |
    |   +- MusicBox ... メイン・コマンド・スクリプト (wrapper script)
    |   +- boot-musicbox.sh ... 起動スクリプト
    |
    +- musicbox-env ... 環境変数設定ファイル【インストール時に作成】
    |    【環境変数】
    |    MUSICBOX_DIR ... git clone されたディレクトリ
    |    MUSICBOX_WORK ... 作業用ディレクトリ ($HOME/msucibox_work/)
    |    VENVDIR ... python3 Virtualenv ディレクトリ ($HOME/env1/ など)
    |    (etc.)
    |
    +- musicbox-servo.conf ... サーボ調整パラメータ保存ファイル
    |
    +- musicbox_work/ ... 作業用ディレクトリ
    |   |
    |   +- upload/ ... アップロードされたファイル(MIDIなど)
    |   +- music_data/ ... パーズ後の音楽データ
    |   +- log/ ... ログディレクトリ
    |
    +- env1/  ... python3 Virtualenv(venv) 【ユーザが作成する】
        |
        +- musicbox/ ... musicboxプロジェクトの gitリポジトリ
        |
        | 【以下、インストールに必要なライブラリなど】
        |
        +- ServoPCA9685/
        +- StepperMotor/
        +- MIDI-lib/
        :

END
}

############################################################
MYNAME=`basename $0`
MYDIR=`dirname $0`

PKG_NAME="musicbox"

BINDIR="$HOME/bin"
WORKDIR="$HOME/${PKG_NAME}_work"
UPLOAD_DIR="$WORKDIR/upload"
MUSICDATA_DIR="$WORKDIR/music_data"
LOG_DIR="$WORKDIR/log/"

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

    echo "### install/update $_PKG"
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
if [ ! -z $1 ];then
    help
    exit 0
fi

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
echo "export MUSICBOX_DIR=$MYDIR" > $HOME/$ENV_FILE
echo "export MUSICBOX_WORK=$WORKDIR" >> $HOME/$ENV_FILE
echo "export VENVDIR=$VIRTUAL_ENV" >> $HOME/$ENV_FILE

echo "export MUSICBOX_WAV_DIR=\$MUSICBOX_DIR/wav" >> $HOME/$ENV_FILE
echo "export MUSICBOX_WEB_DIR=\$MUSICBOX_DIR/web-root" >> $HOME/$ENV_FILE

echo "export MUSICBOX_UPLOAD_DIR=\$MUSICBOX_WORK/upload" >> $HOME/$ENV_FILE
echo "export MUSICBOX_MUSICDATA_DIR=\$MUSICBOX_WORK/music_data" >> $HOME/$ENV_FILE
echo "export MUSICBOX_LOG_DIR=\$MUSICBOX_WORK/log" >> $HOME/$ENV_FILE
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

#
# install musicbox package
#
cd_echo $MYDIR
echo "### install main python package"
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

#
# make work directories
#
mkdir -pv $WORKDIR $UPLOAD_DIR $MUSICDATA_DIR $LOG_DIR

#
# display usage
#
echo "### usage"
echo
$WRAPPER_SCRIPT
echo
