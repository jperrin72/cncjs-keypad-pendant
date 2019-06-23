#!/usr/local/bin/python3

import websocket
import requests # pip install requests / https://pypi.org/project/requests/
import sys, asyncore
import jwt # pip3 install pyjwt
import logging
import socketio # pip3 install "python-socketio[client]" / https://python-socketio.readthedocs.io/en/latest/client.html
from socketio import packet

class CNCjsGrbl:
	'Implement communication through websockets to Grbl'
	def __init__(self,ip,port,serial,secret=None):
		self.server_ip=ip
		self.server_port=port
		self.serial_port=serial
		self.serial_baud=115200
		self.controller_type="Grbl"
		self.user_id=""
		self.user_name="cncjs-pendant"
		self.user_pass=""
		self.workflow_state=''
		self.active_state=''
		self.ws_secret=secret
		#self.sio = socketio.Client(logger=True)
		self.sio = socketio.Client(logger=False)
		print(self,ip,port,serial,secret)

	def disconnect(self):
		self.sio.disconnect()


	def connect_http(self):
		'initiate api http session'
		'''
		Machine ={'records': [{'id': '0fc57b97-3628-48a2-843b-8e3e597ff5e0', 'name': 'OpenBuilds OX', 'limits': {'xmin': 0, 'xmax': 418, 'ymin': 0, 'ymax': 1029, 'zmin': 0, 'zmax': 47}}]}
		Commands ={'records': [{'id': 'ad5309c1-61c7-4d6e-a55a-bf8a9ebc8610', 'mtime': 1513531359625, 'enabled': True, 'title': 'Halt', 'commands': '/usr/bin/sudo /sbin/halt'}, {'id': 'cd21c946-2799-4151-9ead-b1726814a79a', 'mtime': 1560974944292, 'enabled': True, 'title': 'Test', 'commands': 'ls -l\n'}]}
		Api ={'records': [{'id': '2860bb42-a5e7-41e2-9393-f49f54891ffd', 'name': 'Tool change', 'command': '; Wait until the planner queue is empty\n%wait\n\n; Set user-defined variables\n%CLEARANCE_HEIGHT = 2\n%PROBE_DISTANCE = 40 ; maximum distance to probe\n%TOOL_CHANGE_X = -416\n%TOOL_CHANGE_Y = -1028\n%TOOL_CHANGE_Z = -1\n%TOOL_PROBE_Z = 0\n%PROBE_FEEDRATE = 50\n%TOUCH_PLATE_HEIGHT = 19.5\n%RETRACTION_DISTANCE = 1\n\n; Keep a backup of current work position\n%X0=posx\n%Y0=posy\n%Z0=posz\n\n; save modal state\n%WCS = modal.wcs\n%PLANE = modal.plane\n%UNITS = modal.units\n%DISTANCE = modal.distance\n%FEEDRATE = modal.feedrate\n%SPINDLE = modal.spindle\n%COOLANT = modal.coolant\n\n\n; Absolute positioning\nG90\n\n; Raise to tool change Z\nG53 Z[TOOL_CHANGE_Z]\n\n; move to tool change area\nG53 X[TOOL_CHANGE_X] Y[TOOL_CHANGE_Y]\n\n; Wait until the planner queue is empty\n%wait\n\nM0\n\n; Go to previous work position\nG0 X[X0] Y[Y0]\n\n; Restore modal state\n[WCS] [PLANE] [UNITS] [DISTANCE] [FEEDRATE] [SPINDLE] [COOLANT]\n', 'grid': {'xs': 3}}, {'id': 'e9b687b9-791c-4758-ac79-28fe925ec127', 'name': 'Tool probe', 'command': '; Wait until the planner queue is empty\n%wait\n\n; Set user-defined variables\n%CLEARANCE_HEIGHT = 2\n%PROBE_DISTANCE = 35 ; maximum distance to probe\n%TOOL_CHANGE_X = -416\n%TOOL_CHANGE_Y = -1028\n%TOOL_CHANGE_Z = -1\n%TOOL_PROBE_Z = 0\n%PROBE_FEEDRATE = 50\n%TOUCH_PLATE_HEIGHT = 19.5\n%RETRACTION_DISTANCE = 1\n\n; Keep a backup of current work position\n%X0=posx\n%Y0=posy\n%Z0=posz\n\n; Save modal state\n%WCS = modal.wcs\n%PLANE = modal.plane\n%UNITS = modal.units\n%DISTANCE = modal.distance\n%FEEDRATE = modal.feedrate\n%SPINDLE = modal.spindle\n%COOLANT = modal.coolant\n\n; Absolute positioning\nG90\n\n; Raise to tool change Z\nG53 Z[TOOL_CHANGE_Z]\n\n; Wait until the planner queue is empty\n%wait\n\nM0\n\n; Probe toward workpiece with a maximum probe distance\nG91 ; Relative positioning\nG38.2 Z-[PROBE_DISTANCE] F[PROBE_FEEDRATE]\nG90 ; Absolute positioning\n\n; Set Z0 for the active work coordinate system\nG10 L20 P0 Z[TOUCH_PLATE_HEIGHT]\n\n; Wait until the planner queue is empty\n%wait\nG4 P1\n%wait\n\n; Retract from the touch plate\nG91 ; Relative positioning\nG0 Z[RETRACTION_DISTANCE]\nG90 ; Absolute positioning\n\n; Wait until the planner queue is empty\n%wait\n\nM1\n\n; Restore modal state\n[WCS] [PLANE] [UNITS] [DISTANCE] [FEEDRATE] [SPINDLE] [COOLANT]\n', 'grid': {'xs': 3}}, {'id': '3f102c19-ea8a-44d3-8013-54b6021546d9', 'name': 'Tool center', 'command': '; Keep a backup of current Z work position\n%Z0=posz\n\n; lift tool\nG53 Z-0.1\n\n; go to center\nG53 X-208 Y-514\n\n; Go to previous Z work position\nG0 Z[Z0]', 'grid': {'xs': 3}}, {'id': '40a84249-4851-407d-b7a8-919e74cd9ce2', 'name': 'Tool up', 'command': 'G53 Z-0.1', 'grid': {'xs': 3}}, {'id': 'ac7c8c62-70a0-4352-bd4b-424bcdfaf55e', 'name': 'cal y=0', 'command': 'G0 X0 Y0 Z5\nG0 Z0\nM1\nG0 X415 Z5\nG0 Z0\n', 'grid': {'xs': 3}}, {'id': '7bfb22fe-0a8c-46de-862e-4dd5d6c05658', 'name': 'cal y=1020', 'command': 'G0 X0 Y1020 Z5\nG0 Z0\nM1\nG0 X415 Z5\nG0 Z0\n', 'grid': {'xs': 3}}, {'id': '3374467d-0aba-4d3d-a0a4-bf675c8e758a', 'name': 'cal x=0', 'command': 'G0 X0 Y0 Z5\nG0 Z0\nM1\nG0 Y1020 Z5\nG0 Z0\n', 'grid': {'xs': 3}}, {'id': 'd9080322-31ec-4683-9b82-59e05a022757', 'name': 'cal x=415', 'command': 'G0 X415 Y0 Z5\nG0 Z0\nM1\nG0 Y1020 Z5\nG0 Z0\n', 'grid': {'xs': 3}}, {'id': '9619accb-1847-4025-b450-ac7417bd4aaf', 'name': 'CNC Mode', 'command': '$32=0\n$30=30000\n$H\nG53 Z-0.1\nG10 L20 P1 X0 Y0 Z0\n', 'grid': {'xs': 3}}, {'id': 'e52381a0-71d6-47ba-a6d9-1b8a9a5cac8d', 'name': 'Laser Mode', 'command': '$32=1\n$30=100\n$H\n;G53 Z-36.3 ; engraver\n; delta=-8.2\nG53 Z-44.5 ; cutter\nG10 L20 P1 X0 Y0 Z0\nG53 Z-0.1', 'grid': {'xs': 3}}, {'id': 'dc9e2e7d-8521-4667-9bf5-6ecbe1cc743d', 'name': 'Go Home', 'command': 'G0 X0 Y0 Z0', 'grid': {'xs': 3}}, {'id': '1c9dc622-49bf-4dfa-a115-8c4bc9f4ce73', 'name': 'Set Home', 'command': 'G10 L20 P1 X0 Y0 Z0', 'grid': {'xs': 3}}]}
		'''

		self.session=requests.session()
		auth_token='{"token":"'+'{}'.format(self.access_token.decode('utf-8'))+'"}'
		self.request = self.session.post(	'http://'+self.server_ip+':'+str(self.server_port)+'/api/signin',
											headers={
											'Authorization': 'Bearer {}'.format(self.access_token.decode('utf-8')),
											'content-type': 'application/json'
											},data=auth_token)
		auth_token=self.request.json()['token']
		self.request = self.session.get('http://'+self.server_ip+':'+str(self.server_port)+'/api/machines',params={'token':'{}'.format(auth_token)})
		self.machine=self.request.json()
		self.request = self.session.get('http://'+self.server_ip+':'+str(self.server_port)+'/api/commands',params={'token':'{}'.format(auth_token)})
		self.commands=self.request.json()
		self.request = self.session.get('http://'+self.server_ip+':'+str(self.server_port)+'/api/mdi',params={'token':'{}'.format(auth_token)})
		self.api=self.request.json()

	def connect(self):

		# define websocket handlers

		@self.sio.on('connect')
		def connect_message():
			''
			print("connect")
			self.connect_http()

		@self.sio.on('startup')
		def open_startup(data):
		    self.startup_data=data
		    self.send('open',{'baudrate':self.serial_baud,'controllerType':self.controller_type})

		@self.sio.on('serialport:open')
		def serialport_open_message(data):
		    self.serial_state=data

		@self.sio.on('serialport:close')
		def serialport_close_message(data):
		    ''
		    print("serialport:close")

		@self.sio.on('serialport:error')
		def serialport_error_message(data):
		    ''
		    print("serialport:error",data)

		@self.sio.on('serialport:read')
		def serialport_read_message(data):
		    ''
		    print("serialport:read",data)
		    if (data=='ok'):
		    	self.active_state='PacketOK'

		@self.sio.on('serialport:change')
		def serialport_read_message(data):
		    ''
		    print("serialport:change",data)

		@self.sio.on('serialport:write')
		def serialport_write_message(data,sender):
			''
			print("serialport:write=",data)

		@self.sio.on('controller:settings')
		def controller_settings_message(controller,settings):
			self.controller_settings=settings

		@self.sio.on('Grbl:state')
		def grbl_state_message(state):
		    self.controller_state=state
		    self.active_state=state['status']['activeState']
		    print("activeState=",self.active_state)

		@self.sio.on('controller:state')
		def controller_state_message(controller,state):
		    self.controller_state=state
		    self.active_state=state['status']['activeState']
		    print("activeState=",self.active_state)

		@self.sio.on('workflow:state')
		def workflow_state_message(state):
		    self.workflow_state=state

		@self.sio.on('feeder:status')
		def feeder_status_message(status):
		    self.feeder_status=status	

		@self.sio.on('sender:status')
		def sender_status_message(status):
		    self.sender_status=status	

		@self.sio.on('error')
		def error_message(data):
		    print("error",data)

		# connect to websocket service
		self.access_token = jwt.encode({'id': self.user_id, 'name': self.user_name}, self.ws_secret, algorithm='HS256')
		self.access_token_url_string = "{}".format(self.access_token.decode('utf-8'))
		self.sio.connect('ws://'+self.server_ip+':'+str(self.server_port),headers={'Authorization': 'Bearer {}'.format(self.access_token.decode('utf-8'))})


	def send(self,event,data=None,wait=False):

		if (wait):
			self.active_state='PacketSent'
		self.sio._send_packet(packet.Packet(	packet.EVENT,
												namespace=None,
												data=[event,self.serial_port,data],
												id=None,
												binary=None))

	def run_cmd(self):
		'''


		POST /api/commands/run/ad5309c1-61c7-4d6e-a55a-bf8a9ebc8610 HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Content-Length: 0
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		Cache-Control: no-cache
		Origin: http://192.168.0.19:8000
		X-Requested-With: XMLHttpRequest
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Vary: X-HTTP-Method-Override, Accept-Encoding
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:10 GMT
		Content-Type: application/json; charset=utf-8
		Content-Length: 22
		ETag: W/"16-QOcQiOYUimQ/h6ViETUBnWYLjQQ"
		Date: Sun, 23 Jun 2019 18:38:10 GMT
		Connection: keep-alive

		{"taskId":"58gMuwjOp"}
		---

		GET /api/machines?_=1561315083326 HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:03 GMT
		Content-Type: application/json; charset=utf-8
		Content-Length: 153
		ETag: W/"99-PjWaYBSJ7NN2CKjuCS7VSlk59Ig"
		Vary: Accept-Encoding
		Date: Sun, 23 Jun 2019 18:38:03 GMT
		Connection: keep-alive

		{"records":[{"id":"0fc57b97-3628-48a2-843b-8e3e597ff5e0","name":"OpenBuilds OX","limits":{"xmin":0,"xmax":418,"ymin":0,"ymax":1029,"zmin":0,"zmax":47}}]}
				

		------

		GET /api/commands?_=1561315082859&paging=false HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:02 GMT
		Content-Type: application/json; charset=utf-8
		Content-Length: 325
		ETag: W/"145-8Cm4XOzzzRcrL85mZjSnQ2scnds"
		Vary: Accept-Encoding
		Date: Sun, 23 Jun 2019 18:38:02 GMT
		Connection: keep-alive

		{"pagination":{"page":1,"pageLength":10,"totalRecords":2},"records":[{"id":"ad5309c1-61c7-4d6e-a55a-bf8a9ebc8610","mtime":1513531359625,"enabled":true,"title":"Halt","commands":"/usr/bin/sudo /sbin/halt"},{"id":"cd21c946-2799-4151-9ead-b1726814a79a","mtime":1560974944292,"enabled":true,"title":"Test","commands":"ls -l\n"}]}


		------

		GET /api/mdi?_=1561315083328 HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:03 GMT
		Content-Type: application/json; charset=utf-8
		ETag: W/"f38-OdHuUveqDQv/HaqcWlOOnRDs4KA"
		Vary: Accept-Encoding
		Content-Encoding: gzip
		Date: Sun, 23 Jun 2019 18:38:03 GMT
		Connection: keep-alive
		Transfer-Encoding: chunked

		a
		..........
		4f5
		.Wmo.6..+..~+.."%.A>x...K..q....P$...%O.....}G..#;....6`.b..r.=........rS.._~m%....B.D.gX	.`N-.........%.c.z.J....a.M..U.....f3..S..g..h.........*Mm.~[..EI..l^>^.o.a.Uz...s..
		.cc.$....<Q.....s.m...N...{.;.....|68..{}x|>ts`.....zHf..2IQ.T[Tfh.g.........Q...^_.....0.....n...}e.];.y....=..... ..O.....0.qS.'`n.......i.9~Zs...s.P.....e1..<.i......gER&..|{A.....F..Q:.F..'....Yf.......s..<U..{.............?..W...tk...'V,.......Z..^.....'..b..f.f:@g.?|.. *.V.p..."..J..v..\.=I...J.*..Z.h........M....nk.....\4.\L..a.-..^}.\..e...].-..|.... ...,=
		lQf.F./!..tY%...T..*90\...K.a...N.r..]..m=@.{...[v.+#?."..I5.......,..d.j....P.....x....h......7...V......W...0O,H.>)o!S+.U2CkJz."W.SU&w.Ax..Cc|.T..}.l.iR..v..*.1Aq.WQ)]....t.&I!..x,J;..(A'..3R..)..b....m....9.Aq.....l.o.9._1.p.P . ...K..6...a4...Pa...CB=,x..F....|hA...F...).[.....I\VE...L..L.TWT.ly'bFB4....o.-WU..d.;|NT......bN...@.XRi.....m...7B.B..	.[:.>..Q.sO0...ap.i..X..v.!.......d.F....".b..S....F...c...3....8.....a|M./.M. ...8.O....s..&*....`E..Q..B...{....zN....a$	.....u....Q.....E..D.....B...Y,..Ri.a.r..C......{8
		@2J.k,.~.}.L....c....G.<....5*.....{.
		.
		...T.P..+.r..#`..J*......;Q.nz...A........y.Gmz...!wEm..T.....p...sJ/......+..hi.....A..~.......,.@..,..-G........ji....p:(;..(.8.P.2.......0..lG..o.....D.8...
		0

		------


		GET /api/commands?_=1561315082859&paging=false HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:02 GMT
		Content-Type: application/json; charset=utf-8
		Content-Length: 325
		ETag: W/"145-8Cm4XOzzzRcrL85mZjSnQ2scnds"
		Vary: Accept-Encoding
		Date: Sun, 23 Jun 2019 18:38:02 GMT
		Connection: keep-alive

		{"pagination":{"page":1,"pageLength":10,"totalRecords":2},"records":[{"id":"ad5309c1-61c7-4d6e-a55a-bf8a9ebc8610","mtime":1513531359625,"enabled":true,"title":"Halt","commands":"/usr/bin/sudo /sbin/halt"},{"id":"cd21c946-2799-4151-9ead-b1726814a79a","mtime":1560974944292,"enabled":true,"title":"Test","commands":"ls -l\n"}]}GET /api/mdi?_=1561315083328 HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:03 GMT
		Content-Type: application/json; charset=utf-8
		ETag: W/"f38-OdHuUveqDQv/HaqcWlOOnRDs4KA"
		Vary: Accept-Encoding
		Content-Encoding: gzip
		Date: Sun, 23 Jun 2019 18:38:03 GMT
		Connection: keep-alive
		Transfer-Encoding: chunked

		a
		..........
		4f5
		.Wmo.6..+..~+.."%.A>x...K..q....P$...%O.....}G..#;....6`.b..r.=........rS.._~m%....B.D.gX	.`N-.........%.c.z.J....a.M..U.....f3..S..g..h.........*Mm.~[..EI..l^>^.o.a.Uz...s..
		.cc.$....<Q.....s.m...N...{.;.....|68..{}x|>ts`.....zHf..2IQ.T[Tfh.g.........Q...^_.....0.....n...}e.];.y....=..... ..O.....0.qS.'`n.......i.9~Zs...s.P.....e1..<.i......gER&..|{A.....F..Q:.F..'....Yf.......s..<U..{.............?..W...tk...'V,.......Z..^.....'..b..f.f:@g.?|.. *.V.p..."..J..v..\.=I...J.*..Z.h........M....nk.....\4.\L..a.-..^}.\..e...].-..|.... ...,=
		lQf.F./!..tY%...T..*90\...K.a...N.r..]..m=@.{...[v.+#?."..I5.......,..d.j....P.....x....h......7...V......W...0O,H.>)o!S+.U2CkJz."W.SU&w.Ax..Cc|.T..}.l.iR..v..*.1Aq.WQ)]....t.&I!..x,J;..(A'..3R..)..b....m....9.Aq.....l.o.9._1.p.P . ...K..6...a4...Pa...CB=,x..F....|hA...F...).[.....I\VE...L..L.TWT.ly'bFB4....o.-WU..d.;|NT......bN...@.XRi.....m...7B.B..	.[:.>..Q.sO0...ap.i..X..v.!.......d.F....".b..S....F...c...3....8.....a|M./.M. ...8.O....s..&*....`E..Q..B...{....zN....a$	.....u....Q.....E..D.....B...Y,..Ri.a.r..C......{8
		@2J.k,.~.}.L....c....G.<....5*.....{.
		.
		...T.P..+.r..#`..J*......;Q.nz...A........y.Gmz...!wEm..T.....p...sJ/......+..hi.....A..~.......,.@..,..-G........ji....p:(;..(.8.P.2.......0..lG..o.....D.8...
		0

		GET /api/version/latest?_=1561315083532 HTTP/1.1
		Host: 192.168.0.19:8000
		Connection: keep-alive
		Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IiIsIm5hbWUiOiIiLCJpYXQiOjE1NjEzMTUwODIsImV4cCI6MTU2MzkwNzA4Mn0.FvLH6gCGob0B4J_7nNikXMhl3uqHLXGEgGK9Z1cQl9M
		X-Requested-With: XMLHttpRequest
		Cache-Control: no-cache
		User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36
		Accept: */*
		Referer: http://192.168.0.19:8000/
		Accept-Encoding: gzip, deflate
		Accept-Language: fr-FR,fr;q=0.9,en-GB;q=0.8,en;q=0.7
		Cookie: lang=en; connect.sid=s%3AB1Pa_cKSSMmy1cvU-DECLB_NtIpTlifp.A7FyWete1gfjj6pQdfVG1kQj7mgUdZST1315851Ebgk; io=mWb5JFAuZXwdZXtjAAAD

		HTTP/1.1 200 OK
		Set-Cookie: lang=en; path=/; expires=Tue, 23 Jun 2020 18:38:03 GMT
		Content-Type: application/json; charset=utf-8
		Content-Length: 189
		ETag: W/"bd-zAqdzZ+5V6JSOYyoe+33pMd/4Cs"
		Vary: Accept-Encoding
		Date: Sun, 23 Jun 2019 18:38:03 GMT
		Connection: keep-alive

		{"name":"cncjs","version":"1.9.20","description":"A web-based interface for CNC milling controller running Grbl, Marlin, Smoothieware, or TinyG","homepage":"https://github.com/cncjs/cncjs"}

		'''

	def wait(self):
		while (self.active_state not in ['Idle','Alarm','PacketOK','Hold','Sleep']):
			print("wait=",self.active_state)
			self.sio.sleep(0.05)


