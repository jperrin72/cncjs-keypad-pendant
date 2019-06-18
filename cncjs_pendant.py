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

#pendant= CNCjsPendant(serial='/dev/tty.MALS')
pendant= CNCjsPendant(local=False, ip='192.168.0.19',secret='$2a$10$IYnT/KjMHedGJUqaS.riNe')
pendant.grbl.connect()
pendant.grbl.wait()
pendant.grbl.send(event="write",data="$H\r")
pendant.grbl.wait()
pendant.grbl.send(event="write",data="$$\r")
pendant.grbl.wait()
#pendant.grbl.disconnect()
print(vars(pendant.grbl))

# main program

while (True):
	pendant.pad.get_key_press()
