#!/usr/local/bin/python3

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
	action=''
	for action in [rec for rec in ACTIONS if rec['key'] == key]:
		pass
	#print(action)
	if action!='':
		action['method'](action['params'])
	else:
		print(key+" not found!")

def push_gcode(gcode):
	'push a command into gcode buffer'
	print("gcode: %s" % gcode)

# constants and global variables section

STEP_INCREMENTS=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]

ACTIONS=(	{'key':'KEY_0', 'method':gcode_Cycle_Start, 'params':None},
			{'key':'KEY_1', 'method':gcode_Feed_Hold, 'params':None},
			{'key':'KEY_2', 'method':gcode_Homing, 'params':None},
			{'key':'KEY_3', 'method':gcode_Sleep, 'params':None},
			{'key':'KEY_4', 'method':gcode_Unlock, 'params':None},
			{'key':'KEY_5', 'method':gcode_Start, 'params':None},
			{'key':'KEY_6', 'method':gcode_Pause, 'params':None},
			{'key':'KEY_7', 'method':gcode_Stop, 'params':None},
			{'key':'KEY_8', 'method':gcode_Resume, 'params':None},
			{'key':'KEY_9', 'method':gcode_Unload, 'params':None},
			{'key':'KEY_-', 'method':Step_Size, 'params':-1},
			{'key':'KEY_+', 'method':Step_Size, 'params':+1},
			{'key':'KEY_X-', 'method':gcode_Move, 'params':['X',-1]},
			{'key':'KEY_X+', 'method':gcode_Move, 'params':['X',+1]},
			{'key':'KEY_Y-', 'method':gcode_Move, 'params':['Y',-1]},
			{'key':'KEY_Y+', 'method':gcode_Move, 'params':['Y',+1]},
			{'key':'KEY_Z-', 'method':gcode_Move, 'params':['Z',-1]},
			{'key':'KEY_Z+', 'method':gcode_Move, 'params':['Z',+1]}
		)

step_index=STEP_INCREMENTS.index(1.0)
tool_pos = {'X':0.0,'Y':0.0,'Z':0.0}


# main program

gcode_Get_Position()
print(step_index)
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_X+')
decode_key('KEY_Y+')
decode_key('KEY_Z+')
decode_key('KEY_X-')
decode_key('KEY_Y-')
decode_key('KEY_Z-')

decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_-')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')
decode_key('KEY_+')