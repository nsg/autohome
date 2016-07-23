#!/usr/bin/python

from phue import Bridge
import logging, datetime, time, os

class House:

    hue = None

    def __init__(self):
        self.hue = Bridge(ip='10.90.0.106', config_file_path="/var/lib/hue/hue.conf")

    def lights(self):
        return self.hue.lights

    def work_morning(self):
        lamps = ['Bedroom', 'Hall spot 1']
        self.hue.set_light(lamps, {
            'transitiontime' : 6000,
            'on' : True,
            'bri' : 254}
        )

    def good_night(self):
        for l in self.hue.lights:
            l.on = False

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

while True:
    s = time.strftime("%H:%M:%S")

    # Morning light
    if s == "07:55:30":
        house.work_morning()

    # Every minute
    if datetime.datetime.now().second == 0:
        for l in house.lights():
            house.time_based_white(l.name)

    time.sleep(1)
