#!/usr/local/bin/python3

import websocket
import sys, asyncore
import jwt
import logging
import socketio # pip install "python-socketio[client]" / https://python-socketio.readthedocs.io/en/latest/client.html
from socketio import packet

class CNCjsGrbl:
	'Implement communication through websockets to Grbl'
	def __init__(self,ip,port,serial,secret=None):
		self.server_ip=ip
		self.server_port=port
		self.serial_port=serial
		self.serial_baud=115200
		self.controller_type="Grbl"
		self.user_id=""
		self.user_name="cncjs-pendant"
		self.user_pass=""
		self.workflow_state=''
		self.ws_secret=secret
		self.sio = socketio.Client(logger=True)
		print(self,ip,port,serial,secret)

	def disconnect(self):
		self.sio.disconnect()

	def connect(self):

		# define websocket handlers

		@self.sio.on('connect')
		def connect_message():
		    print("connect")

		@self.sio.on('startup')
		def open_startup(data):
		    self.startup_data=data
		    self.send('open',{'baudrate':self.serial_baud,'controllerType':self.controller_type})

		@self.sio.on('serialport:open')
		def serialport_open_message(data):
		    self.serial_state=data

		@self.sio.on('serialport:close')
		def serialport_close_message(data):
		    print("serialport:close")

		@self.sio.on('serialport:read')
		def serialport_read_message(data):
		    print("serialport:read",data)

		@self.sio.on('serialport:change')
		def serialport_read_message(data):
		    print("serialport:change",data)

		@self.sio.on('serialport:write')
		def serialport_write_message(data,sender):
			print("serialport:write=",data)

		@self.sio.on('controller:settings')
		def controller_settings_message(controller,settings):
			self.controller_settings=settings

		@self.sio.on('Grbl:state')
		def grbl_state_message(state):
		    self.controller_state=state
		    self.active_state=state['status']['activeState']
		    print("activeState=",self.active_state)

		@self.sio.on('controller:state')
		def controller_state_message(controller,state):
		    self.controller_state=state
		    self.active_state=state['status']['activeState']
		    print("activeState=",self.active_state)

		@self.sio.on('workflow:state')
		def workflow_state_message(state):
		    self.workflow_state=state

		@self.sio.on('feeder:status')
		def feeder_status_message(status):
		    self.feeder_status=status	

		@self.sio.on('sender:status')
		def sender_status_message(status):
		    self.sender_status=status	

		@self.sio.on('error')
		def error_message(data):
		    print("error",data)

		# connect to websocket service
		self.access_token = jwt.encode({'id': self.user_id, 'name': self.user_name}, self.ws_secret, algorithm='HS256')
		self.access_token_url_string = "{}".format(self.access_token.decode('utf-8'))
		self.sio.connect('ws://'+self.server_ip+':'+str(self.server_port),headers={'Authorization': 'Bearer {}'.format(self.access_token.decode('utf-8'))})


	def send(self,event,data=None):

		self.sio._send_packet(packet.Packet(	packet.EVENT,
												namespace=None,
												data=[event,self.serial_port,data],
												id=None,
												binary=None))

	def wait(self):
		while (self.workflow_state!='idle'):
			self.sio.sleep(0.1)

"""
'server_ip': '127.0.0.1',
'server_port': 8000,
'serial_port': '/dev/tty.MALS',
'serial_baud': 115200,
'controller_type': 'Grbl',
'user_id': '',
'user_name': 'cncjs-pendant',
'user_pass': '',
'ws_secret': '$2a$10$6LHS.kcGOmdGcu2kmbTMUu',
'sio': <socketio.client.Client object at 0x10ce2f2e8>,
'access_token': b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IiIsIm5hbWUiOiJjbmNqcy1wZW5kYW50In0.aDWMfveVjKazAw1GvQ-XcxCE-vE4cfeYzTTdNIrdvck',
'access_token_url_string': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IiIsIm5hbWUiOiJjbmNqcy1wZW5kYW50In0.aDWMfveVjKazAw1GvQ-XcxCE-vE4cfeYzTTdNIrdvck',
'startup_data': {'loadedControllers': ['Grbl', 'Marlin', 'Smoothie', 'TinyG'], 'baudrates': [], 'ports': []},
'serial_state': {'port': '/dev/tty.MALS', 'baudrate': 115200, 'controllerType': 'Grbl', 'inuse': True},
'controller_settings': {'version': '', 'parameters': {}, 'settings': {}},
'controller_state': {'status': {'activeState': '', 'mpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'wpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'ov': []}, 'parserstate': {'modal': {'motion': 'G0', 'wcs': 'G54', 'plane': 'G17', 'units': 'G21', 'distance': 'G90', 'feedrate': 'G94', 'program': 'M0', 'spindle': 'M5', 'coolant': 'M9'}, 'tool': '', 'feedrate': '', 'spindle': ''}},
'feeder_status': 	{'hold': False, 'holdReason': None, 'queue': 0, 'pending': False, 'changed': False},
'sender_status': 	{'sp': 1, 'hold': False, 'holdReason': None, 'name': '', 'context': {}, 'size': 0, 'total': 0, 'sent': 0, 'received': 0, 'startTime': 0, 'finishTime': 0, 'elapsedTime': 0, 'remainingTime': 0},
'workflow_state': 'idle'}
"""
