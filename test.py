#!/usr/local/bin/python3

step_sequence=[0.01,0.05,0.1,0.5,1.0,5.0,10.0,50.0,100.0]
step_index=step_sequence.index(1.0)

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

def gcode_Move(axis,dir):
	'gcode:G0 [X|Y|Z]<dir*step_size>'

def Step_Size(dir):
	'set step size mm'
	step_index+=dir
	if step_index<0:
		index+=1
	if step_index==step_sequence>count():
		step_index-=1
	print("step index: %fmm" % step_sequence[step_index])

def decode_key(key):
	actions=(	{'key':'KEY_0', 'method':gcode_Cycle_Start, 'params':None},
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
	action=''
	for action in [rec for rec in actions if rec['key'] == key]:
		pass
	print(action)
	if action!='':
		action['method'](action['params'])
	else:
		print(key+" not found!")


decode_key('KEY_6')
decode_key('KEY_3')
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