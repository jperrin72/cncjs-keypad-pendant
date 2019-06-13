#!/usr/local/bin/python3

import websocket
import requests # pip install requests / https://pypi.org/project/requests/
import sys, asyncore
import jwt
import logging
import ast

#SERVER_ADDRESS = "192.168.0.19" # cncox
SERVER_ADDRESS = "127.0.0.1" # localhost
SERVER_PORT = 8000
BASE_URL='http://'+SERVER_ADDRESS+':'+str(SERVER_PORT)+'/'

SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200
CONTROLLER_TYPE = "Grbl"

#SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
SECRET = "$2a$10$6LHS.kcGOmdGcu2kmbTMUu" # localhost
USER_ID = "" # obtained from ~/.cncrc
USER_NAME = "cnc"
USER_PASS = ""

signed_jwt = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')

# connect

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
"""

print('\n\r')
session=requests.session()
request = session.get(BASE_URL)
print("request url:{}".format(request.url))
#print("request headers:{}".format(request.headers))
#print('request_payload='+str(request.content))

# sign-in

"""
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
"""

print('\n\r')
auth_token='{"token":"'+'{}'.format(signed_jwt.decode('utf-8'))+'"}'
print('auth_token='+auth_token)
request = session.post(	BASE_URL+'api/signin',
						headers={
						'Authorization': 'Bearer {}'.format(signed_jwt.decode('utf-8')),
						'content-type': 'application/json'
						},data=auth_token)

print("request url:{}".format(request.url))
#set_cookie=request.headers['set-cookie']
REQUEST_URL=BASE_URL+'socket.io/'
#r.headers={'Cookie': c}
auth_token=request.json()['token']
#print('auth_cookie='+auth_token)
#print(r.headers['cookie'])
#print('request_json_payload='+str(request.json()))


# start communication


"""
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



"""

print('\n\r')
request = session.get(REQUEST_URL, params={'token':'{}'.format(auth_token),'transport': ['polling']})
print("request url:{}".format(request.url))
print('request_payload='+str(request.text))
#print("request headers:{}".format(request.headers))
request_sid=ast.literal_eval('{'+request.text.split('{')[1])['sid']
#request_sid=(request.text.split('"sid":"')[1]).split('"')[0]
print('request_sid='+request_sid)

# start API

"""
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
"""

print('\n\r')
request = session.get(REQUEST_URL,params={'token':'{}'.format(auth_token),'transport': ['polling'],'sid': request_sid})
print("request url:{}".format(request.url))
print("request headers:{}".format(request.headers))
print('request_payload='+str(request.content))



#

"""
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
"""

print('\n\r')
request = session.get(REQUEST_URL,params={'token':'{}'.format(auth_token),'transport': ['polling'],'sid': request_sid})
print("request url:{}".format(request.url))
print("request headers:{}".format(request.headers))
print('request_payload='+str(request.content))




# switch to websocket

print('\n\r')


request=session.get(REQUEST_URL, headers={'Connection': 'Upgrade',
						'Upgrade': 'websocket',
						'Sec-Websocket-Key': 'zC7WWRo2t8O2KCXZ9u0zNg==',
						'Sec-Websocket-Extensions': 'x-webkit-deflate-frame',
						'Sec-WebSocket-Version': '13',
						},params={'token':'{}'.format(auth_token),'transport': 'websocket','sid': request_sid},stream=True)

print("request url:{}".format(request.url))
print("request headers:{}".format(request.headers))
print('request_payload='+str(request.content))


while True:
	print(request.raw.read(10))

