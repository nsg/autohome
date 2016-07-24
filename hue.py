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

@app.route("/hue-status")
def hue_status():
    return render_template('hue-status.html', lamps=house.lights())

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
    app.run(host='0.0.0.0')
