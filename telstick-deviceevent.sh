#!/bin/bash

# Place this in /usr/local/share/telldus/scripts/deviceevent/
curl 10.90.0.223:5000/telldus/$DEVICEID/$METHOD > /tmp/telldus-button.log
