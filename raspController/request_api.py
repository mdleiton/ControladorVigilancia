import requests
import syslog
from datetime import datetime

URL_SERVER = "http://10.42.0.1:8081/"
END_POINT_SEND_ALARM = "novelties/"
API_LOGIN = "api-token-auth/ "
DIR_VIDEOS = ""
CREDENTIALS = {'username': "admin1", 'password': "adminadmin"}

headers= {}
r = requests.post(URL_SERVER + API_LOGIN,data=CREDENTIALS, timeout=None)
if "token" in r.json():
    headers["Authorization"] = "Token " + r.json()["token"]
data = {"date_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "node": "1", "region": "1"}
files = {}
files["video"] = open("21-01-2020_13:31:05.mp4", 'rb')
r = requests.post(URL_SERVER + END_POINT_SEND_ALARM, data=data, files=files, timeout=None, headers=headers)
if r.status_code ==  201:
    syslog.syslog("Foto tomada, enviada correctamente.")
else:
    syslog.syslog("Foto tomada, no se puede enviar.")
