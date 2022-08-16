import json
from channels.generic.websocket import WebsocketConsumer


class ControllerConsumer(WebsocketConsumer):

    consumers = {}
    name = 'controller'

    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        to_delete = []
        for k, v in ControllerConsumer.consumers.items():
            if v == self:
                to_delete.append(k)

        for k in to_delete:
            del ControllerConsumer.consumers[k]

    @staticmethod
    def send_data_downloaded(prefix):
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager
        if prefix in ControllerConsumer.consumers.keys():
            ControllerConsumer.consumers[prefix].send(text_data=json.dumps({"type": "data_downloaded"}))

    @staticmethod
    def send_properties(prefix, properties):
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager
        properties["type"] = "properties"
        if prefix in ControllerConsumer.consumers.keys():
            ControllerConsumer.consumers[prefix].send(text_data=json.dumps(properties))

    def receive(self, text_data=None, bytes_data=None):
        from main.models import Controller
        from ControllerManagers import ControllerV2Manager

        json_data = json.loads(text_data)
        if "prefix" not in json_data or "command" not in json_data:
            self.send(text_data=json.dumps({'error': "invalid syntax"}))

        prefix = json_data["prefix"]
        ControllerConsumer.consumers[prefix] = self

        command = json_data["command"]
        instance = ControllerV2Manager.get_instance(prefix)
        if instance is None:
            self.send(text_data=json.dumps({'error': "invalid prefix"}))

        if command == "download_data":
            instance.command_get_channels()
        elif command == "get_properties":
            instance.command_get_state()
        elif command == "set_name" and "data" in json_data.keys():
            instance.set_name(json_data["data"])



