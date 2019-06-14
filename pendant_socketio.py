#!/usr/local/bin/python3

import websocket
import sys, asyncore
import jwt
import logging
import socketio # pip install "python-socketio[client]" / https://python-socketio.readthedocs.io/en/latest/client.html

SERVER_ADDRESS = "192.168.0.19" # cncox
#SERVER_ADDRESS = "127.0.0.1" # localhost
SERVER_PORT = 8000

SERIAL_PORT = "/dev/ttyUSB0" # cncox
#SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200
CONTROLLER_TYPE = "Grbl"

SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
#SECRET = "$2a$10$6LHS.kcGOmdGcu2kmbTMUu" # localhost
USER_ID = "" # obtained from ~/.cncrc
USER_NAME = "cncjs-pendant"
USER_PASS = ""
COMMAND="$$"

signed_jwt = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token_url_string = "{}".format(access_token.decode('utf-8'))

logging.getLogger('socketIO-client').setLevel(logging.DEBUG)
logging.basicConfig()

sio = socketio.Client(logger=True)

@sio.event
def message(data):
    print('I received a message!')



@sio.on('connect')
def connect_message():
    print("connect")

@sio.on('startup')
def open_startup(data):
    print("startup=",data)
    sio.emit('open', SERIAL_PORT)

@sio.on('serialport:open')
def serialport_open_message(data):
    print("serialport:open=",data)

@sio.on('serialport:close')
def serialport_close_message(data):
    print("serialport:close")

@sio.on('serialport:read')
def serialport_read_message(data):
    print("serialport:read",data)

@sio.on('serialport:write')
def serialport_write_message(data,sender):
    print("serialport:write=",data)

@sio.on('controller:settings')
def controller_settings_message(controller,settings):
    print("controller:settings=",controller,settings)


@sio.on('controller:state')
def controller_state_message(controller,state):
    print("controller:state=",controller,state)

@sio.on('Grbl:state')
def grbl_state_message(state):
    print("Grbl:state=",state)

@sio.on('feeder:status')
def feeder_status_message(status):
    print("feeder:status=",status)

@sio.on('sender:status')
def sender_status_message(status):
    print("sender:status=",status)

@sio.on('workflow:state')
def workflow_state_message(state):
    print("workflow:state=",state)
    sio.emit('write','G91 X10;\n')


@sio.on('error')
def error_message(data):
    print("error",data)

@sio.on('open')
def open_message(data):
    print("open")


sio.connect('ws://'+SERVER_ADDRESS+':'+str(SERVER_PORT),headers={'Authorization': 'Bearer {}'.format(signed_jwt.decode('utf-8'))})
sio.wait()
#sio.emit('write', SERIAL_PORT, "{};\n".format(COMMAND))
#print("ok4")
