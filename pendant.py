#!/usr/local/bin/python3

import websocket
import requests # pip install requests / https://pypi.org/project/requests/
import sys, asyncore
import jwt
import logging
from socketIO_client import SocketIO, LoggingNamespace # pip install socketIO-client==0.5.7.2


SERVER_ADDRESS = "192.168.0.19"
SERVER_PORT = 8000

SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200


SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
access_token = jwt.encode({'id': '', 'name': 'cnc'}, SECRET, algorithm='HS256')
access_token_url_string = "{}".format(access_token.decode('utf-8'))


r = requests.post('http://'+SERVER_ADDRESS+':'+str(SERVER_PORT)+'/api/signin', headers={'token':access_token_url_string})
c=r.headers['set-cookie']
r.headers={'Cookie': c}

print(c)

def on_connect(*args):
  print('connect')
  socketIO.emit('open', SERIAL_PORT, {'baudrate': SERIAL_BAUDRATE, 'controllerType': CONTROLLER_TYPE})
  socketIO.on('serialport:open', on_serial_port_open)

def on_serial_port_open(*args):
  print('serialport:open')
  socketIO.emit('write', SERIAL_PORT, "{};\n".format(COMMAND))
  socketIO.on('serialport:write', on_serial_port_write)

def on_serial_port_write(*args):
  print("serialport:write")
  global loop
  loop = False

loop = True
with SocketIO(SERVER_ADDRESS, SERVER_PORT, LoggingNamespace, headers={'Cookie': r.headers['set-cookie']}) as socketIO:
  socketIO.on('connect', on_connect)
  while loop:
    socketIO.wait(seconds=WAIT_DURATION)

#print(r.headers['cookie'])

#print(r.content)


