import datetime
import time
from bitstring import BitStream, BitArray

import paho.mqtt.client as MQTT
import random

def _int(i):
    try:
        return int(i)
    except:
        return 0

class MQTTManager:

    client = None
    onConnected = None
    topicHandlers = {}

    def __call__(self, *args, **kwargs):
        self.host = '185.134.36.37'
        self.port = 18883
        self.user = '221'
        self.password = '183015864'
        self.prefix = "221/"
        self.connect()

    def send(self, topic, data):
        if self.client == None:
            return
        print(f"MQTT: Send to [{topic}]: {data}")
        self.client.publish(self.prefix + topic, data)

    def on_disconnect(self, *args):
        self.client.on_message = lambda: True


    def connect(self):
        self.client = MQTT.Client()
        self.topicHandlers["aqua_kontr"] = self.on_message_kontr
        self.client.username_pw_set(self.user, self.password)
        self.client.on_message = lambda cl, userdata, message: self.on_message(userdata, message)
        if not self.onConnected == None: self.client.on_connect = lambda cl, ud, fl, rc: self.on_connected
        self.client.on_connect = lambda cl, ud, fl, rc: self.on_disconnect
        self.client.connect(self.host, port=self.port, keepalive=10)
        print(f'MQTT: Connected to {self.user}@{self.host}:{self.port}')
        print(self.topicHandlers)
        for t in self.topicHandlers.keys():
            self.client.subscribe(self.prefix + t)

        print(f'MQTT: Subscribed to {", ".join([self.prefix + n for n in self.topicHandlers.keys()])}')
        global Controller, Channel, Program
        from main.models import Controller, Channel, Program
        self.on_connected()



    def on_connected(self):
        self.send("aqua_smart", "1.2.3.4.3.2.1.8.8.8.8.8.8.8.8.8.8.0.80.9.8.7.6.7.8.9.9")


    def on_message_kontr(self, message):
        s = list(map(_int, message.split(".")))
        k = Controller.objects.all()[0]
        k.time = datetime.time(s[8], s[9], s[10])
        k.day = s[11]
        k.week = bool(s[21])
        k.nearest_chn = s[23]
        k.nearest_time = datetime.time(s[24], s[25])
        k.t1 = s[12]
        k.t2 = s[13]
        k.t_amount = s[19]
        k.rain = bool(s[14])
        k.pause = bool(s[26])
        k.version = s[27]
        k.ip = f"{s[28]}.{s[29]}.{s[30]}.{s[31]}"
        k.esp_v = f"{s[32]}.{s[33]}.{s[34]}"
        esp_d = BitArray(int=s[35], length=8)[::-1]
        k.esp_connected = esp_d[0]
        k.esp_ap = esp_d[1]
        k.esp_net = esp_d[2]
        k.esp_mqtt = esp_d[3]
        k.esp_errors = esp_d[4]
        k.pressure = s[36]
        k.stream = s[37]
        k.num = f"{s[39]}-{s[40]}"

        db_chns = Channel.objects.all()
        chns = list(BitArray(uint=s[15], length=8)) + list(BitArray(uint=s[16], length=8)) + list(BitArray(uint=s[17], length=8)) + list(BitArray(uint=s[18], length=8))
        for c in db_chns:
            s = chns[c.id-1]
            if c.state != s:
                c.state = s
                c.save()

        k.save()


    def on_message(self, userdata, message):
        print(f'MQTT - [{message.topic.replace(self.prefix, "")}] - {str(message.payload.decode("utf-8")).strip()}')
        if message.topic.replace(self.prefix, '') in self.topicHandlers.keys():
            self.topicHandlers[message.topic.replace(self.prefix, "")](str(message.payload.decode("utf-8")).strip())

    def __init__(self):
        self.host = '185.134.36.37'
        self.port = 18883
        self.user = '221'
        self.password = '183015864'
        self.prefix = "221/"

#m = MQTTManager()
#m.connect()


"""
Prg: 
1 - номер программы
2 - дни недели (перевести в bin)
3 - час
4 - минута
5 - резерв
6 - время полива при мин температуре (мин)
7 - время полива при макс температуре (мин)
"""