"""
'server_ip': '127.0.0.1',
'server_port': 8000,
'serial_port': '/dev/tty.MALS',
'serial_baud': 115200,
'controller_type': 'Grbl',
'user_id': '',
'user_name': 'cncjs-pendant',
'user_pass': '',
'ws_secret': '$2a$10$6LHS.kcGOmdGcu2kmbTMUu',
'sio': <socketio.client.Client object at 0x10ce2f2e8>,
'access_token': b'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IiIsIm5hbWUiOiJjbmNqcy1wZW5kYW50In0.aDWMfveVjKazAw1GvQ-XcxCE-vE4cfeYzTTdNIrdvck',
'access_token_url_string': 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6IiIsIm5hbWUiOiJjbmNqcy1wZW5kYW50In0.aDWMfveVjKazAw1GvQ-XcxCE-vE4cfeYzTTdNIrdvck',
'startup_data': {'loadedControllers': ['Grbl', 'Marlin', 'Smoothie', 'TinyG'], 'baudrates': [], 'ports': []},
'serial_state': {'port': '/dev/tty.MALS', 'baudrate': 115200, 'controllerType': 'Grbl', 'inuse': True},
'controller_settings': {'version': '', 'parameters': {}, 'settings': {}},
'controller_state': {'status': {'activeState': '', 'mpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'wpos': {'x': '0.000', 'y': '0.000', 'z': '0.000'}, 'ov': []}, 'parserstate': {'modal': {'motion': 'G0', 'wcs': 'G54', 'plane': 'G17', 'units': 'G21', 'distance': 'G90', 'feedrate': 'G94', 'program': 'M0', 'spindle': 'M5', 'coolant': 'M9'}, 'tool': '', 'feedrate': '', 'spindle': ''}},
'feeder_status': 	{'hold': False, 'holdReason': None, 'queue': 0, 'pending': False, 'changed': False},
'sender_status': 	{'sp': 1, 'hold': False, 'holdReason': None, 'name': '', 'context': {}, 'size': 0, 'total': 0, 'sent': 0, 'received': 0, 'startTime': 0, 'finishTime': 0, 'elapsedTime': 0, 'remainingTime': 0},
'workflow_state': 'idle'}
"""

