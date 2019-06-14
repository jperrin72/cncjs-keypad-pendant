#!/usr/local/bin/python3

import websocket
import requests # pip install requests / https://pypi.org/project/requests/
import sys, asyncore
import jwt
import logging
from socketIO_client import SocketIO, LoggingNamespace # pip install -U socketIO-client / pip install socketIO-client==0.5.7.2 / https://github.com/invisibleroads/socketIO-client



#SERVER_ADDRESS = "192.168.0.19" # cncox
SERVER_ADDRESS = "127.0.0.1" # localhost
SERVER_PORT = 8000

SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200
CONTROLLER_TYPE = "Grbl"

#SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
SECRET = "$2a$10$6LHS.kcGOmdGcu2kmbTMUu" # localhost
USER_ID = "" # obtained from ~/.cncrc
USER_NAME = "cnc"
USER_PASS = ""

signed_jwt = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token_url_string = "{}".format(access_token.decode('utf-8'))

logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

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

print(str(LoggingNamespace))

loop = True
with SocketIO(SERVER_ADDRESS, SERVER_PORT, LoggingNamespace, params={'token':'{}'.format(signed_jwt),'transport': ['xhr-polling']}, headers={'Authorization': 'Bearer {}'.format(signed_jwt.decode('utf-8'))}) as socketIO:
  socketIO.on('connect', on_connect)
  while loop:
    socketIO.wait(seconds=WAIT_DURATION)

# problem sur reception sid 