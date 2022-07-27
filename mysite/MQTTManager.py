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
    connected = False
    trying = 2

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

    def subscribe(self, topic, func):
        self.topicHandlers[topic] = func
        self.client.subscribe(self.prefix + topic)

    def on_connected(self, client, userdata, flags, rc):
        if self.trying > 0:
            self.trying -= 1
        else:
            return False
        if rc == 0:
            print(f'MQTT: Connected to {self.user}@{self.host}:{self.port}')
            # from main.models import Controller, Channel, Program
            if self.onConnected is not None:
                self.onConnected(self)
            self.connected = True
            self.trying = 0
            return True
        else:
            self.connected = False
            return False

    def connect(self):
        self.client = MQTT.Client()
        self.client.username_pw_set(self.user, self.password)
        self.client.on_message = lambda cl, userdata, message: self.on_message(userdata, message)
        self.client.on_connect = self.on_connected
        self.client.connect(self.host, port=self.port, keepalive=15)
        self.client.loop_start()
        while self.trying > 0:
            pass
        return self.connected


    def on_message_kontr(self, mqtt, prefix, message):
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
        #print(f'MQTT - [{message.topic.replace(self.prefix, "")}] - {str(message.payload.decode("utf-8")).strip()}')
        if message.topic.replace(self.prefix, '') in self.topicHandlers.keys():
            self.topicHandlers[message.topic.replace(self.prefix, "")](self, self.user, str(message.payload.decode("utf-8")).strip())

    def __init__(self, user, password):
        self.host = '185.134.36.37'
        self.port = 18883
        #self.user = '2E8'
        self.user = user
        #self.password = '433987208'
        self.password = password
        self.prefix = f"{self.user}/"

    @staticmethod
    def try_connect(user: str, password: str):
        try:
            m = MQTTManager(user, password)
            s = m.connect()
            return m if s else None
        except:
            return None
