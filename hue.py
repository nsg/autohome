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
from flask import Flask
from flask import render_template
from flask import redirect
import re

class House:

    hue = None
    state_dirty = True
    state = None
    was_state = None

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

    def brightness(self, lamp, value, time=1):
        lamp.on = True
        self.hue.set_light(lamp.light_id, 'bri', value, transitiontime=time)

    def lamp_state_control(self, lamp_name, state, restore_to="normal"):
        msg = []
        if self.was_state != state and not self.lights_name()[lamp_name].reachable:
            self.state_dirty = True
            if set_state(state):
                msg.append("{} unreachable, set state to {}".format(lamp_name, state))
        elif self.was_state == state and self.lights_name()[lamp_name].reachable:
            self.state_dirty = True
            if set_state(restore_to):
                msg.append("{} reachable, restore state to {}".format(lamp_name, restore_to))

        return msg

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

logging.basicConfig()
house = House()
app = Flask(__name__)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/hue")
def hue_status():
    return render_template('hue-status.html', lamps=house.lights())

@app.route("/set-state")
def set_state_index():
    states = [ "Normal", "Movie", "Bed", "Off" ]
    return render_template('set-state.html', active_state=house.load_state(), states=states)

@app.route("/set-state/<action>")
def set_state_url(action="normal"):
    house.state_dirty = True
    set_state(action)
    return redirect("/set-state", code=302)

@app.route("/telldus/<int:deviceid>/<int:method>")
def telldus(deviceid, method):
    house.state_dirty = True

    # Wall Switch - Button 1
    if deviceid == 1:
        if method == 1:
            set_state("normal")
        else:
            set_state("off")

    # Wall Switch - Button 2
    if deviceid == 2:
        if method == 1:
            pass
        else:
            set_state("bed")

    # Door Switch
    if deviceid == 3:
        if method == 1: # Door opens
            if (house.load_state() == "normal"):
                set_state("off")
            if (house.load_state() == "off"):
                set_state("normal")
        if method == 2: # Door closes
            pass

    return "Got a event with deviceid:{} and method:{}".format(deviceid, method)

def set_state(action):
    if not house.state_dirty: return False

    hour = datetime.datetime.now().hour

    if action == "normal":
        for l in house.lights():
            if re.match(r'^Hall spot', l.name):
                house.brightness(l, 150, 100)
            if re.match(r'^Vardagsrum', l.name):
                house.brightness(l, 201, 100)

            if l.name == "Kitchen":
                house.brightness(l, 201, 100)
            if re.match(r'^Kitchen Bench', l.name):
                if 6 > hour or hour > 18:
                    house.brightness(l, 201, 100)
                else:
                    l.on = False

            if l.name == "Soffa":
                l.on = False
            if l.name == "Soffa Large":
                if 6 > hour or hour > 18:
                    house.brightness(l, 201, 100)
                else:
                    l.on = False
            if l.name == "Bedroom":
                l.on = False

    if action == "movie":
        for l in house.lights():
            if re.match(r'^Hall spot', l.name):
                house.brightness(l, 50, 100)
            if re.match(r'^Vardagsrum', l.name):
                house.brightness(l, 50, 100)

            if l.name == "Soffa":
                house.brightness(l, 250, 100)
            if l.name == "Soffa Large":
                house.brightness(l, 50, 100)

    if action == "bed":
        for l in house.lights():
            if re.match(r'^Hall spot', l.name):
                l.on = False
            if re.match(r'^Vardagsrum', l.name):
                l.on = False
            if re.match(r'^Soffa', l.name):
                l.on = False
            if re.match(r'^Kitchen', l.name):
                l.on = False
            if l.name == "Bedroom":
                house.brightness(l, 150, 100)

    if action == "off":
        for l in house.lights():
            l.on = False

    house.save_state(action)
    house.state_dirty = False
    return True

@app.route("/api/hue/<int:lamp_id>/state/<state>")
def lamp_on(lamp_id, state):
    for l in house.lights():
        if l.light_id == lamp_id:
            if state == "on":
                l.on = True
            else:
                l.on = False
            return "Set lamp {} to {}\n".format(l.name, state)

@app.route("/tick")
def tick():
    msg = []

    # Set a nice time-based white color
    for l in house.lights():
        if not house.is_locked(l):
            if (house.time_based_white(l)):
                msg.append("Set light {} to time based white".format(l.name))

    # Restore the state, if it's dirty
    if set_state(house.load_state()):
        msg.append("Restore cached state\n")

    # Control lamps
    #msg = msg + house.lamp_state_control("Hall spot 1", "off")
    #msg = msg + house.lamp_state_control("Vardagsrum 1", "bed")

    return "\n".join(msg)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
