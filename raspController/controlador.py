import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep
from datetime import datetime
import signal
import requests
import threading
import syslog
import os
syslog.syslog('Controlador Inicializado')

GPIO.setmode(GPIO.BOARD)
contador_foto = 0
SENSOR_MOVIMIENTO_1 = 11    ### en 0 grados
DIR_SENSOR_MOVIMIENTO_1 = 0
SENSOR_MOVIMIENTO_2 = 18    ### en 180 grados
DIR_SENSOR_MOVIMIENTO_2 = 180
SERVOR_MOTOR = 12

# POSIBLES PARAMETRO DE UN NODOS
CANTIDAD_FOTOS = 1
INTENTOS_NOTIFICAR = 1
DIR_IMAGENES = "/home/pi/imagenes/"
DIR_VIDEOS = "/home/pi/videos/"
URL_SERVER = "http://10.42.0.1:8081/"
END_POINT_SEND_ALARM = "novelties/"
API_LOGIN = "api-token-auth/ "
CREDENTIALS = {'username': "admin1", 'password': "adminadmin"}

ANGULO_ACTUAL = 0

# configuracion del primer sensor de movimiento
GPIO.setup(SENSOR_MOVIMIENTO_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# configuracion del segundo sensor de movimiento
GPIO.setup(SENSOR_MOVIMIENTO_2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# configuracion del servomotor
GPIO.setup(SERVOR_MOTOR, GPIO.OUT)
pwm = GPIO.PWM(SERVOR_MOTOR, 50)
pwm.start(0)

# configuracion de la camara
camera = PiCamera()
#camera.resolution = (2592, 1944)
camera.framerate = 15

lock = threading.Lock()

def thread_function():
    global lock, contador_foto, DIR_VIDEOS, URL_SERVER, API_LOGIN, CREDENTIALS, END_POINT_SEND_ALARM
    for i in range(CANTIDAD_FOTOS):
        nombre = obtener_fecha_hora() +  ".h264" #".jpg"
        lock.acquire()
        grabar(nombre, 10)
        #tomar_foto(nombre)
        lock.release()
        nombremp4 = DIR_VIDEOS+nombre[:-5]+".mp4"
        os.rename(DIR_VIDEOS+nombre, nombremp4)
        intentos = INTENTOS_NOTIFICAR
        while intentos>0:
            intentos -= 1
            try:
                headers= {}
                r = requests.post(URL_SERVER + API_LOGIN,data=CREDENTIALS, timeout=2)
                if "token" in r.json():
                    headers["Authorization"] = "Token " + r.json()["token"]
                data = {"date_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "node": "1", "region": "1"}
                files = {}
                files["video"] = open(DIR_VIDEOS + nombremp4, 'rb')
                r = requests.post(URL_SERVER + END_POINT_SEND_ALARM, data=data, files=files, timeout=None, headers=headers)
                if r.status_code ==  201:
                    syslog.syslog("Foto tomada, enviada correctamente.")
                else:
                    syslog.syslog("Foto tomada, no se puede enviar.")
            except Exception:
                syslog.syslog("TimeoutException")
        return 1

def tomar_foto(nombre):
    """toma una foto y la guarda con nombre en DIR_IMAGENES"""
    syslog.syslog('Foto tomada, guardada con nombre:' + nombre)
    #camera.start_preview()
    #camera.annotate_text = nombre
    #sleep(1)
    #camera.annotate_text_size = 50   # tamano
    #camera.annotate_background = Color('blue')
    #camera.stop_preview()
    camera.capture(DIR_IMAGENES + nombre)


def grabar(nombre, tiempo):
    """toma un video de x tiempo en segundos y la guarda con nombre en DIR_VIDEOS"""
    syslog.syslog('Video tomado de ' + str(tiempo) + ' segundos, guardada con nombre:' + nombre)
    camera.start_recording(DIR_VIDEOS + nombre)         #ejemplo nombre 'video.h264'
    sleep(tiempo)
    camera.stop_recording()


def obtener_fecha_hora():
    """permite obtener una cadena de texto que representa la fecha actual."""
    now = datetime.now()
    return now.strftime("%d-%m-%Y_%H:%M:%S")


def enviar_fotos():
    """toma fotos y envia al servidor"""
    x = threading.Thread(target=thread_function)
    x.start()
    return True

def mover_x_angulos(angulos):
    """controla el servomotor, hace que se mueva x angulo en grados."""
    global ANGULO_ACTUAL
    if ANGULO_ACTUAL != angulos:
        duty = angulos / 18 + 2
        GPIO.output(SERVOR_MOTOR, True)
        pwm.ChangeDutyCycle(duty)
        sleep(0.25)
        GPIO.output(SERVOR_MOTOR, False)
        pwm.ChangeDutyCycle(0)
        ANGULO_ACTUAL = angulos

def notificar(id_sensor):
    """en caso de detectar movimiento en id_sensor, se movera a su ubicacion, tomara fotos y enviara al servidor."""
    if id_sensor == SENSOR_MOVIMIENTO_1:
        mover_x_angulos(DIR_SENSOR_MOVIMIENTO_1)
        return enviar_fotos()
    else:
        mover_x_angulos(DIR_SENSOR_MOVIMIENTO_2)
        return enviar_fotos()


def detectar_movimiento(id_sensor):
    """funcion que lee la entrada del sensor de movimiento respectivo y verifica si existe alguna alarma nueva."""
    on = 1 if GPIO.input(id_sensor) == 0 else 0 
    if on>=1:
        return True
    else:
        return False

syslog.syslog('Sensores correctamente inicializados.')

mover_x_angulos(0)
try:
    while True:
        while detectar_movimiento(SENSOR_MOVIMIENTO_1):
            syslog.syslog('Sensor de movimiento 1 a detectado movimiento.')
            notificar(SENSOR_MOVIMIENTO_1)
            contador_foto +=1 
            if contador_foto > 5:
                syslog.syslog('max')
                contador_foto = 0
                sleep(5)
                break
            sleep(4)
        while detectar_movimiento(SENSOR_MOVIMIENTO_2):
            syslog.syslog('Sensor de movimiento 2 a detectado movimiento.')
            notificar(SENSOR_MOVIMIENTO_2)
            contador_foto +=1 
            if contador_foto > 5:
                syslog.syslog('max')
                contador_foto = 0
                sleep(5)
                break
            sleep(4)
        sleep(1)
        #mover_x_angulos(180)
except KeyboardInterrupt:
    syslog.syslog(syslog.LOG_ERR, 'Controlador a finalizado inesperadamente.')
    mover_x_angulos(0)
    pwm.stop()
    GPIO.cleanup()
    syslog.closelog()
mover_x_angulos(0)