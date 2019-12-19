import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep
from datetime import datetime
import requests
import syslog
syslog.syslog('Controlador Inicializado')

GPIO.setmode(GPIO.BOARD)

SENSOR_MOVIMIENTO_1 = 11    ### en 0 grados
DIR_SENSOR_MOVIMIENTO_1 = 0
SENSOR_MOVIMIENTO_2 = 13    ### en 180 grados
DIR_SENSOR_MOVIMIENTO_2 = 180
SERVOR_MOTOR = 12

# POSIBLES PARAMETRO DE UN NODOS
CANTIDAD_FOTOS = 1
INTENTOS_NOTIFICAR = 1
DIR_IMAGENES = "/home/pi/imagenes/"
DIR_VIDEOS = "/home/pi/video/"
URL_SERVER = "http://200.126.1.152:8080/"
END_POINT_SEND_ALARM = "alarm/"

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
#camera.framerate = 15

def tomar_foto(nombre):
    """toma una foto y la guarda con nombre en DIR_IMAGENES"""
    syslog.syslog('Foto tomada, guardada con nombre:' + nombre)
    #camera.start_preview()
    camera.annotate_text = nombre
    #sleep(1)
    camera.annotate_text_size = 50   # tamano
    camera.annotate_background = Color('blue')
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
    envio_correcto = True
    for i in range(CANTIDAD_FOTOS):
        intentos = INTENTOS_NOTIFICAR
        while intentos>0:
            intentos -= 1
            nombre = obtener_fecha_hora() +  ".jpg"
            tomar_foto(nombre)
            files = {'media': open(DIR_IMAGENES + nombre, 'rb')}
            """r = requests.post(URL_SERVER + END_POINT_SEND_ALARM, files=files)
            if r.status_code ==  200:
                syslog.syslog('Foto tomada, guardada con nombre:' + nombre + " enviada correctamente.")
            else:
                syslog.syslog('Foto tomada, guardada con nombre:' + nombre + " no se puede enviar.")
                envio_correcto = False
            """
    return envio_correcto

def mover_x_angulos(angulos):
    """controla el servomotor, hace que se mueva x angulo en grados."""
    global ANGULO_ACTUAL
    if ANGULO_ACTUAL != angulos:
        duty = angulos / 18 + 2
        GPIO.output(SERVOR_MOTOR, True)
        pwm.ChangeDutyCycle(duty)
        sleep(1)
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
    return not GPIO.input(id_sensor)

syslog.syslog('Sensores correctamente inicializados.')
mover_x_angulos(180)
try:
    while True:
        if detectar_movimiento(SENSOR_MOVIMIENTO_1):
            syslog.syslog('Sensor de movimiento 1 a detectado movimiento.')
            notificar(SENSOR_MOVIMIENTO_1)
        """
        if detectar_movimiento(SENSOR_MOVIMIENTO_2):
            syslog.syslog('Sensor de movimiento 2 a detectado movimiento.')
            notificar(SENSOR_MOVIMIENTO_2)
        """
        mover_x_angulos(180)
        sleep(1)
except KeyboardInterrupt:
    syslog.syslog(syslog.LOG_ERR, 'Controlador a finalizado inesperadamente.')
    pwm.stop()
    GPIO.cleanup()
    syslog.closelog()
