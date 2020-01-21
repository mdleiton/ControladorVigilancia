import requests
import syslog
from datetime import datetime

URL_SERVER = "http://192.168.0.9:8081/"
END_POINT_SEND_ALARM = "novelties/"
API_LOGIN = "api-token-auth/ "
DIR_VIDEOS = ""
TOKEN = None
CREDENTIALS = {'username': "admin1", 'password': "adminadmin"}

def obtener_fecha_hora():
    """permite obtener una cadena de texto que representa la fecha actual."""
    now = datetime.now()
    return now.strftime("%d-%m-%Y_%H:%M:%S")


headers= {}
r = requests.post(URL_SERVER + API_LOGIN,data=CREDENTIALS, timeout=2)
if "token" in r.json():
    headers["Authorization"] = "Token " + r.json()["token"]
data = {"date_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "node": URL_SERVER + "nodes/1/", "region": "1"}
files = {}
files["video"] = open("19-12-2019_15:42:24.h264", 'rb')
r = requests.post(URL_SERVER + END_POINT_SEND_ALARM, data=data, files=files, timeout=None, headers=headers)
if r.status_code ==  201:
    syslog.syslog("Foto tomada, enviada correctamente.")
else:
    syslog.syslog("Foto tomada, no se puede enviar.")
