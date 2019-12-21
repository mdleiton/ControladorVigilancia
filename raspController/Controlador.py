import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep
from datetime import datetime
import requests
import syslog


class Controlador:
	def __init__(self, parametros):
    	self.parametros = parametros
