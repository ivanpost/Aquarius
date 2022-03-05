import json
from channels.generic.websocket import WebsocketConsumer
import threading

consumers = []

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
        consumers.append(self)

    def disconnect(self, close_code):
        consumers.remove(self)

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        for c in consumers:
            c.send(text_data=json.dumps({
                'message': message
            }))