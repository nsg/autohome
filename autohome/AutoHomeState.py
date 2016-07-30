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

class AutoHomeState:
    state_dirty = True
    state = None
    was_state = None
    telldus_state = {}
    telldus_last_command = 0

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
