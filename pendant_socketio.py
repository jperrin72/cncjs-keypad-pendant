#!/usr/local/bin/python3

import websocket
import sys, asyncore
import jwt
import logging
import socketio # pip install "python-socketio[client]" / https://python-socketio.readthedocs.io/en/latest/client.html

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

access_token = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token_url_string = "{}".format(access_token.decode('utf-8'))

logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

sio = socketio.Client(logger=True)

sio.connect('http://'+SERVER_ADDRESS+':'+str(SERVER_PORT)+'/socket.io/?tocken='+access_token_url_string,{},['polling'])
print("ok1")

sio.sleep(1)
print("ok2")

sio.emit('open',  {'ports': SERIAL_PORT,'baudrate': SERIAL_BAUDRATE, 'controllerType': CONTROLLER_TYPE})

print("ok3")

