#!/usr/bin/python3
#!/usr/local/bin/python3

import json
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
		self.grbl.wait()
		#pendant.grbl.disconnect()
		self.pad.gcode_Set_Limits(x=self.grbl.controller_settings['settings']['$130'],y=self.grbl.controller_settings['settings']['$131'],z=self.grbl.controller_settings['settings']['$132'])
		self.pad.gcode_Set_Position(pos=self.grbl.controller_state['status']['mpos'])


#pendant= CNCjsPendant(serial='/dev/tty.MALS')
pendant= CNCjsPendant(local=False, ip='192.168.0.19',secret='$2a$10$IYnT/KjMHedGJUqaS.riNe')
pendant.connect()
print(vars(pendant.grbl))
#
while True:
	pendant.pad.get_key_press()
	if pendant.pad.gcode_ready():
		gcode=pendant.pad.gcode_queue.pop()
		print("gcode:",gcode)
		pendant.grbl.send(event='write',data=gcode,wait=True)
		pendant.grbl.wait()
