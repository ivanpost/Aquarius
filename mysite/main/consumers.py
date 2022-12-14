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
        if prefix in ControllerConsumer.consumers.keys():
            ControllerConsumer.consumers[prefix].send(text_data=json.dumps({"type": "data_downloaded"}))

    @staticmethod
    def send_properties(prefix, properties, is_time_updated=True):
        properties["type"] = "properties"

        # если время не изменилось с последней отправки, то не отправляем его на страницу.
        # необходимо, чтобы не появлялось предложение синхронизировать время в случае,
        # если на сервере не успели обновиться данные
        if not is_time_updated:
            for k in ("hour", "minute"):
                if k in properties.keys():
                    del properties[k]


        if prefix in ControllerConsumer.consumers.keys():
            ControllerConsumer.consumers[prefix].send(text_data=json.dumps(properties))

    def receive(self, text_data=None, bytes_data=None):
        from ControllerManagers import ControllerV2Manager

        json_data = json.loads(text_data)
        if "mqtt_user" not in json_data.keys() or "command" not in json_data:
            self.send(text_data=json.dumps({'error': "invalid syntax"}))
            return

        mqtt_user = json_data["mqtt_user"]
        ControllerConsumer.consumers[mqtt_user] = self

        command = json_data["command"]

        instance = ControllerV2Manager.get_instance(mqtt_user)
        if instance is None:
            self.send(text_data=json.dumps({'error': "invalid prefix"}))
            return

        if command == "download_data":
            instance.command_get_channels()
        elif command == "get_properties":
            instance.command_get_state()
        elif command == "set_name" and "data" in json_data.keys():
            instance.set_name(json_data["data"])



