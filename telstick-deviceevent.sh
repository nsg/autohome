#!/bin/bash

# Place this in /usr/local/share/telldus/scripts/deviceevent/

if [[ $DEVICEID == 1 ]]; then

    if [[ $METHOD == 1 ]]; then
        curl 10.90.0.223:5000/set-state/normal
    else
        curl 10.90.0.223:5000/set-state/off
    fi

fi
