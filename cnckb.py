# inspired by cncjs-pendant-raspi-gpio: https://github.com/cncjs/cncjs-pendant-raspi-gpio
# This CNC.js pendant opens a connection to the CNC.js web server, opens a serial port connection,
# writes a command, then terminates.

import jwt
import logging
from socketIO_client import SocketIO, LoggingNamespace

SERVER_ADDRESS = "192.168.0.19"
SERVER_PORT = 8000

SERIAL_PORT = "ENTER_SERIAL_PORT_HERE" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200

SECRET = "ENTER_SECRET_HERE" # obtained from ~/.cncrc (home directory of user that runs CNC.js)
USER_ID = "ENTER_USER_ID_HERE" # obtained from ~/.cncrc
USER_NAME = "ENTER_USERNAME_HERE"

CONTROLLER_TYPE = "Grbl"
COMMAND = "$H" # run homing cycle

access_token = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token_url_string = "token={}".format(access_token.decode('utf-8'))

logging.getLogger('requests').setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG)

def on_connect(*args):
  print('connect')
  socketIO.emit('open', SERIAL_PORT, {'baudrate': SERIAL_BAUDRATE, 'controllerType': CONTROLLER_TYPE})
  socketIO.on('serialport:open', on_serial_port_open)

def on_serial_port_open(*args):
  print('serialport:open')
  socketIO.emit('write', SERIAL_PORT, "{};\n".format(COMMAND))
  socketIO.on('serialport:write', on_serial_port_write)

def on_serial_port_write(*args):
  print("serialport:write")
  global loop
  loop = False

loop = True
with SocketIO(SERVER_ADDRESS, SERVER_PORT, LoggingNamespace, params={'token': access_token}) as socketIO:
  socketIO.on('connect', on_connect)
  while loop:
    socketIO.wait(seconds=WAIT_DURATION)
