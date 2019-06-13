#!/usr/local/bin/python3
# inspired by cncjs-pendant-raspi-gpio: https://github.com/cncjs/cncjs-pendant-raspi-gpio
# This CNC.js pendant opens a connection to the CNC.js web server, opens a serial port connection,
# writes a command, then terminates.

import jwt # pip install pyjwt
import logging

