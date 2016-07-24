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

    def __init__(self):
        self.hue = Bridge(ip='10.90.0.106', config_file_path="/var/lib/hue/hue.conf")

    def lights(self):
        return self.hue.lights

    def is_locked(self, lamp):
        return os.path.isfile("/var/lib/hue/locks/{}".format(lamp.light_id))

    def lock_file(self, lamp):
        open("/var/lib/hue/locks/{}".format(lamp.light_id), 'a').close()

    def brightness(self, lamp, value, time=1):
        lamp.on = True
        self.hue.set_light(lamp.light_id, 'bri', value, transitiontime=time)

    def time_based_white(self, light):
        if not self.hue.get_light(light, 'on'): return

        hour = datetime.datetime.now().hour

        # Be nice, show a nice warm light
        # between 00:00 - 08:00
        if hour < 8:
            hour = 24

        ct = (500-154)/24
        self.hue.set_light(light, 'ct', 154 + ct * hour)

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
def set_state():
    return render_template('set-state.html')

@app.route("/set-state/<action>")
def set_state_normal(action="normal"):
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

    return redirect("/set-state", code=302)

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
    for l in house.lights():
        if not house.is_locked(l):
            msg.append("Set light {} to time based white".format(l.name))
            house.time_based_white(l.name)
    msg.append("")
    return "\n".join(msg)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
