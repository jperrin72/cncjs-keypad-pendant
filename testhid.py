#!/usr/bin/python
# run with root privilege!!!
import evdev
from select import select
from evdev import ecodes

devices = []
for fn in evdev.list_devices():
  device = evdev.InputDevice(fn)
  capabilities=device.capabilities().get(ecodes.EV_KEY, [])
  if  evdev.ecodes.EV_KEY in capabilities:
    devices.append(device)

fds = {dev.fd: dev for dev in devices}

while True:
	r, w, x = select(devices, [], [])
	for dev in r:
		for event in fds[dev.fd].read(): 
			if event.value==1 and event.type==ecodes.EV_KEY: # key down / key event
				#print(dev.fd,event.type,ecodes.KEY[event.code],event.value,event)
				print(ecodes.KEY[event.code])
				#dev.set_led(ecodes.LED_NUML, 1)
