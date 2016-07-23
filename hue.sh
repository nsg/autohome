#!/bin/bash

DATA_DIR=/var/lib/hue

log() {	echo $@; }

log "Setup enviroment"

# Setup a virtualenv
[ ! -e $DATA_DIR/.env ] && virtualenv $DATA_DIR/.env
. $DATA_DIR/.env/bin/activate

[ ! -e $DATA_DIR/app ] && git clone https://github.com/nsg/autohome.git $DATA_DIR/app

cd $DATA_DIR/app
export TZ=Europe/Stockholm

pip install -r requirements.txt
python hue.py
