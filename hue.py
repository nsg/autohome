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
from flask import request

logging.basicConfig()
app = Flask(__name__)
hue = AutoHomeHue()
state = AutoHomeState()
match = AutoHomeMatch()
log = AutoHomeLog()
sonos = AutoHomeSonos()
yrno = AutoHomeYrNo()

@app.route("/")
def url_index():
    return render_template('index.html')

@app.route("/hue")
def url_hue():
    return render_template('hue-status.html', lamps=hue.lights())

@app.route("/switch")
def url_switch():
    switches = [
        {"name": "Wall Switch - Button 1",  "id": 1 },
        {"name": "Wall Switch - Button 2",  "id": 2 },
        {"name": "Door Sensor",             "id": 3 },
        {"name": "Kitcken Movement Sensor", "id": 4 }
    ]
    return render_template('switch.html', switches=switches, telldus=state.telldus_state)

@app.route("/sonos")
def url_sonos():
    return render_template('sonos.html', speakers=sonos.list_soco())

@app.route("/log")
def url_log():
    return render_template('log.html', logs=log.load())

@app.route("/set-state")
def url_set_state():
    states = [ "Normal", "Movie", "Cozy", "Bed", "Morning", "Off" ]
    return render_template('set-state.html', active_state=state.load_state(), states=states)

@app.route("/set-state/<action>")
def url_set_state_action(action="normal"):
    state.dirty()
    set_state(action)
    log.insert("set-stage called, set action to {}".format(action))
    return redirect("/set-state", code=302)

@app.route("/sonos/set")
def url_sonos_set():
    name = request.args.get('name')
    volume = request.args.get('volume')

    if name == "all":
        for s in sonos.list_soco():
            s.volume = volume
    else:
        for s in sonos.list_soco():
            if s.player_name == name:
                s.volume = volume

    return redirect("/sonos", code=302)

@app.route("/sonos/set/group_all")
def url_sonos_set_group_all():
    sonos.group_speakers()
    return redirect("/sonos", code=302)

@app.route("/telldus/<int:deviceid>/<int:method>")
def url_telldus_deviceid_method(deviceid, method):

    # The door sensor sends several pulses, only accept one every 10s
    if deviceid == 3 and state.telldus_time_since_command() < 10:
        log.insert("Throttled telldus event, deviceid:{} method:{} time:{}".format(
            deviceid, method, state.telldus_time_since_command()))
        return "Throttled"
    # For the rest, 2s will do
    elif state.telldus_time_since_command() < 2:
        log.insert("Throttled telldus event, deviceid:{} method:{} time:{}".format(
            deviceid, method, state.telldus_time_since_command()))
        return "Throttled"

    log.insert("Accepted telldus event, deviceid:{} method:{}".format(deviceid, method))
    state.telldus(deviceid, method)

    cur_state = state.load_state()

    # Wall Switch - Button 1
    if deviceid == 1:
        state.dirty()
        if method == 1:
            set_state("normal")
        else:
            set_state("off")

    # Wall Switch - Button 2
    if deviceid == 2:
        state.dirty()
        if method == 1:
            set_state("cozy")
        else:
            set_state("bed")

    # Door Switch
    if deviceid == 3:
        state.dirty()
        if method == 1: # Door opens
            if state.load_state() == "off":
                set_state("normal")
            else:
                set_state("off")
        if method == 2: # Door closes
            pass

    # Kitchen Movement
    if deviceid == 4:
        for l in hue.lights():
            if match.kitchen(l.name):
                if cur_state == "normal":
                    if method == 1:
                        if match.lamp_kitchen(l.name):
                            hue.brightness(l, 201)
                        if match.kitchen_bench(l.name):
                            hue.brightness(l, 201)
                    if method == 2:
                        if match.lamp_kitchen(l.name):
                            hue.brightness(l, 150)
                        if match.kitchen_bench(l.name):
                            hue.brightness(l, 50)
                elif cur_state == "cozy":
                    if method == 1:
                        if match.kitchen_bench(l.name):
                            hue.brightness(l, 90)
                    if method == 2:
                        if match.kitchen_bench(l.name):
                            hue.brightness(l, 50)
                elif cur_state == "off":
                    if method == 1:
                        if match.kitchen_bench(l.name):
                            hue.brightness(l, 50)
                    if method == 2:
                        if match.kitchen_bench(l.name):
                            l.on = False
            if match.bedroom(l.name):
                if l.on and method == 2:
                    if cur_state == "normal" or cur_state == "cozy":
                        l.on = False

    state.telldus_record_timestamp()
    return redirect("/switch", code=302)

def sonos_normal():
    hour = datetime.datetime.now().hour

    for s in sonos.list_soco():
        if 8 < hour and hour < 23:
            if s.volume > 10:
                s.volume = 10
                log.insert("Set volume to 10")
        else:
            if s.volume > 8:
                s.volume = 8
                log.insert("Set volume to 8")

def set_state(action):
    if not state.is_dirty(): return False

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

        sonos_normal()

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

        sonos_normal()

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
                hue.brightness(l, 120, 1)   # Set it quite bright
                hue.brightness(l, 60, 3000) # Over 5 minutes, make it quite dark

    if action == "morning":
        log.insert("Load weather data from yr.no")
        yrno.load() # Load fresh weather data
        for l in hue.lights():
            if match.bedroom(l.name):
                hue.brightness(l, 254, 9000) # Over 15 minutes, make it bright
            if l.name == "Hall spot 1":
                hue.brightness(l, 254)
            if l.name == "Hall spot 2":
                t = yrno.get_temperature(yrno.find_next_morning())
                p = yrno.get_precipitation(yrno.find_next_morning())
                if float(p) > 0.5:
                    hue.color(l, hue=46920) # blue
                    log.insert("Set hue blue b/c forcast for this morning is rain")
                else:
                    hue_color = 12750 - (12750/30) * int(t)
                    hue.color(l, hue=hue_color + 1)
                    log.insert("Set hue to {} b/c the forcast for this morning is {}C".format(hue_color, t))
                hue.lock(l)
            if l.name == "Hall spot 3":
                t = yrno.get_temperature(yrno.find_next_evening())
                p = yrno.get_precipitation(yrno.find_next_evening())
                p = 0.7
                if float(p) > 0.5:
                    hue.color(l, hue=46920) # blue
                    log.insert("Set hue to blue b/c the forcast for this evening is rain")
                else:
                    hue_color = 12750 - (12750/30) * int(t)
                    hue.color(l, hue=hue_color + 1)
                    log.insert("Set hue to {} b/c the forcast for this evening is {}C".format(hue_color, t))
                hue.lock(l)

    if action == "off":
        for l in hue.lights():
            l.on = False
            if (hue.is_locked(l)):
                hue.unlock(l)
        for s in sonos.list_soco():
            s.volume = 0
            log.insert("Set volume to 0")

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
