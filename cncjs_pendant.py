#!/usr/bin/python3
#!/usr/local/bin/python3

import time
from pathlib import Path
from cncjs_grbl import CNCjsGrbl
from cncjs_pad import CNCjsPad

class CNCjsPendant:
	'Python pendant for CncJs'

	def __init__(self,local=True,ip='127.0.0.1',port=8000,serial='/dev/ttyUSB0',secret=None):
		if secret==None:
			if local:
				with open(str(Path.home())+"/.cncrc") as cncrc:  
				    data = json.load(cncrc)
				    secret=data['secret']
		self.grbl=CNCjsGrbl(ip,port,serial,secret)
		self.pad=CNCjsPad()

	def connect(self):
		self.grbl.connect()
		self.grbl.wait_ready()
		#pendant.grbl.disconnect()
		self.pad.gcode_Set_Limits(x=self.grbl.controller_settings['settings']['$130'],y=self.grbl.controller_settings['settings']['$131'],z=self.grbl.controller_settings['settings']['$132'])
		self.pad.gcode_Set_Position(pos=self.grbl.controller_state['status']['mpos'])

#pendant= CNCjsPendant(serial='/dev/tty.MALS')


pendant= CNCjsPendant(local=False, ip='192.168.0.19',secret='$2a$10$IYnT/KjMHedGJUqaS.riNe')
pendant.grbl.set_activeState_callback(pendant.pad.grbl_callback)
pendant.connect()
print(vars(pendant.grbl))
#
while True:
	if pendant.pad.gcode_ready():

		if pendant.pad.gcode_queue[0]['stateless'] or pendant.grbl.active_state in ['Idle','Run']: 
			message=pendant.pad.gcode_queue.pop()
			pendant.grbl.send(event=message['event'],data=message['data'],wait=message['wait'])
		else:
			print('activeState:',pendant.grbl.active_state,'\tqueue:',str(pendant.pad.gcode_queue))
			pass
	time.sleep(0.001)
