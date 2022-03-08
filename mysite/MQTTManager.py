import time

import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
    print("message qos=",message.qos)
    print("message retain flag=",message.retain)


client = mqtt.Client("P1")
client.username_pw_set("WEB", "456456")
client.on_message = on_message
client.connect("185.134.36.37", port=18883)
client.loop_start()
client.subscribe("WEB/test")
client.publish("WEB/test", "Hello World!")


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