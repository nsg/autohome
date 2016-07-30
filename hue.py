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

from autohome import *

import logging, datetime, time, os
from flask import Flask
from flask import render_template
from flask import redirect

logging.basicConfig()
app = Flask(__name__)
hue = AutoHomeHue()
state = AutoHomeState()
match = AutoHomeMatch()
log = AutoHomeLog()

@app.route("/")
def url_index():
    return render_template('index.html')

@app.route("/hue")
def url_hue():
    return render_template('hue-status.html', lamps=hue.lights())

@app.route("/switch")
def url_switch():
    switches = [
        {"name": "Wall 1", "id": 1 },
        {"name": "Wall 2", "id": 2 },
        {"name": "Door",   "id": 3 }
    ]
    return render_template('switch.html', switches=switches)

@app.route("/log")
def url_log():
    return render_template('log.html', logs=log.load())

@app.route("/set-state")
def url_set_state():
    states = [ "Normal", "Movie", "Bed", "Cozy", "Off" ]
    return render_template('set-state.html', active_state=state.load_state(), states=states)

@app.route("/set-state/<action>")
def url_set_state_action(action="normal"):
    state.dirty()
    set_state(action)
    log.insert("set-stage called, set action to {}".format(action))
    return redirect("/set-state", code=302)

@app.route("/telldus/<int:deviceid>/<int:method>")
def url_telldus_deviceid_method(deviceid, method):
    log.insert("telldus event, deviceid:{} method:{}".format(deviceid, method))
    state.dirty()

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
            if (state.load_state() == "normal"):
                set_state("off")
            if (state.load_state() == "off"):
                set_state("normal")
        if method == 2: # Door closes
            pass

    return redirect("/switch", code=302)

def set_state(action):
    if not state.is_dirty():
        log.insert("Discard set-state, not dirty")
        return False

    log.insert("Set state to {} with curent state {}, is dirty {}".format(action, state.state, state.is_dirty()))

    hour = datetime.datetime.now().hour

    if action == "normal":
        for l in hue.lights():
            if match.hall(l.name):
                hue.brightness(l, 150)
            if match.vardagsrum(l.name):
                hue.brightness(l, 201)

            if match.lamp_kitchen(l.name):
                hue.brightness(l, 201)
            if match.kitchen_bench(l.name):
                if 6 > hour or hour > 18:
                    hue.brightness(l, 201)
                else:
                    l.on = False

            if match.lamp_soffa(l.name):
                l.on = False
            if match.lamp_soffa_large(l.name):
                if 6 > hour or hour > 18:
                    hue.brightness(l, 201)
                else:
                    l.on = False
            if match.bedroom(l.name):
                l.on = False

    if action == "movie":
        for l in hue.lights():
            if match.hall(l.name):
                hue.brightness(l, 50)
            if match.vardagsrum(l.name):
                hue.brightness(l, 50)

            if match.lamp_soffa(l.name):
                hue.brightness(l, 250)
            if match.lamp_soffa_large(l.name):
                hue.brightness(l, 50)

    if action == "cozy":
        for l in hue.lights():
            if match.hall(l.name):
                hue.brightness(l, 50)
            if match.vardagsrum(l.name):
                hue.brightness(l, 140)

            if match.lamp_soffa(l.name):
                l.on = False
            if match.lamp_soffa_large(l.name):
                hue.brightness(l, 150)
            if match.kitchen_bench(l.name):
                hue.brightness(l, 50)
            if match.lamp_kitchen(l.name):
                hue.brightness(l, 90)

    if action == "bed":
        for l in hue.lights():
            if match.hall(l.name):
                l.on = False
            if match.vardagsrum(l.name):
                l.on = False
            if match.soffa(l.name):
                l.on = False
            if match.kitchen(l.name):
                l.on = False
            if match.bedroom(l.name):
                hue.brightness(l, 150)

    if action == "off":
        for l in hue.lights():
            l.on = False

    state.save_state(action)
    state.dirty(False)
    log.insert("State was set to {}".format(action))
    return True

@app.route("/api/hue/<int:lamp_id>/state/<state>")
def url_api_hue_lamp_id_state_state(lamp_id, state):
    for l in hue.lights():
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
    for l in hue.lights():
        if not hue.is_locked(l):
            if (hue.time_based_white(l)):
                msg.append("Set light {} to time based white".format(l.name))

    # Restore the state, if it's dirty
    if set_state(state.load_state()):
        msg.append("State was not dirty, ignore\n")

    for m in msg:
        log.insert(m)
    return "\n".join(msg)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
