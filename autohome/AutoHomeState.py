#!/usr/bin/python

# Copyright (c) 2016 Stefan Berggren <nsg@nsg.cc>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import time
import thread
import requests
import json

class AutoHomeState:
    state_dirty = True
    state = None
    was_state = None
    telldus_state = {}
    telldus_last_command = 0

    alexa_last_state_ts = 0
    alexa_last_volume_ts = 0
    alexa_last_volume_room_ts = 0

    alexa_state = None
    alexa_volume = None
    alexa_volume_room = None

    def save_state(self, action):
        fd = open("/var/lib/hue/state", 'w')
        fd.write(action)
        fd.close()
        self.was_state = self.state
        self.state = action

    def load_state(self):
        fd = open("/var/lib/hue/state", 'r')
        r = fd.read()
        fd.close()
        self.was_state = self.state
        self.state = r
        return r

    def dirty(self, yes=True):
        self.state_dirty = yes

    def is_dirty(self):
        return self.state_dirty

    def telldus(self, deviceid, method):
        self.telldus_state[deviceid] = method

    def telldus_record_timestamp(self):
        self.telldus_last_command = time.time()

    def telldus_time_since_command(self):
        return time.time() - self.telldus_last_command

    def alexa_get(self):
        return {
            "state": self.alexa_state,
            "volume": self.alexa_volume,
            "volume_room": self.alexa_volume_room
        }

    def alexa_read_command(self):
        alexa = {
            "state": None,
            "volume": None,
            "volume_room": None
        }

        try:
            d = requests.get('https://nsg-home-skill.app.stefanberggren.se/state')
        except ConnectionError:
            return alexa

        try:
            jd = json.loads(d.text)
        except ValueError:
            return alexa

        alexa_state = jd.get('state', None)
        if alexa_state and alexa_state['ts'] > self.alexa_last_state_ts:
            self.alexa_state = alexa_state['value']
            self.alexa_last_state_ts = alexa_state['ts']
            self.dirty()
            alexa['state'] = self.alexa_state

        alexa_volume = jd.get('volume', None)
        if alexa_volume and alexa_volume['ts'] != self.alexa_last_volume_ts:
            self.alexa_volume = alexa_volume['value']
            self.alexa_last_volume_ts = alexa_volume['ts']
            alexa['volume'] = self.alexa_volume

        alexa_volume_room = jd.get('volume_room', None)
        if alexa_volume_room and alexa_volume_room['ts'] != self.alexa_last_volume_room_ts:
            self.alexa_volume_room = alexa_volume_room['value']
            self.alexa_last_volume_room_ts = alexa_volume_room['ts']
            alexa['volume_room'] = self.alexa_volume_room

        return alexa
