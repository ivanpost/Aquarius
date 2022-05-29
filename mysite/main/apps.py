from MQTTManager import MQTTManager
from django.apps import AppConfig
from multiprocessing import Process
from background_task import background

class MainConfig(AppConfig):
    name = 'main'
    verbose_name = "Main app"

    manager = None
    counter = 0

    process = None


    def ready(self):
        m = MQTTManager()
        m.connect()
        m.client.loop_start()

