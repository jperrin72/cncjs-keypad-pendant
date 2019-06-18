#!/usr/local/bin/python3

import time
import evdev
from select import select
from evdev import ecodes

class CNCjsPad:
	'Manage keyboard events and generate associated gcode'

	def __init__(self):

		# constants and global variables section

		self.CNC_LIMITS={'xmin':0.0, 'xmax':450.0, 'ymin':0.0, 'ymax':1024.0, 'zmin':0.0, 'zmax':35.0}
		self.STEP_INCREMENTS=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]

		self.F_IGNORE_REPEAT=1
		self.F_3TIME=2
		self.ACTIONS=(	{'key':'KEY_0', 'method':CNCjsPad.gcode_Cycle_Start, 	'params':None, 		'flag':None					},
						{'key':'KEY_1', 'method':CNCjsPad.gcode_Feed_Hold, 		'params':None, 		'flag':None					},
						{'key':'H', 	'method':CNCjsPad.gcode_Homing, 		'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_3', 'method':CNCjsPad.gcode_Sleep, 			'params':None, 		'flag':None					},
						{'key':'KEY_4', 'method':CNCjsPad.gcode_Unlock, 		'params':None, 		'flag':None					},
						{'key':'KEY_5', 'method':CNCjsPad.gcode_Start, 			'params':None, 		'flag':None					},
						{'key':'KEY_6', 'method':CNCjsPad.gcode_Pause, 			'params':None, 		'flag':None					},
						{'key':'KEY_7', 'method':CNCjsPad.gcode_Stop, 			'params':None, 		'flag':None					},
						{'key':'KEY_8', 'method':CNCjsPad.gcode_Resume, 		'params':None, 		'flag':None					},
						{'key':'U', 	'method':CNCjsPad.gcode_Unload, 		'params':None, 		'flag':self.F_IGNORE_REPEAT	},
						{'key':'-', 	'method':CNCjsPad.Step_Size, 			'params':-1, 		'flag':None					},
						{'key':'+', 	'method':CNCjsPad.Step_Size, 			'params':+1, 		'flag':None					},
						{'key':'A', 	'method':CNCjsPad.gcode_Move, 			'params':['X',-1], 	'flag':None					},
						{'key':'S', 	'method':CNCjsPad.gcode_Move, 			'params':['X',+1], 	'flag':None					},
						{'key':'Q', 	'method':CNCjsPad.gcode_Move, 			'params':['Y',-1], 	'flag':None					},
						{'key':'Z', 	'method':CNCjsPad.gcode_Move, 			'params':['Y',+1], 	'flag':None					},
						{'key':'W', 	'method':CNCjsPad.gcode_Move, 			'params':['Z',-1], 	'flag':None					},
						{'key':'X', 	'method':CNCjsPad.gcode_Move, 			'params':['Z',+1], 	'flag':None					}
					)

		self.KEY_REPEAT_TIME=1.0
		self.step_index=self.STEP_INCREMENTS.index(1.0)
		self.tool_pos = {'X':0.0,'Y':0.0,'Z':0.0}
		self.prev_key = None
		self.prev_key_time = None
		self.cur_key = None
		self.cur_key_time = None
		self.key_rep_num = 0
		self.gcode_Get_Position()

		# init evdev

		self.devices = []
		for fn in evdev.list_devices():
		  device = evdev.InputDevice(fn)
		  capabilities=device.capabilities().get(ecodes.EV_KEY, [])
		  if  evdev.ecodes.EV_KEY in capabilities:
		    self.devices.append(device)

		self.fds = {dev.fd: dev for dev in self.devices}


	def gcode_Get_Position(self):
		'get x/y/z coordinates from cnc'
		print("tool_pos: %s" % self.tool_pos)

	def foo(self,params):
		print("foo called! params=",params)

	def gcode_Cycle_Start(self,foo):
		'cyclestart'

	def gcode_Feed_Hold(self,foo):
		'feedhold'

	def gcode_Homing(self,foo):
		'homing'
		print("Home called!")

	def gcode_Sleep(self,foo):
		'sleep'

	def gcode_Unlock(self,foo):
		'unlock'

	def gcode_Start(self,foo):
		'gcode:start'

	def gcode_Pause(self,foo):
		'gcode:pause'

	def gcode_Stop(self,foo):
		'gcode:stop'

	def gcode_Resume(self,foo):
		'gcode:resume'

	def gcode_Unload(self,foo):
		'gcode:unload'
		print("Unload called!")

	def gcode_Move(self,args):

		'gcode:G0 [X|Y|Z]<dir*step_size>'
		axis,dir=args
		self.tool_pos[axis]+=dir*self.STEP_INCREMENTS[self.step_index]
		cmd="G0 X%f Y%f Z%f" % (self.tool_pos['X'],self.tool_pos['Y'],self.tool_pos['Z'])
		#print("new pos: %s" % tool_pos)
		self.push_gcode(cmd)

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


	def push_gcode(self,gcode):
		'push a command into gcode buffer'
		print("gcode: %s" % gcode)

	def get_key_press(self):

		self.prev_key = self.cur_key
		self.prev_key_time = self.cur_key_time
		#self.cur_key  = input()

		r, w, x = select(self.devices, [], [])
		for dev in r:
			for event in self.fds[dev.fd].read(): 
				if event.value==1 and event.type==ecodes.EV_KEY: # key down / key event
					self.cur_key=ecodes.KEY[event.code]
					print(self.cur_key)
					#dev.set_led(ecodes.LED_NUML, 1)

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



