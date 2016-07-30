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

from phue import Bridge
import logging, datetime, time, os

class AutoHomeHue:
    hue = None

    def __init__(self):
        self.hue = Bridge(ip='10.90.0.106', config_file_path="/var/lib/hue/hue.conf")

    def lights(self):
        return self.hue.lights

    def lights_name(self):
        return self.hue.get_light_objects('name')

    def is_locked(self, lamp):
        return os.path.isfile("/var/lib/hue/locks/{}".format(lamp.light_id))

    def lock_file(self, lamp):
        open("/var/lib/hue/locks/{}".format(lamp.light_id), 'a').close()

    def brightness(self, lamp, value, time=1):
        lamp.on = True
        self.hue.set_light(lamp.light_id, 'bri', value, transitiontime=time)

    def time_based_white(self, light):
        if not self.hue.get_light(light.name, 'on'): return False
        if not self.hue.get_light(light.name, 'reachable'): return False

        hour = datetime.datetime.now().hour

        # Be nice, show a nice warm light
        # between 00:00 - 08:00
        if hour < 8:
            hour = 24

        ct = 154 + ((500-154)/24) * hour

        if (light.colortemp != ct):
            self.hue.set_light(light.name, 'ct', ct)
            return True

        return False
