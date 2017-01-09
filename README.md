# Automatic scripts and things for my home

This is a collection of scripts and things that I use to control my home. Some assembly is needed and understanding of the tools are needed.

*Warning: Most of the code here is written in a sense of fast prototyping and trying things out, it's possible that I will clean things up in the future, time will tell...*

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

## pulseaudio.service
Used in the container pulse, this container is a sink. Installed packages are:

* pulseaudio
* pulseaudio-module-zeroconf
* pulseaudio-esound-compat

### /etc/pulse/daemon.conf
```
exit-idle-time = 10800
log-level = info
```

### /etc/pulse/default.pa
```
load-module module-native-protocol-unix auth-anonymous=1
load-module module-esound-protocol-tcp auth-anonymous=1
load-module module-native-protocol-tcp auth-ip-acl=127.0.0.1;192.168.1.0/24;fdad:a03e:511b::/64
load-module module-zeroconf-publish
```

### On client
Check the box in `paprefs`.

## pulseaudio-dlna.service
Relay the sound to my sonos speakers (or chromecast, whatever in the network)

* adduser sonos --disabled-password
* apt-add-repository ppa:qos/pulseaudio-dlna
* apt update
* apt install dbus-x11 pulseaudio-dlna

Note, use this instead of the pulseaudio unit. pulseaudio-dlna will start pulseaudio by it self.
