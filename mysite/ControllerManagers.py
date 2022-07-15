from MQTTManager import MQTTManager
from main.models import Controller, Channel, UserExtension
import datetime
from bitstring import BitArray
from django.contrib.auth.models import User
import json
def try_int(i):
    try:
        return int(i)
    except:
        return 0


class ControllerV2Manager:

    instances = {}

    cmd_pattern = "1.2.3.4.3.2.1.{request_code}.{payload}.{check_sum[0]}.{check_sum[1]}.9.8.7.6.7.8.9"
    topic_send = "aqua_smart"
    topic_receive = "aqua_kontr"

    prefix: str
    command_response_handlers: dict

    last_command: str
    data_model: Controller
    mqtt_manager: MQTTManager

    @staticmethod
    def get_instance(prefix: str):
        if prefix in ControllerV2Manager.instances.keys():
            return ControllerV2Manager.instances[prefix]
        else:
            return None

    @staticmethod
    def add(prefix: str, password: str):
        if ControllerV2Manager.get_instance(prefix) is None:
            mqtt = MQTTManager.try_connect(prefix, password)
            if mqtt is not None:
                cm = ControllerV2Manager(prefix, password, mqtt)
                cm.subscribe(mqtt)
                cm.on_connected(mqtt)
                return True
            else:
                return False
        else:
            return True


    @staticmethod
    def check_auth(prefix: str = "", password: str = "", user: User = None) -> bool:
        if user is not None:
            try:
                saved_controllers = user.userextension.saved_controllers
            except:
                uex = UserExtension(user=user, saved_controllers="[]")
                uex.save()
                saved_controllers = "[]"
                return False
            if saved_controllers is None:
                saved_controllers = []
            else:
                saved_controllers = json.loads(saved_controllers)
            s_cont = [c for c in saved_controllers if c[0] == prefix]
            if len(s_cont) > 0:
                return ControllerV2Manager.check_auth(s_cont[0][0], s_cont[0][1])
        else:
            instance = ControllerV2Manager.get_instance(prefix)
            return instance is not None and instance.data_model.prefix == prefix and instance.data_model.password == password

    def __init__(self, controller_prefix: str, password: str, mqtt_manager: MQTTManager):
        try:
            self.data_model = Controller.objects.get(prefix=controller_prefix)
        except:
            self.data_model = Controller(prefix=controller_prefix, password=password)
            self.data_model.save()

        self.mqtt_manager = mqtt_manager
        self.prefix = controller_prefix
        self.command_response_handlers = {
            "8.8.8.8.8.8.8.8": self.command_get_state_response,
            "0.0.8": self.command_get_channels_response,
        }
        ControllerV2Manager.instances[self.prefix] = self

    def subscribe(self, mqtt: MQTTManager) -> None:
        mqtt.subscribe(self.topic_receive, self.handle_message)
        mqtt.onConnected = self.on_connected

    def send_command(self, request_code: str, payload: str = ""):
        msg = self.wrap_command(request_code, payload)
        self.last_command = request_code
        self.mqtt_manager.send(self.topic_send, msg)

    def wrap_command(self, request_code: str, payload: str) -> str:
        return self.cmd_pattern.format(request_code=request_code, payload=payload, check_sum=self.get_check_sum(payload))

    def command_get_channels(self) -> None:
        self.send_command("0.0.8")

    def command_get_channels_response(self, data, **kwargs) -> bool:
        print(data)
        s = list(map(try_int, data.split(".")))
        [print(f"{num}: {i}") for num, i in enumerate(s)]
        return False

    def command_get_state(self) -> None:
        self.send_command("8.8.8.8.8.8.8.8")

    def command_get_state_response(self, data, **kwargs) -> bool:
        try:
            data = kwargs["old_data"]
            #print(f"Message: {data}")
            s = list(map(try_int, data.split(".")))
            #[print(f"{num}: {i}") for num, i in enumerate(s)]
            self.data_model.time = datetime.time(s[8], s[9], s[10])
            self.data_model.day = s[11]
            self.data_model.week = bool(s[21])
            self.data_model.nearest_chn = s[23]
            try:
                self.data_model.nearest_time = datetime.time(s[24], s[25])
            except ValueError:
                self.data_model.nearest_time = datetime.time(0, 0)
            self.data_model.t1 = s[12]
            self.data_model.t2 = s[13]
            self.data_model.t_amount = s[19]
            self.data_model.rain = bool(s[14])
            self.data_model.pause = bool(s[26])
            self.data_model.version = s[27]
            self.data_model.ip = f"{s[28]}.{s[29]}.{s[30]}.{s[31]}"
            self.data_model.esp_v = f"{s[32]}.{s[33]}.{s[34]}"
            esp_d = BitArray(int=s[35], length=8)[::-1]
            self.data_model.esp_connected = esp_d[0]
            self.data_model.esp_ap = esp_d[1]
            self.data_model.esp_net = esp_d[2]
            self.data_model.esp_mqtt = esp_d[3]
            self.data_model.esp_errors = esp_d[4]
            self.data_model.pressure = s[36]
            self.data_model.stream = s[37]
            self.data_model.num = f"{s[39]}-{s[40]}"

            db_chns = Channel.objects.all()
            chns = list(BitArray(uint=s[15], length=8)) + list(BitArray(uint=s[16], length=8)) + list(
                BitArray(uint=s[17], length=8)) + list(BitArray(uint=s[18], length=8))
            for c in db_chns:
                s = chns[c.id - 1]
                if c.state != s:
                    c.state = s
                    c.save()
            self.data_model.save()
            return True
        except:
            return False

    def on_connected(self, mqtt: MQTTManager):
        #self.command_get_state()
        self.command_get_channels()

    def get_check_sum(self, data: str) -> (int, int):
        bytes = sum(list(data.encode("ascii"))).to_bytes(2, "little")
        return bytes[0], bytes[1]

    def handle_message(self, mqtt: MQTTManager, controller_prefix: str, data: str) -> None:
        if self.last_command in self.command_response_handlers.keys():
            if self.command_response_handlers[self.last_command](data.replace(".1.2.3.4.3.2.1.", "").replace(".9.8.7.6.7.8.9..", ""), old_data=data):
                self.last_command = ""


#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.44.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.38.0.0.5.142.127.9.8.7.6.7.8.9..
#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.45.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.37.0.0.5.142.127.9.8.7.6.7.8.9..

