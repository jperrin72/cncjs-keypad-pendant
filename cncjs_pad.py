#!/usr/local/bin/python3

import time
import evdev # pip3 install evdev
from collections import deque
from select import select
from evdev import ecodes
from math import floor

class CNCjsPad:
	'Manage keyboard events and generate associated gcode'

	def __init__(self):

		# constants and global variables section

		self.CNC_LIMITS={'xmin':0.0, 'xmax':450.0, 'ymin':0.0, 'ymax':1024.0, 'zmin':0.0, 'zmax':35.0}
		self.STEP_INCREMENTS=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]

		self.F_IGNORE_REPEAT=1
		self.F_3TIME=2
		self.ACTIONS=(	{'key':'KEY_KPENTER', 'method':CNCjsPad.gcode_Cycle_Start, 	'params':None, 		'flag':None					},
						{'key':'KEY_0', 'method':CNCjsPad.gcode_Feed_Hold, 		'params':None, 		'flag':None					},
						{'key':'KEY_KP7', 	'method':CNCjsPad.gcode_Homing, 		'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_KP1', 'method':CNCjsPad.gcode_Sleep, 			'params':None, 		'flag':self.F_3TIME					},
						{'key':'KEY_KP0', 'method':CNCjsPad.gcode_Unlock, 		'params':None, 		'flag':None					},
						{'key':'KEY_NUMLOCK', 'method':CNCjsPad.gcode_Start, 			'params':None, 		'flag':None					},
						{'key':'KEY_KPSLASH', 'method':CNCjsPad.gcode_Pause, 			'params':None, 		'flag':None					},
						{'key':'KEY_KPASTERISK', 'method':CNCjsPad.gcode_Stop, 			'params':None, 		'flag':None					},
						{'key':'KEY_BACKSPACE/', 'method':CNCjsPad.gcode_Resume, 		'params':None, 		'flag':None					},
						{'key':'KEY_KPDOT', 	'method':CNCjsPad.gcode_Unload, 		'params':None, 		'flag':self.F_IGNORE_REPEAT	},
						{'key':'KEY_KPMINUS', 	'method':CNCjsPad.Step_Size, 			'params':-1, 		'flag':None					},
						{'key':'KEY_KPPLUS', 	'method':CNCjsPad.Step_Size, 			'params':+1, 		'flag':None					},
						{'key':'KEY_HOMEPAGE', 	'method':CNCjsPad.gcode_Reset, 			'params':None, 		'flag':self.F_3TIME			},
						{'key':'KEY_KP4', 	'method':CNCjsPad.gcode_Move, 			'params':['x',-1], 	'flag':None					},
						{'key':'KEY_KP6', 	'method':CNCjsPad.gcode_Move, 			'params':['x',+1], 	'flag':None					},
						{'key':'KEY_KP8', 	'method':CNCjsPad.gcode_Move, 			'params':['y',+1], 	'flag':None					},
						{'key':'KEY_KP2', 	'method':CNCjsPad.gcode_Move, 			'params':['y',-1], 	'flag':None					},
						{'key':'KEY_KP9', 	'method':CNCjsPad.gcode_Move, 			'params':['z',+1], 	'flag':None					},
						{'key':'KEY_KP3', 	'method':CNCjsPad.gcode_Move, 			'params':['z',-1], 	'flag':None					}
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
		cmd="~\n"
		self.push_gcode(cmd)

	def gcode_Feed_Hold(self,foo):
		'feedhold'
		print("feedhold")
		cmd="!\n"
		self.push_gcode(cmd)

	def gcode_Homing(self,foo):
		'homing'
		print("homing")
		cmd="$H\n"
		self.push_gcode(cmd)
		cmd="?\n"
		self.push_gcode(cmd)

	def gcode_Sleep(self,foo):
		'sleep'
		print("sleep")
		cmd="$SLP\n"
		self.push_gcode(cmd)

	def gcode_Unlock(self,foo):
		'unlock'
		print("unlock")
		cmd="$X\n"
		self.push_gcode(cmd)
	
	def gcode_Reset(self,foo):
		'reset'
		print("reset")
		cmd="\x18\n"
		self.push_gcode(cmd)

	def gcode_Start(self,foo):
		'gcode:start'
		print("gcode:start")
		cmd="gcode:start\n"
		self.push_gcode(cmd)

	def gcode_Pause(self,foo):
		'gcode:pause'
		print("gcode:pause")
		cmd="gcode:pause\n"
		self.push_gcode(cmd)

	def gcode_Stop(self,foo):
		'gcode:stop'
		print("gcode:stop")
		cmd="gcode:stop\n"
		self.push_gcode(cmd)
		
	def gcode_Resume(self,foo):
		'gcode:resume'
		print("gcode:resume")
		cmd="gcode:resume\n"
		self.push_gcode(cmd)
		
	def gcode_Unload(self,foo):
		'gcode:unload'
		print("gcode:unload")
		cmd="gcode:unload\n"
		self.push_gcode(cmd)
		
	def gcode_Move(self,args):

		'gcode:G53 [X|Y|Z]<dir*step_size>'
		axis,dir=args
		#print(axis,dir,self.tool_pos,self.step_index)
		self.tool_pos[axis]+=dir*self.STEP_INCREMENTS[self.step_index]

		if self.tool_pos[axis]<self.CNC_LIMITS[axis+'min']:
			self.tool_pos[axis]=self.CNC_LIMITS[axis+'min']

		if self.tool_pos[axis]>self.CNC_LIMITS[axis+'max']:
			self.tool_pos[axis]=self.CNC_LIMITS[axis+'max']

		#cmd="G53 X%f Y%f Z%f" % (self.tool_pos['x'],self.tool_pos['y'],self.tool_pos['z'])
		cmd="G53 %s%f\n" % (axis.upper(),self.tool_pos[axis])
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


	def push_gcode(self,gcode):
		'push a command into gcode buffer'
		self.gcode_queue.append(gcode)
		#print("gcode: %s" % gcode)

	def gcode_ready(self):
		'return True if gcode is ready for processing'
		return (len(self.gcode_queue)>0)

	def pop_gcode(self):
		'pop a command from gcode buffer'
		gcode = self.gcode_queue.popleft()
		#print("gcode: %s" % gcode)
		return gcode

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



