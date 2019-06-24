#!/usr/local/bin/python3

import time
import sys
import evdev # pip3 install evdev
from collections import deque
from select import select
from evdev import ecodes
from math import floor
from threading import Thread, RLock

class CNCjsPadLed(Thread):

	def __init__(self):
		'thread to manage led'
		Thread.__init__(self)
		self.LED_SEQ=(	{'state':'Off', 	'sequence':0b00000000000000000000000000000000, 'repeat': False	},
						{'state':'On',		'sequence':0b11111111111111111111111111111111, 'repeat': True	},
						{'state':'Sleep',	'sequence':0b01111111111111111111111111111111, 'repeat': True	},
						{'state':'Hold',	'sequence':0b00111111111111111111111111111111, 'repeat': True	},
						{'state':'Idle',	'sequence':0b11111111111111110000000000000000, 'repeat': True	},
						{'state':'Alarm', 	'sequence':0b11100111001110011111111111111100, 'repeat': True	},
						{'state':'Task', 	'sequence':0b10101010101010101010101010101010, 'repeat': True	}
					)

		self.set_led_sequence('Sleep')
		self.dev=None

	def get_led_sequence(self):
		'get current animation sequence for led'
		print('led_sequence=',self.led_sequence['state'])
		return self.led_sequence['state']

	def set_led_sequence(self,state='Off'):
		'set current animation sequence for led'
		self.led_sequence=list(filter(lambda seq: seq['state'] == state, self.LED_SEQ))[0]
		print('led_sequence=',self.led_sequence['state'])

	def set_dev(self,dev=None):
		if (self.dev==None):
			self.dev=dev
			print('dev=',dev)

	def run(self):
		'animate led according to sequence (period=1s)'
		while (True):
			index=int(32.0*(time.time()%1))
			led=(self.led_sequence['sequence']>>index)&1
			if self.dev is not None:
				self.dev.set_led(ecodes.LED_NUML, led)
			time.sleep(1.0/64)

