from picamera import PiCamera, Color
from time import sleep
# configurate camera
camera.resolution = (2592, 1944)
camera.framerate = 15


camera = PiCamera()
# para tomar fotos.
camera.start_preview()
camera.annotate_text = "colocar fecha!"
camera.annotate_text_size = 50   # tamano
camera.annotate_background = Color('blue')
sleep(5)
camera.capture('/home/pi/Desktop/image.jpg')
camera.stop_preview()


# para grabar
camera.start_preview()
camera.start_recording('/home/pi/Desktop/video.h264')
sleep(5)
camera.stop_recording()
camera.stop_preview()
