import RPi.GPIO as GPIO
from picamera import PiCamera, Color
from time import sleep

GPIO.setmode(GPIO.BOARD)


SENSOR_MOVIMIENTO_1 = 11    ### en 0 grados
DIR_SENSOR_MOVIMIENTO_1 = 0
SENSOR_MOVIMIENTO_2 = 13    ### en 180 grados
DIR_SENSOR_MOVIMIENTO_2 = 180
SERVOR_MOTOR = 12


# POSIBLES PARÁMETROS NODOS
CANTIDAD_FOTOS = 2
INTENTOS_NOTIFICAR = 3
DIR_IMAGENES = "/home/pi/imagenes/"
DIR_VIDEOS = "/home/pi/video/"

# configuración del primer sensor de movimiento
GPIO.setup(SENSOR_MOVIMIENTO_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# configuración del segundo sensor de movimiento
GPIO.setup(SENSOR_MOVIMIENTO_1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# configuración del servomotor
GPIO.setup(SERVOR_MOTOR, GPIO.OUT)
pwm = GPIO.PWM(SERVOR_MOTOR, 50)
pwm.start(0)

# configuración de la camara
camera = PiCamera()
#camera.resolution = (2592, 1944)
#camera.framerate = 15

def tomar_foto(nombre):
    camera.annotate_text = nombre
    camera.annotate_text_size = 50   # tamano
    camera.annotate_background = Color('blue')
    camera.capture(DIR_IMAGENES + nombre)


def grabar(nombre, tiempo):
    camera.start_recording(DIR_VIDEOS + nombre)         #ejemplo nombre 'video.h264'
    sleep(tiempo)
    camera.stop_recording()



def enviar_fotos():
    """toma fotos y envia al servidor"""
    return True


def mover_x_angulos(angulos):
    """controla el servomotor, hace que se mueva x angulo en grados."""
    duty = angulos / 18 + 2
    GPIO.output(SERVOR_MOTOR, True)
    pwm.ChangeDutyCycle(duty)
    sleep(1)
    GPIO.output(SERVOR_MOTOR, False)
    pwm.ChangeDutyCycle(0)
    sleep(1)

def notificar(id_sensor):
    """en caso de detectar movimiento en id_sensor, se moverá a su ubicación, tomará fotos y enviará al servidor."""
    if id_sensor = SENSOR_MOVIMIENTO_1:
        mover_x_angulos(DIR_SENSOR_MOVIMIENTO_1)
        return enviar_fotos()
    else:
        mover_x_angulos(DIR_SENSOR_MOVIMIENTO_2)
        return enviar_fotos()


def detectar_movimiento(id_sensor):
    """funcion que lee la entrada del sensor de movimiento respectivo y verifica si existe alguna alarma nueva."""
    return not GPIO.input(id_sensor)

try:
    while True:
        if detectar_movimiento(SENSOR_MOVIMIENTO_1):
            intentos = INTENTOS_NOTIFICAR
            while not notificar(SENSOR_MOVIMIENTO_1) and intentos>0:
                intentos -= 1
        if detectar_movimiento(SENSOR_MOVIMIENTO_2):
            intentos = INTENTOS_NOTIFICAR
            while not notificar(SENSOR_MOVIMIENTO_1) and intentos>0:
                intentos -= 1
        sleep(1)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()