import json
from channels.generic.websocket import WebsocketConsumer

consumers = {'index': []}

class IndexConsumer(WebsocketConsumer):
    name = 'index'
    def connect(self):
        self.accept()
        consumers[self.name].append(self)

    def disconnect(self, close_code):
        consumers[self.name].remove(self)

    def receive(self, text_data=None, bytes_data=None):
        pass
        '''text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))'''