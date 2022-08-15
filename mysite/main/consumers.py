import json
from channels.generic.websocket import WebsocketConsumer


class ControllerConsumer(WebsocketConsumer):

    consumers = []
    name = 'controller'

    def connect(self):
        self.accept()
        ControllerConsumer.consumers.append(self)

    def disconnect(self, close_code):
        ControllerConsumer.consumers.remove(self)

    @staticmethod
    def send_data_downloaded():
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager
        print("Send data downloaded")
        for cons in ControllerConsumer.consumers:
            cons.send(text_data=json.dumps({"type": "data_downloaded"}))

    @staticmethod
    def send_properties(properties):
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager


        properties["type"] = "properties"
        for cons in ControllerConsumer.consumers:
            cons.send(text_data=json.dumps(properties))

    def receive(self, text_data=None, bytes_data=None):
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager

        json_data = json.loads(text_data)
        if "prefix" not in json_data or "command" not in json_data:
            self.send(text_data=json.dumps({'error': "invalid syntax"}))

        prefix = json_data["prefix"]
        command = json_data["command"]
        instance = ControllerV2Manager.get_instance(prefix)
        if instance is None:
            self.send(text_data=json.dumps({'error': "invalid prefix"}))

        if command == "download_data":
            instance.command_get_channels()
        elif command == "get_properties":
            print("command get properties")
            instance.command_get_state()



