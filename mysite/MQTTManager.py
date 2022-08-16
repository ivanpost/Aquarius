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
        print(f"After subscribe {self.user}: {self.topicHandlers}")

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


    def on_message(self, userdata, message):
        print(f'MQTT ({self.user}) - [{message.topic.replace(self.prefix, "")}] - {str(message.payload.decode("utf-8")).strip()}')
        if message.topic.replace(self.prefix, '') in self.topicHandlers.keys():
            self.topicHandlers[message.topic.replace(self.prefix, "")](self, self.user, str(message.payload.decode("utf-8")).strip())
        print(self.topicHandlers)

    def __init__(self, user, password):
        self.topicHandlers = {}
        self.host = '185.134.36.37'
        self.port = 18883
        self.user = user
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
