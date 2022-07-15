import datetime
import time
from bitstring import BitStream, BitArray
from RedisService import RedisService

import paho.mqtt.client as MQTT
import random

DEBUG = True
Instance = None


def _int(i):
    try:
        return int(i)
    except:
        return 0


class MQTTManager:

    client = None

    '''def __call__(self, *args, **kwargs):
        self.host = '185.134.36.37'
        self.port = 18883
        self.user = '221'
        self.password = '183015864'
        self.prefix = "221/"
        self.connect()'''

    def send(self, topic, data):
        if self.client is None:
            return
        if DEBUG: print(f"MQTT: Send to [{topic}]: {data}")
        self.client.publish(self.prefix + topic, data)

    @staticmethod
    @RedisService.event_handler("mqtt:subscribe")
    def subscribe_handler(channel, data):
        Instance.subscribe(data)

    @staticmethod
    @RedisService.event_handler("mqtt:send:*")
    def send_handler(channel, data):
        topic = channel.replace("mqtt:send:", "")
        Instance.send(topic, data)

    def subscribe(self, topics):
        self.client.subscribe(self.prefix + topics)
        print(f'MQTT: Subscribed to {self.prefix + topics}')

    def connect(self):
        self.client = MQTT.Client()
        self.client.username_pw_set(self.user, self.password)
        self.client.on_message = lambda cl, userdata, message: self.on_message(userdata, message)
        self.client.connect(self.host, port=self.port, keepalive=10)
        RedisService.publish("mqtt:connected")
        print(f'MQTT: Connected to {self.user}@{self.host}:{self.port}')
        #from main.models import Controller, Channel, Program
        global Controller, Channel, Program
        self.client.loop_forever()

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
        #if DEBUG: print(f'MQTT - [{message.topic.replace(self.prefix, "")}] - {str(message.payload.decode("utf-8")).strip()}')
        RedisService.publish(f"mqtt:message:{message.topic.replace(self.prefix, '')}", str(message.payload.decode("utf-8")).strip())

    def __init__(self):
        self.host = '185.134.36.37'
        self.port = 18883
        self.user = '2E8'
        self.password = '433987208'
        self.prefix = f"{self.user}/"


if __name__ == "__main__":
    Instance = MQTTManager()
    Instance.connect()

    while True:
        pass