from MQTTManager import MQTTManager
from django.apps import AppConfig

class MainConfig(AppConfig):
    name = 'main'
    verbose_name = "Main app"

    manager = None
    counter = 0

    def on_message_kontr(self, manager, message):
        print(message)

    def on_connected(self, manager, client, userdata, flags, rc):
        manager.send("aqua_smart", "1.2.3.4.3.2.1.8.8.8.8.8.8.8.8.8.8.0.80.9.8.7.6.7.8.9.9")

    def ready(self):
        self.manager = MQTTManager('185.134.36.37', '18883', '221', '183015864', "221/")
        self.manager.onConnected = self.on_connected
        self.manager.topicHandlers["aqua_kontr"] = self.on_message_kontr
        self.manager.connect()

