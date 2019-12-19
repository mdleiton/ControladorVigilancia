import RPi.GPIO as GPIO
from time import sleep

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

try:
    while True:
        print(GPIO.input(11))
        sleep(3)
except KeyboardInterrupt:
    GPIO.cleanup()
