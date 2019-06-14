#!/usr/local/bin/python3

import websocket
import requests # pip install requests / https://pypi.org/project/requests/
import sys, asyncore
import jwt
import logging
from socketio_client.manager import Manager  # pip install python-socketio-client / https://pypi.org/project/python-socketio-client/

import gevent
from gevent import monkey;
monkey.patch_socket()

#SERVER_ADDRESS = "192.168.0.19" # cncox
SERVER_ADDRESS = "127.0.0.1" # localhost
SERVER_PORT = 8000

SERIAL_PORT = "/dev/tty.MALS" # e.g. /dev/ttyACM0
SERIAL_BAUDRATE = 115200
CONTROLLER_TYPE = "Grbl"

#SECRET = "$2a$10$IYnT/KjMHedGJUqaS.riNe" # cncox
SECRET = "$2a$10$6LHS.kcGOmdGcu2kmbTMUu" # localhost
USER_ID = "" # obtained from ~/.cncrc
USER_NAME = "cnc"
USER_PASS = ""

access_token = jwt.encode({'id': USER_ID, 'name': USER_NAME}, SECRET, algorithm='HS256')
access_token_url_string = "{}".format(access_token.decode('utf-8'))

# can't install with pip...