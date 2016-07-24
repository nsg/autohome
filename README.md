# Automatic scripts and things for my home

This is a collection of scripts and things that I use to control my home. Some assembly is needed and understanding of the tools are needed.

## hue.py
Used to control my Hue lights, this script runs all the time and manages the state.

## hue.sh
Startup script deployed to a container on my home server.

## hue.service
Unit-file for systemd for hue.sh

## sonos.py

Control script that talks with my sonos speakers.

## telstick-deviceevent.sh

Trigged by telldusd when we recv a event.
