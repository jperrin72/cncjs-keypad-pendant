#!/usr/bin/python3
import evdev
from evdev import ecodes

devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
for device in devices:
  print(device.fn, device.name, device.phys)

device = evdev.InputDevice("/dev/input/event2")
print(device)
for event in device.read_loop():
	if event.value==1 and event.type==ecodes.EV_KEY:
		print(ecodes.KEY[event.code], event.type, event.value)


