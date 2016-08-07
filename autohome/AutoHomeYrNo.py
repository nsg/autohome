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

import xml.etree.ElementTree as ET
import urllib2

class AutoHomeYrNo:
    url = "http://www.yr.no/place/Sweden/Stockholm/Stockholm/forecast.xml"
    root = None

    def load(self):
        xml_string = urllib2.urlopen(self.url).read()
        self.root = ET.fromstring(xml_string)

    def find_next_morning(self):
        for forecast in self.root.iter('forecast'):
            for time in forecast.iter('time'):
                if time.attrib['period'] == '1': # From 06 - 12
                    return time

    def find_next_evening(self):
        for forecast in self.root.iter('forecast'):
            for time in forecast.iter('time'):
                if time.attrib['period'] == '3': # From 18 - 00
                    return time

    def get_precipitation(self, xml):
        for c in xml:
            if c.tag == 'precipitation':
                return c.attrib['value']

    def get_temperature(self, xml):
        for c in xml:
            if c.tag == 'temperature':
                return c.attrib['value']

