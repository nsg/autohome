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

from __future__ import print_function
import argparse
import soco
import re
import time

class AutoHomeSonos():

    def list_soco(self):
        # Hack!
        r = None
        while not r:
            r = soco.discover()
            if not r:
                time.sleep(1)

        return list(r)

    def get_soco(self):
        return self.list_soco()[0]

    def find_playing_speaker(self):
        for s in self.list_soco():
            i = s.get_current_transport_info()
            if (i['current_transport_state'] == "PLAYING"):
                return s
        return None

    def list_groups(self):
        return self.get_soco().all_groups

    def print_groups(self):
        for zg in self.list_groups():
            print("Group: ", end="")
            for m in zg.members:
                if (m.player_name == zg.coordinator.player_name):
                    print("[{}] ".format(m.player_name), end="")
                else:
                    print(m.player_name, end=" ")
            print("")

    def print_volumes(self):
        for s in list_soco():
            print("{:15}{}".format(s.player_name, s.volume))

    def group_speakers(self):
        master = self.find_playing_speaker()
        if (master == None):
            print("No playing speaker found")
            return
        for s in self.list_soco():
            if(s.player_name != master.player_name):
                print("Join {} to master {}".format(s.player_name, master.player_name))
                s.join(master)

    def ungroup_speakers(self):
        master = self.find_playing_speaker()
        if (master == None):
            print("No playing speaker found")
            return
        for s in self.list_soco():
            if(s.player_name != master.player_name):
                print("Leave {} from master {}".format(s.player_name, master.player_name))
                s.unjoin()

    def set_volume(self, volume, speaker):
        r = re.compile(".*{}.*".format(speaker))
        for s in self.list_soco():
            if (r.match(s.player_name)):
                print("Set volume {} -> {} to {}".format(s.volume, volume, s.player_name))
                s.volume = volume