"""
GET / HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=Xafll0TNUrGBcRejAAAc
If-None-Match: W/"4d4-aQOYumep9us0Q06e6W/SHRlS53w"

	HTTP/1.1 304 Not Modified
	Set-Cookie: lang=en; path=/; expires=Sun, 07 Jun 2020 09:35:11 GMT
	X-UA-Compatible: IE=edge
	ETag: W/"4d4-aQOYumep9us0Q06e6W/SHRlS53w"
	Date: Fri, 07 Jun 2019 09:35:11 GMT
	Connection: keep-alive

POST /api/signin HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Content-Length: 164
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk4OTg4MzUsImV4cCI6MTU2MjQ5MDgzNX0.2ooMKHLlFjhjnVpljHEHvLMUUyZVmWyqJJJl61OB_oM
Cache-Control: no-cache
Origin: http://192.168.0.19:8000
X-Requested-With: XMLHttpRequest
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Content-Type: application/json
Accept: */*
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=Xafll0TNUrGBcRejAAAc

{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk4OTg4MzUsImV4cCI6MTU2MjQ5MDgzNX0.2ooMKHLlFjhjnVpljHEHvLMUUyZVmWyqJJJl61OB_oM"}

	HTTP/1.1 200 OK
	Vary: X-HTTP-Method-Override, Accept-Encoding
	Set-Cookie: lang=en; path=/; expires=Sun, 07 Jun 2020 09:35:12 GMT
	Content-Type: application/json; charset=utf-8
	Content-Length: 190
	ETag: W/"be-kzLldlQ+nZxw3AS0q1fXi1SnKl0"
	Date: Fri, 07 Jun 2019 09:35:12 GMT
	Connection: keep-alive

	{"enabled":false,"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s","name":""}

GET /socket.io/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s&EIO=3&transport=polling&t=MinIiVc HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=Xafll0TNUrGBcRejAAAc

	HTTP/1.1 200 OK
	Content-Type: text/plain; charset=UTF-8
	Content-Length: 99
	Access-Control-Allow-Origin: *
	Set-Cookie: io=CCG1s97x66DuuqeNAAAd; Path=/; HttpOnly
	Date: Fri, 07 Jun 2019 09:35:12 GMT
	Connection: keep-alive

	96:0{"sid":"CCG1s97x66DuuqeNAAAd","upgrades":["websocket"],"pingInterval":25000,"pingTimeout":5000}

GET /socket.io/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s&EIO=3&transport=polling&t=MinIiWR&sid=CCG1s97x66DuuqeNAAAd HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=CCG1s97x66DuuqeNAAAd

	HTTP/1.1 200 OK
	Content-Type: text/plain; charset=UTF-8
	Content-Length: 105
	Access-Control-Allow-Origin: *
	Set-Cookie: io=CCG1s97x66DuuqeNAAAd; Path=/; HttpOnly
	Date: Fri, 07 Jun 2019 09:35:12 GMT
	Connection: keep-alive

	2:4098:42["startup",{"loadedControllers":["Grbl","Marlin","Smoothie","TinyG"],"baudrates":[],"ports":[]}]

GET /socket.io/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s&EIO=3&transport=polling&t=MinIiWf&sid=CCG1s97x66DuuqeNAAAd HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Accept: */*
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=CCG1s97x66DuuqeNAAAd

	HTTP/1.1 200 OK
	Content-Type: text/plain; charset=UTF-8
	Content-Length: 3
	Access-Control-Allow-Origin: *
	Set-Cookie: io=CCG1s97x66DuuqeNAAAd; Path=/; HttpOnly
	Date: Fri, 07 Jun 2019 09:35:13 GMT
	Connection: keep-alive

	1:6

GET /api/state?_=1559900113165 HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s
X-Requested-With: XMLHttpRequest
Cache-Control: no-cache
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Accept: */*
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=CCG1s97x66DuuqeNAAAd

	HTTP/1.1 200 OK
	Set-Cookie: lang=en; path=/; expires=Sun, 07 Jun 2020 09:35:13 GMT
	Content-Type: application/json; charset=utf-8
	Content-Length: 74
	ETag: W/"4a-A19EJvGDCwXz9mx7V2Y0f/ulejA"
	Vary: Accept-Encoding
	Date: Fri, 07 Jun 2019 09:35:13 GMT
	Connection: keep-alive

	{"checkForUpdates":true,"controller":{"exception":{"ignoreErrors":false}}}

GET /api/mdi?_=1559900113606 HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s
X-Requested-With: XMLHttpRequest
Cache-Control: no-cache
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Accept: */*
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=CCG1s97x66DuuqeNAAAd

HTTP/1.1 200 OK
Set-Cookie: lang=en; path=/; expires=Sun, 07 Jun 2020 09:35:13 GMT
Content-Type: application/json; charset=utf-8
ETag: W/"f09-vIKByg35Vtj84F0rPqTZbfTvNNk"
Vary: Accept-Encoding
Content-Encoding: gzip
Date: Fri, 07 Jun 2019 09:35:13 GMT
Connection: keep-alive
Transfer-Encoding: chunked

{"records":[{"id":"2860bb42-a5e7-41e2-9393-f49f54891ffd","name":"Tool change","command":"; Wait until the planner queue is empty\n%wait\n\n; Set user-defined variables\n%CLEARANCE_HEIGHT = 2\n%PROBE_DISTANCE = 40 ; maximum distance to probe\n%TOOL_CHANGE_X = -416\n%TOOL_CHANGE_Y = -1028\n%TOOL_CHANGE_Z = -1\n%TOOL_PROBE_Z = 0\n%PROBE_FEEDRATE = 50\n%TOUCH_PLATE_HEIGHT = 19.5\n%RETRACTION_DISTANCE = 1\n\n; Keep a backup of current work position\n%X0=posx\n%Y0=posy\n%Z0=posz\n\n; save modal state\n%WCS = modal.wcs\n%PLANE = modal.plane\n%UNITS = modal.units\n%DISTANCE = modal.distance\n%FEEDRATE = modal.feedrate\n%SPINDLE = modal.spindle\n%COOLANT = modal.coolant\n\n\n; Absolute positioning\nG90\n\n; Raise to tool change Z\nG53 Z[TOOL_CHANGE_Z]\n\n; move to tool change area\nG53 X[TOOL_CHANGE_X] Y[TOOL_CHANGE_Y]\n\n; Wait until the planner queue is empty\n%wait\n\nM0\n\n; Go to previous work position\nG0 X[X0] Y[Y0]\n\n; Restore modal state\n[WCS] [PLANE] [UNITS] [DISTANCE] [FEEDRATE] [SPINDLE] [COOLANT]\n","grid":{"xs":3}},{"id":"e9b687b9-791c-4758-ac79-28fe925ec127","name":"Tool probe","command":"; Wait until the planner queue is empty\n%wait\n\n; Set user-defined variables\n%CLEARANCE_HEIGHT = 2\n%PROBE_DISTANCE = 35 ; maximum distance to probe\n%TOOL_CHANGE_X = -416\n%TOOL_CHANGE_Y = -1028\n%TOOL_CHANGE_Z = -1\n%TOOL_PROBE_Z = 0\n%PROBE_FEEDRATE = 50\n%TOUCH_PLATE_HEIGHT = 19.5\n%RETRACTION_DISTANCE = 1\n\n; Keep a backup of current work position\n%X0=posx\n%Y0=posy\n%Z0=posz\n\n; Save modal state\n%WCS = modal.wcs\n%PLANE = modal.plane\n%UNITS = modal.units\n%DISTANCE = modal.distance\n%FEEDRATE = modal.feedrate\n%SPINDLE = modal.spindle\n%COOLANT = modal.coolant\n\n; Absolute positioning\nG90\n\n; Raise to tool change Z\nG53 Z[TOOL_CHANGE_Z]\n\n; Wait until the planner queue is empty\n%wait\n\nM0\n\n; Probe toward workpiece with a maximum probe distance\nG91 ; Relative positioning\nG38.2 Z-[PROBE_DISTANCE] F[PROBE_FEEDRATE]\nG90 ; Absolute positioning\n\n; Set Z0 for the active work coordinate system\nG10 L20 P0 Z[TOUCH_PLATE_HEIGHT]\n\n; Wait until the planner queue is empty\n%wait\nG4 P1\n%wait\n\n; Retract from the touch plate\nG91 ; Relative positioning\nG0 Z[RETRACTION_DISTANCE]\nG90 ; Absolute positioning\n\n; Wait until the planner queue is empty\n%wait\n\nM1\n\n; Restore modal state\n[WCS] [PLANE] [UNITS] [DISTANCE] [FEEDRATE] [SPINDLE] [COOLANT]\n","grid":{"xs":3}},{"id":"3f102c19-ea8a-44d3-8013-54b6021546d9","name":"Tool center","command":"; Keep a backup of current Z work position\n%Z0=posz\n\n; lift tool\nG53 Z-0.1\n\n; go to center\nG53 X-208 Y-514\n\n; Go to previous Z work position\nG0 Z[Z0]","grid":{"xs":3}},{"id":"40a84249-4851-407d-b7a8-919e74cd9ce2","name":"Tool up","command":"G53 Z-0.1","grid":{"xs":3}},{"id":"ac7c8c62-70a0-4352-bd4b-424bcdfaf55e","name":"cal y=0","command":"G0 X0 Y0 Z5\nG0 Z0\nM1\nG0 X415 Z5\nG0 Z0\n","grid":{"xs":3}},{"id":"7bfb22fe-0a8c-46de-862e-4dd5d6c05658","name":"cal y=1020","command":"G0 X0 Y1020 Z5\nG0 Z0\nM1\nG0 X415 Z5\nG0 Z0\n","grid":{"xs":3}},{"id":"3374467d-0aba-4d3d-a0a4-bf675c8e758a","name":"cal x=0","command":"G0 X0 Y0 Z5\nG0 Z0\nM1\nG0 Y1020 Z5\nG0 Z0\n","grid":{"xs":3}},{"id":"d9080322-31ec-4683-9b82-59e05a022757","name":"cal x=415","command":"G0 X415 Y0 Z5\nG0 Z0\nM1\nG0 Y1020 Z5\nG0 Z0\n","grid":{"xs":3}},{"id":"9619accb-1847-4025-b450-ac7417bd4aaf","name":"CNC Mode","command":"$32=0\n$30=30000\n$H\nG53 Z-0.1\nG10 L20 P1 X0 Y0 Z0\n","grid":{"xs":3}},{"id":"e52381a0-71d6-47ba-a6d9-1b8a9a5cac8d","name":"Laser Mode","command":"$32=1\n$30=100\n$H\nG53 Z-36.3\nG10 L20 P1 X0 Y0 Z0\nG53 Z-0.1","grid":{"xs":3}},{"id":"dc9e2e7d-8521-4667-9bf5-6ecbe1cc743d","name":"Go Home","command":"G0 X0 Y0 Z0","grid":{"xs":3}},{"id":"1c9dc622-49bf-4dfa-a115-8c4bc9f4ce73","name":"Set Home","command":"G10 L20 P1 X0 Y0 Z0","grid":{"xs":3}}]}GET /api/version/latest?_=1559900113979 HTTP/1.1
Host: 192.168.0.19:8000
Connection: keep-alive
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NTk5MDAxMTIsImV4cCI6MTU2MjQ5MjExMn0.7sNGznKavl94R6RQbhs7IWtnes6mlySQwfB0fUxZT6s
X-Requested-With: XMLHttpRequest
Cache-Control: no-cache
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36
Accept: */*
Referer: http://192.168.0.19:8000/
Accept-Encoding: gzip, deflate
Accept-Language: en-GB,en-US;q=0.9,en;q=0.8,fr;q=0.7
Cookie: lang=en; connect.sid=s%3ALLtp3vjjIMpHE4w_tpU_pMHgpybotbEu.fCz78evQP7fqU3tovbLW%2FHHnXvsUBd0XqytjU3ej%2FnY; io=CCG1s97x66DuuqeNAAAd

HTTP/1.1 200 OK
Set-Cookie: lang=en; path=/; expires=Sun, 07 Jun 2020 09:35:14 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 189
ETag: W/"bd-zAqdzZ+5V6JSOYyoe+33pMd/4Cs"
Vary: Accept-Encoding
Date: Fri, 07 Jun 2019 09:35:14 GMT
Connection: keep-alive

{"name":"cncjs","version":"1.9.20","description":"A web-based interface for CNC milling controller running Grbl, Marlin, Smoothieware, or TinyG","homepage":"https://github.com/cncjs/cncjs"}
"""
