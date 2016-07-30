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

import re

class AutoHomeMatch:

    def vardagsrum(self, lamp_name):
        if re.match(r'^Vardagsrum', lamp_name):
            return True
        return False

    def hall(self, lamp_name):
        if re.match(r'^Hall', lamp_name):
            return True
        return False

    def bedroom(self, lamp_name):
        if re.match(r'^Bedroom', lamp_name):
            return True
        return False

    def kitchen(self, lamp_name):
        if re.match(r'^Kitchen', lamp_name):
            return True
        return False

    def soffa(self, lamp_name):
        if re.match(r'^Soffa', lamp_name):
            return True
        return False

    def kitchen_bench(self, lamp_name):
        if re.match(r'^Kitchen Bench', lamp_name):
            return True
        return False

    def lamp_soffa(self, lamp_name):
        return lamp_name == "Soffa"

    def lamp_soffa_large(self, lamp_name):
        return lamp_name == "Soffa Large"

    def lamp_kitchen(self, lamp_name):
        return lamp_name == "Kitchen"