class CNCjsPad:
	'Manage keyboard events and generate associated gcode'

	def __init__(self):

		# constants and global variables section

		self.CNC_LIMITS={'xmin':0.0, 'xmax':450.0, 'ymin':0.0, 'ymax':1024.0, 'zmin':0.0, 'zmax':35.0}
		self.STEP_INCREMENTS=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]

		self.F_IGNORE_REPEAT=1
		self.F_3TIME=2
		self.ACTIONS=(
						{'key':'KEY_HOMEPAGE', 	'method':CNCjsPad.task_Macro, 			'params':'Go Home', 'flag':self.F_3TIME			},
						{'key':'KEY_TAB', 		'method':CNCjsPad.task_Macro, 			'params':'Tool up', 'flag':self.F_3TIME			},
						{'key':'KEY_MAIL', 		'method':CNCjsPad.gcode_Reset, 			'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_CALC', 	    'method':CNCjsPad.task_Command,			'params':'Halt', 	'flag':self.F_3TIME			},
						{'key':'KEY_NUMLOCK',   'method':CNCjsPad.gcode_Start, 			'params':None, 		'flag':None					},
						{'key':'KEY_KPSLASH',   'method':CNCjsPad.gcode_Pause, 			'params':None, 		'flag':None					},
						{'key':'KEY_KPASTERISK','method':CNCjsPad.gcode_Stop, 			'params':None, 		'flag':None					},
						{'key':'KEY_BACKSPACE', 'method':CNCjsPad.gcode_Resume, 		'params':None, 		'flag':None					},
						{'key':'KEY_KP7', 	    'method':CNCjsPad.gcode_Homing, 		'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_KP8', 	    'method':CNCjsPad.gcode_Move, 			'params':['y',+1], 	'flag':None					},
						{'key':'KEY_KP9', 	    'method':CNCjsPad.gcode_Move, 			'params':['z',+1], 	'flag':None					},
						{'key':'KEY_KPMINUS', 	'method':CNCjsPad.Step_Size, 			'params':-1, 		'flag':None					},
						{'key':'KEY_KP4', 	    'method':CNCjsPad.gcode_Move, 			'params':['x',-1], 	'flag':None					},
						{'key':'KEY_KP5', 	    'method':CNCjsPad.gcode_SetHome, 		'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_KP6', 	    'method':CNCjsPad.gcode_Move, 			'params':['x',+1], 	'flag':None					},
						{'key':'KEY_KPPLUS', 	'method':CNCjsPad.Step_Size, 			'params':+1, 		'flag':None					},
						{'key':'KEY_KP1',       'method':CNCjsPad.gcode_Sleep, 			'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_KP2', 	    'method':CNCjsPad.gcode_Move, 			'params':['y',-1], 	'flag':None					},
						{'key':'KEY_KP3', 	    'method':CNCjsPad.gcode_Move, 			'params':['z',-1], 	'flag':None					},
						{'key':'KEY_KP0',       'method':CNCjsPad.gcode_Unlock, 		'params':None, 		'flag':None					},
						{'key':'KEY_0',         'method':CNCjsPad.gcode_Feed_Hold, 		'params':None, 		'flag':None					}, #key 000
						{'key':'KEY_KPDOT', 	'method':CNCjsPad.task_Laser_Test, 		'params':None, 		'flag':self.F_IGNORE_REPEAT	},
						{'key':'KEY_KPENTER',   'method':CNCjsPad.gcode_Cycle_Start, 	'params':None, 		'flag':None					}
					)

		self.KEY_REPEAT_TIME=1.0
		self.step_index=self.STEP_INCREMENTS.index(1.0)
		self.tool_pos = {'x':0.0,'y':0.0,'z':0.0}
		self.prev_key = None
		self.prev_key_time = None
		self.cur_key = None
		self.cur_key_time = None
		self.key_rep_num = 0
		self.gcode_queue = deque('')
		self.led = CNCjsPadLed()
		self.led.start()

		#self.gcode_Get_Position()

		# init evdev

		self.devices = []
		for fn in evdev.list_devices():
		  device = evdev.InputDevice(fn)
		  capabilities=device.capabilities().get(ecodes.EV_KEY, [])
		  if  evdev.ecodes.EV_KEY in capabilities:
		    self.devices.append(device)

		self.fds = {dev.fd: dev for dev in self.devices}
		#print("devices=",self.devices)

	def gcode_Set_Position(self,pos={'xmin':0.0,'ymin':0.0,'zmin':0.0}):
		'get x/y/z coordinates from cnc'
		self.tool_pos['x']=float(pos['x'])
		self.tool_pos['y']=float(pos['y'])
		self.tool_pos['z']=float(pos['z'])
		#print("tool_pos: %s" % self.tool_pos)

	def gcode_Set_Limits(self,x,y,z):
		self.CNC_LIMITS={'xmin':1.0-floor(float(x)), 'xmax':-1.0, 'ymin':1.0-floor(float(y)), 'ymax':-1.0, 'zmin':1.0-floor(float(z)), 'zmax':-1.0}
		print("tool_limits: %s" % self.CNC_LIMITS)

	def gcode_Get_Position(self):
		'get x/y/z coordinates from cnc'
		print("tool_pos: %s" % self.tool_pos)

	def foo(self,params):
		print("foo called! params=",params)

	def gcode_Cycle_Start(self,foo):
		'cyclestart'
		print("cyclestart")
		self.push_gcode(data='~\n',wait=False)

	def gcode_Feed_Hold(self,foo):
		'feedhold'
		print("feedhold")
		self.push_gcode(data='!\n',wait=False)

	def gcode_Homing(self,foo):
		'homing'
		print("homing")
		self.push_gcode(data='$H\n',wait=True)

	def gcode_Sleep(self,foo):
		'sleep'
		print("sleep")
		self.push_gcode(data='$SLP\n',wait=False)

	def gcode_Unlock(self,foo):
		'unlock'
		print("unlock")
		self.push_gcode(data='$X\n',wait=False)
	
	def gcode_Reset(self,foo):
		'reset'
		print("reset")
		self.push_gcode(data='\x18',wait=False)

	def gcode_Start(self,foo):
		'gcode:start'
		print("gcode:start")
		self.push_gcode(event='command',data='gcode:start',wait=False)

	def gcode_Pause(self,foo):
		'gcode:pause'
		print("gcode:pause")
		self.push_gcode(event='command',data='gcode:pause',wait=False)

	def gcode_Stop(self,foo):
		'gcode:stop'
		print("gcode:stop")
		self.push_gcode(event='command',data='gcode:stop',wait=False)
		
	def gcode_Resume(self,foo):
		'gcode:resume'
		print("gcode:resume")
		self.push_gcode(event='command',data='gcode:resume',wait=False)
		
	def gcode_Unload(self,foo):
		'gcode:unload'
		print("gcode:unload")
		self.push_gcode(event='command',data='gcode:unload',wait=False)

	def gcode_SetHome(self,foo):
		'set working home position'
		print("gcode:sethome")
		self.push_gcode(data='G10 L20 P1 X0 Y0 Z0\n?\n',wait=True)

	def task_Command(self,title):
		'command:start'
		led=self.led.get_led_sequence()
		self.led.set_led_sequence('Task')
		print("command:start=",title)
		self.push_gcode(event='command:start',data=title,wait=False)
		self.led.set_led_sequence(led)

	def task_Macro(self,title):
		'command:start'
		led=self.led.get_led_sequence()
		self.led.set_led_sequence('Task')
		print("macro:start=",title)
		self.push_gcode(event='macro:start',data=title,wait=False)
		self.led.set_led_sequence(led)


	def task_Laser_Test(self,foo):
		'lasertest:on'
		'''
		42["command","/dev/ttyUSB0","lasertest:on",power,waitms,maxpower]
		'''
		print("lasertest:on")
		self.push_gcode(event='command',data=["lasertest:on",1,250,100],wait=True)



	def gcode_Move(self,args):
		'gcode:G53 [X|Y|Z]<dir*step_size>'
		axis,dir=args
		#print(axis,dir,self.tool_pos,self.step_index)
		self.tool_pos[axis]+=dir*self.STEP_INCREMENTS[self.step_index]

		if self.tool_pos[axis]<self.CNC_LIMITS[axis+'min']:
			self.tool_pos[axis]=self.CNC_LIMITS[axis+'min']

		if self.tool_pos[axis]>self.CNC_LIMITS[axis+'max']:
			self.tool_pos[axis]=self.CNC_LIMITS[axis+'max']

		gcode="G53 %s%f F1000\n" % (axis.upper(),self.tool_pos[axis])
		self.push_gcode(data=gcode,wait=False)

	def Step_Size(self,dir):
		'set step size mm'
		self.step_index+=dir
		if self.step_index<0:
			self.step_index+=1
		if self.step_index==len(self.STEP_INCREMENTS):
			self.step_index-=1
		print("step size: %.2fmm" % self.STEP_INCREMENTS[self.step_index])

	def decode_key(self,key):
		action=''
		#print('key=',key)
		for action in [rec for rec in self.ACTIONS if rec['key'] == key]:
			pass
		#print(action)
		if action!='':
			ignore=False
			if action['flag']==self.F_3TIME:
				if self.key_rep_num==3:
					self.key_rep_num=0
				else:
					ignore=True
			if action['flag']==self.F_IGNORE_REPEAT:
				if self.key_rep_num>1:
					ignore=True
			if not ignore:
				action['method'](self,action['params'])


	def push_gcode(self,event='write',data=None,wait=True):
		'push a command into gcode buffer'
		message={'event':event,'data':data,'wait':wait}
		self.gcode_queue.append(message)
		#print("gcode: %s" % gcode)

	def gcode_ready(self):
		'return True if gcode is ready for processing'
		return (len(self.gcode_queue)>0)

	def pop_gcode(self):
		'pop a command from gcode buffer'
		message = self.gcode_queue.popleft()
		print("message: %s" % message)
		return message

	def get_key_press(self):

		keypress=False
		self.prev_key = self.cur_key
		self.prev_key_time = self.cur_key_time
		#self.cur_key  = input()

		r, w, x = select(self.devices, [], [])
		for dev in r:
			for event in self.fds[dev.fd].read(): 
				if event.value==1 and event.type==ecodes.EV_KEY: # key down / key event
					self.cur_key=ecodes.KEY[event.code]
					keypress=True
					self.led.set_dev(dev)
					#dev.set_led(ecodes.LED_NUML, 1)

		if (keypress):
			self.cur_key_time = time.time()

			if self.prev_key_time is None:
				self.key_delta_time = 0.0
			else:
				self.key_delta_time = self.cur_key_time - self.prev_key_time 

			if (self.cur_key == self.prev_key) and (self.key_delta_time<=self.KEY_REPEAT_TIME):
				self.key_rep_num+=1
			else:
				self.key_rep_num=1

			print(self.cur_key,self.prev_key,self.key_delta_time,self.key_rep_num)
			self.decode_key(self.cur_key)



