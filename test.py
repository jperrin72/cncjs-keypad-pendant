#!/usr/local/bin/python3

import time

# functions

def gcode_Get_Position():
	'get x/y/z coordinates from cnc'
	global tool_pos
	print("tool_pos: %s" % tool_pos)

def foo(params):
	print("foo called! params=",params)

def gcode_Cycle_Start(foo):
	'cyclestart'

def gcode_Feed_Hold(foo):
	'feedhold'

def gcode_Homing(foo):
	'homing'
	print("Home called!")

def gcode_Sleep(foo):
	'sleep'

def gcode_Unlock(foo):
	'unlock'

def gcode_Start(foo):
	'gcode:start'

def gcode_Pause(foo):
	'gcode:pause'

def gcode_Stop(foo):
	'gcode:stop'

def gcode_Resume(foo):
	'gcode:resume'

def gcode_Unload(foo):
	'gcode:unload'
	print("Unload called!")

def gcode_Move(args):

	'gcode:G0 [X|Y|Z]<dir*step_size>'
	global tool_pos
	axis,dir=args
	tool_pos[axis]+=dir*STEP_INCREMENTS[step_index]
	cmd="G0 X%f Y%f Z%f" % (tool_pos['X'],tool_pos['Y'],tool_pos['Z'])
	#print("new pos: %s" % tool_pos)
	push_gcode(cmd)

def Step_Size(dir):
	'set step size mm'
	global step_index
	step_index+=dir
	if step_index<0:
		step_index+=1
	if step_index==len(STEP_INCREMENTS):
		step_index-=1
	print("step size: %.2fmm" % STEP_INCREMENTS[step_index])

def decode_key(key):
	global key_rep_num
	action=''
	for action in [rec for rec in ACTIONS if rec['key'] == key]:
		pass
	#print(action)
	if action!='':
		ignore=False
		if action['flag']==F_3TIME:
			if key_rep_num==3:
				key_rep_num=0
			else:
				ignore=True
		if action['flag']==F_IGNORE_REPEAT:
			if key_rep_num>1:
				ignore=True
		if not ignore:
			action['method'](action['params'])


def push_gcode(gcode):
	'push a command into gcode buffer'
	print("gcode: %s" % gcode)

def get_key_press():
	global cur_key, prev_key
	global cur_key_time, prev_key_time
	global key_rep_num, key_delta_time

	prev_key = cur_key
	prev_key_time = cur_key_time
	cur_key  = input()
	cur_key_time = time.time()

	if prev_key_time is None:
		key_delta_time = 0.0
	else:
		key_delta_time = cur_key_time - prev_key_time 

	if (cur_key == prev_key) and (key_delta_time<=KEY_REPEAT_TIME):
		key_rep_num+=1
	else:
		key_rep_num=1

	print(cur_key,prev_key,key_delta_time,key_rep_num)
	decode_key(cur_key)


# constants and global variables section

CNC_LIMITS={'xmin':0.0, 'xmax':450.0, 'ymin':0.0, 'ymax':1024.0, 'zmin':0.0, 'zmax':35.0}
STEP_INCREMENTS=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]

F_IGNORE_REPEAT=1
F_3TIME=2
ACTIONS=(	{'key':'KEY_0', 'method':gcode_Cycle_Start, 	'params':None, 		'flag':None				},
			{'key':'KEY_1', 'method':gcode_Feed_Hold, 		'params':None, 		'flag':None				},
			{'key':'H', 	'method':gcode_Homing, 			'params':None, 		'flag':F_3TIME			},
			{'key':'KEY_3', 'method':gcode_Sleep, 			'params':None, 		'flag':None				},
			{'key':'KEY_4', 'method':gcode_Unlock, 			'params':None, 		'flag':None				},
			{'key':'KEY_5', 'method':gcode_Start, 			'params':None, 		'flag':None				},
			{'key':'KEY_6', 'method':gcode_Pause, 			'params':None, 		'flag':None				},
			{'key':'KEY_7', 'method':gcode_Stop, 			'params':None, 		'flag':None				},
			{'key':'KEY_8', 'method':gcode_Resume, 			'params':None, 		'flag':None				},
			{'key':'U', 	'method':gcode_Unload, 			'params':None, 		'flag':F_IGNORE_REPEAT	},
			{'key':'-', 	'method':Step_Size, 			'params':-1, 		'flag':None				},
			{'key':'+', 	'method':Step_Size, 			'params':+1, 		'flag':None				},
			{'key':'A', 	'method':gcode_Move, 			'params':['X',-1], 	'flag':None				},
			{'key':'S', 	'method':gcode_Move, 			'params':['X',+1], 	'flag':None				},
			{'key':'Q', 	'method':gcode_Move, 			'params':['Y',-1], 	'flag':None				},
			{'key':'Z', 	'method':gcode_Move, 			'params':['Y',+1], 	'flag':None				},
			{'key':'W', 	'method':gcode_Move, 			'params':['Z',-1], 	'flag':None				},
			{'key':'X', 	'method':gcode_Move, 			'params':['Z',+1], 	'flag':None				}
		)

KEY_REPEAT_TIME=1.0
step_index=STEP_INCREMENTS.index(1.0)
tool_pos = {'X':0.0,'Y':0.0,'Z':0.0}
prev_key = None
prev_key_time = None
cur_key = None
cur_key_time = None
key_rep_num = 0

# main program

gcode_Get_Position()

while (True):
	get_key_press()
