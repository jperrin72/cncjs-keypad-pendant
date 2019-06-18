#!/usr/local/bin/python3

import websocket
import sys, asyncore
import jwt
import logging
import socketio # pip install "python-socketio[client]" / https://python-socketio.readthedocs.io/en/latest/client.html
from socketio import packet


"""
connect
startup= {'loadedControllers': ['Grbl', 'Marlin', 'Smoothie', 'TinyG'], 'baudrates': [], 'ports': []}
feeder:status= {'hold': False, 'holdReason': None, 'queue': 0, 'pending': False, 'changed': False}
sender:status= {'sp': 1, 'hold': False, 'holdReason': None, 'name': '', 'context': {}, 'size': 0, 'total': 0, 'sent': 0, 'received': 0, 'startTime': 0, 'finishTime': 0, 'elapsedTime': 0, 'remainingTime': 0}

workflow:state= idle
serialport:open= {'port': '/dev/tty.MALS', 'baudrate': 115200, 'controllerType': 'Grbl', 'inuse': True}
serialport:change {'port': '/dev/tty.MALS', 'inuse': True}
controller:settings= Grbl {'version': '', 'parameters': {}, 'settings': {}}
controller:state= Grbl {'status': {'activeState': '', 'mpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'wpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'ov': []}, 'parserstate': {'modal': {'motion': 'G0', 'wcs': 'G54', 'plane': 'G17', 'units': 'G21', 'distance': 'G90', 'feedrate': 'G94', 'program': 'M0', 'spindle': 'M5', 'coolant': 'M9'}, 'tool': '', 'feedrate': '', 'spindle': ''}}

Grbl:state= {'status': {'activeState': '', 'mpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'wpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'ov': []}, 'parserstate': {'modal': {'motion': 'G0', 'wcs': 'G54', 'plane': 'G17', 'units': 'G21', 'distance': 'G90', 'feedrate': 'G94', 'program': 'M0', 'spindle': 'M5', 'coolant': 'M9'}, 'tool': '', 'feedrate': '', 'spindle': ''}}
serialport:write= $H
serialport:close
"""

SERVER_ADDRESS = "192.168.0.19" # cncox
SERVER_PORT = 8000
SERIAL_PORT = "/dev/ttyUSB0" # cncox
SERIAL_BAUDRATE = 115200
SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
CONTROLLER_TYPE = "Grbl"

"""
SERVER_ADDRESS = "127.0.0.1" # localhost
SERVER_PORT = 8000
SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200
SECRET = "$2a$10$6LHS.kcGOmdGcu2kmbTMUu" # localhost
CONTROLLER_TYPE = "Grbl"
"""

USER_ID = "" # obtained from ~/.cncrc
USER_NAME = "cncjs-pendant"
USER_PASS = ""

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
    sio._send_packet(packet.Packet( packet.EVENT,
                                    namespace=None,
                                    data=['open',SERIAL_PORT,{'baudrate':SERIAL_BAUDRATE,'controllerType':CONTROLLER_TYPE}],
                                    id=None,
                                    binary=None))

@sio.on('serialport:open')
def serialport_open_message(data):
    print("serialport:open=",data)

@sio.on('serialport:close')
def serialport_close_message(data):
    print("serialport:close")
    #sio.disconnect()

@sio.on('serialport:read')
def serialport_read_message(data):
    print("serialport:read",data)


@sio.on('serialport:change')
def serialport_read_message(data):
    print("serialport:change",data)

@sio.on('serialport:write')
def serialport_write_message(data,sender):
    print("serialport:write=",data)
    """sio._send_packet(packet.Packet( packet.EVENT,
                                namespace=None,
                                data=["close",SERIAL_PORT],
                                id=None,
                                binary=None))
"""
@sio.on('controller:settings')
def controller_settings_message(controller,settings):
    print("controller:settings=",controller,settings)


@sio.on('controller:state')
def controller_state_message(controller,state):
    print("controller:state=",controller,state)

@sio.on('Grbl:state')
def grbl_state_message(state):
    print("Grbl:state=",state)
    sio._send_packet(packet.Packet( packet.EVENT,
                                    namespace=None,
                                    data=["write",SERIAL_PORT,"$H\r"],
                                    id=None,
                                    binary=None))

@sio.on('feeder:status')
def feeder_status_message(status):
    print("feeder:status=",status)

@sio.on('sender:status')
def sender_status_message(status):
    print("sender:status=",status)

@sio.on('workflow:state')
def workflow_state_message(state):
    print("workflow:state=",state)
    """if state.startswith('idle'):
        sio._send_packet(packet.Packet( packet.EVENT,
                                        namespace=None,
                                        data=["write",SERIAL_PORT,"$H\r"],
                                        id=None,
                                        binary=None))
                                        """

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
