import time

import paho.mqtt.client as MQTT

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)

class MQTTManager:

    client = None
    host = ""
    port = 0
    user = ""
    password = ""
    prefix = "WEB/"

    def on_message_test(self, message, **kwargs):
        print(message)

    def connect(self):
        self.client = MQTT.Client("WEB1")
        self.client.username_pw_set(self.user, self.password)
        self.client.on_message = lambda cl, userdata, message: self.on_message(userdata, message)
        self.client.connect(self.host, port=self.port)
        print(f'MQTT: Connected to {self.user}@{self.host}:{self.port}')
        self.client.loop_start()
        for t in self.topicHandlers.keys():
            self.client.subscribe(self.prefix + t)
            print(f'MQTT: Subscribed to {self.prefix + t}')

    def on_message(self, userdata, message):
        if message.topic.replace(self.prefix, '') in self.topicHandlers.keys():
            self.topicHandlers[message.topic.replace(self.prefix, "")](self, str(message.payload.decode("utf-8")))
            print(f'MQTT: [{message.topic.replace(self.prefix, "")}] - {str(message.payload.decode("utf-8"))}')

    def __init__(self, host, port, user, password):
        self.host = str(host)
        self.port = int(port)
        self.user = str(user)
        self.password = str(password)

    topicHandlers = {
        "test": on_message_test
    }

if __name__ == "__main__":
    cl = MQTTManager('185.134.36.37', '18883', 'WEB', '456456')
    cl.connect()

    while True:
        pass


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