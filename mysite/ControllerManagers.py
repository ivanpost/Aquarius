from MQTTManager import MQTTManager
from main.models import Controller, Channel, UserExtension, Program
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
import datetime
from bitstring import BitArray
from django.contrib.auth.models import User
import json
from typing import List
from main.consumers import ControllerConsumer
import threading
def try_int(i):
    try:
        return int(i)
    except:
        return 0


class ControllerV2Manager:

    instances = {}

    cmd_pattern = ".1.2.3.4.3.2.1.{request_code}.{payload}.{check_sum[0]}.{check_sum[1]}.9.8.7.6.7.8.9.9."
    topic_send = "aqua_smart"
    topic_receive = "aqua_kontr"

    prefix: str
    command_response_handlers: dict

    blocked: bool = False
    packet: int = -1
    stashed_data: list = []
    last_command: str
    data_model: Controller
    mqtt_manager: MQTTManager

    @staticmethod
    def check_block(prefix: str):
        c = ControllerV2Manager.get_instance(prefix)
        if c is None:
            return True
        return c.blocked

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

        for channel_num in range(1, 31):
            try:
                channel = Channel.objects.get(controller=self.data_model, number=channel_num)
            except ObjectDoesNotExist:
                channel = Channel(controller=self.data_model, number=channel_num)
                channel.save()
            except MultipleObjectsReturned:
                Channel.objects.filter(controller=self.data_model, number=channel_num).delete()

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
        print(self.blocked)
        if not self.blocked:
            msg = self.wrap_command(request_code, payload)
            self.last_command = request_code
            self.mqtt_manager.send(self.topic_send, msg)

    def turn_off_all_channels(self):
        active_channels = Channel.objects.filter(controller__prefix=self.prefix, state=True)

        for i in active_channels:
            self.command_turn_on_channel(i.number, 0)

    def wrap_command(self, request_code: str, payload: str) -> str:
        return self.cmd_pattern.format(request_code=request_code, payload=payload,
                                       check_sum=self.get_check_sum(request_code, payload))

    def command_turn_on_channel(self, channel_num, minutes) -> None:
        minutes_bytes = minutes.to_bytes(2, "big")
        self.send_command("0.0.2", f"{channel_num}.{minutes_bytes[0]}.{minutes_bytes[1]}")

    def command_pause(self, minutes) -> None:
        minutes_bytes = minutes.to_bytes(2, "big")
        self.send_command("0.0.7", f"{minutes_bytes[0]}.{minutes_bytes[1]}")

    def command_get_channels(self) -> None:
        self.send_command("0.0.8")

    def edit_or_add_program(self, channel_num: int, prg_num: int, days: str, weeks: tuple, start_hour: int, start_minute: int, t_min: int, t_max: int):
        chan = Channel.objects.get(controller__prefix=self.data_model.prefix, number=channel_num)
        prg = Program.objects.filter(channel=chan, number=prg_num)
        if len(prg) > 0:
            prg = prg[0]
        else:
            prg = Program()
        prg.channel = chan
        prg.number = prg_num
        prg.days = days
        prg.weeks = int(f'{int(weeks[0])}{int(weeks[1])}', 2)
        prg.hour = start_hour
        prg.minute = start_minute
        prg.t_min = t_min
        prg.t_max = t_max
        prg.save()
        self.command_send_channel(channel_num)

    def create_program(self, channel_num: int) -> Program:
        chan = Channel.objects.get(controller__prefix=self.data_model.prefix, number=channel_num)
        programs = Program.objects.filter(channel=chan)
        if len(programs) == 0:
            prg_num = 1
        else:
            prg_num = max([i.number for i in programs]) + 1
        prg = Program()
        prg.channel = chan
        prg.number = prg_num
        prg.days = "1234567"
        prg.weeks = 3
        prg.hour = 0
        prg.minute = 0
        prg.t_min = 60
        prg.t_max = 120
        prg.save()
        self.command_send_channel(channel_num)
        return prg

    def command_send_channel(self, chn):
        channel = Channel.objects.get(controller=self.data_model, number=chn)
        chn_settings = [channel.cmin, channel.cmax, channel.meandr_on, channel.meaoff_cmin, channel.meaoff_cmax,
                        int(channel.press_on * 10), int(channel.press_off * 10), 0, 0,
                        channel.season, 0, 0, 0, int(channel.rainsens), channel.tempsens, 0, 0, 0, 0]
        programs = Program.objects.filter(channel=channel)
        prgs = []
        for prg in programs:
            days = int(''.join([(str(int(str(i) in prg.days))) for i in range(1, 8)]), 2)
            prg_data = [days, prg.weeks, prg.hour, prg.minute, prg.t_min, prg.t_max]
            prgs.append(".".join([str(i) for i in prg_data]))
        str_data = ".".join([str(i) for i in chn_settings]) + "." + ".".join([str(i) for i in prgs])
        self.send_command(f"0.{channel.number}.6", str_data)

    def command_get_channels_response(self, data: str, **kwargs) -> bool:
        bytes_in_packet = 35
        total_packets = 27

        if True:
            self.blocked = True
            data = data.split(".10.11.12.13.12.11.10")[0]
            parsed_message = list(map(try_int, data.split(".")))
            packet_number = parsed_message[0]
            del parsed_message[0]

            if packet_number != self.packet + 1 or len(parsed_message) != bytes_in_packet:
                self.packet = -1
                self.stashed_data = []
                self.blocked = False
                ControllerConsumer.send_data_downloaded()
                return True

            missed_bytes = max((packet_number - self.packet - 1), 0) * bytes_in_packet
            self.stashed_data += [0] * missed_bytes
            self.stashed_data += parsed_message
            self.packet = packet_number
            print(f"Packet: {packet_number}")

            if packet_number >= total_packets - 1:
                if len(self.stashed_data) < total_packets * bytes_in_packet:
                    self.stashed_data += [0] * (total_packets * bytes_in_packet - len(self.stashed_data))

                skip_start = 20
                self.stashed_data = self.stashed_data[skip_start:]

                total_channels = 10
                bytes_for_channel = 20
                for i in range(total_channels):
                    offset = bytes_for_channel * i
                    try:
                        channel_model: Channel = Channel.objects.get(controller=self.data_model, number=i)
                    except ObjectDoesNotExist:
                        channel_model: Channel = Channel(controller=self.data_model, number=i, name=f"Канал {i}")

                    channel_model.cmin, channel_model.cmax, channel_model.meandr_on, channel_model.meaoff_cmin, \
                    channel_model.meaoff_cmax, channel_model.press_on, channel_model.press_off,\
                    _, _, channel_model.season, _, _, _, channel_model.rainsens, channel_model.tempsens,\
                    channel_model.lowlevel, _, _, _, _ = self.stashed_data[offset:offset+20]

                    channel_model.save()

                total_programs = 80
                bytes_for_program = 8
                for i in range(total_programs):
                    offset = bytes_for_program * i + 220
                    if self.stashed_data[offset] <= 0 or self.stashed_data[offset] >= total_programs:
                        continue

                    channel_model: Channel = Channel.objects.get(controller=self.data_model, number=self.stashed_data[offset]+1)
                    try:
                        program_model: Program = Program.objects.get(channel=channel_model, number=self.stashed_data[offset+1])
                    except ObjectDoesNotExist:
                        program_model: Program = Program(channel=channel_model, number=self.stashed_data[offset+1])

                    program_model.days = ''.join([str(num+1) for num, j in enumerate(list("{0:b}".format(self.stashed_data[offset + 2]))) if bool(int(j))])
                    program_model.weeks, program_model.hour, program_model.minute, program_model.t_min,\
                    program_model.t_max = self.stashed_data[offset+3:offset+8]

                    program_model.save()

                ControllerConsumer.send_data_downloaded()
                self.packet = -1
                self.stashed_data = []
                self.blocked = False
                return True
        '''except:
            self.packet = -1
            self.stashed_data = []
            self.blocked = False
            ControllerConsumer.send_data_downloaded()
            return True'''
        return False

    def get_controller_properties(self) -> dict:
        channels = Channel.objects.filter(controller__prefix=self.data_model.prefix)
        channels_state = [i.state for i in channels]

        properties = {
            "hour": self.data_model.time.hour,
            "minute": self.data_model.time.minute,
            "second": self.data_model.time.second,
            "day_of_week": self.data_model.day,
            "even_week": self.data_model.week,
            "next_chn": self.data_model.nearest_chn,
            "next_time_hour": self.data_model.nearest_time.hour,
            "next_time_minute": self.data_model.nearest_time.minute,
            "temp1": self.data_model.t1,
            "temp2": self.data_model.t2,
            "temp_amount": self.data_model.t_amount,
            "rain": self.data_model.rain,
            "pause": self.data_model.pause,
            "version": self.data_model.version,
            "ip": self.data_model.ip,
            "esp_v": self.data_model.esp_v,
            "esp_connected": self.data_model.esp_connected,
            "esp_ap": self.data_model.esp_ap,
            "esp_net": self.data_model.esp_net,
            "esp_mqtt": self.data_model.esp_mqtt,
            "esp_errors": self.data_model.esp_errors,
            "pressure": self.data_model.pressure,
            "stream": self.data_model.stream,
            "num": self.data_model.num,
            "channels_state": channels_state
        }

        return properties

    def command_get_state(self) -> None:
        self.send_command("8.8.8.8.8.8.8.8")

    def command_set_time(self, year, month, day, hour, minute, second):

        data = '.'.join([str(i) for i in [minute, hour, second, day, month, year % 100]])
        self.send_command("0.0.1", data)

    def command_get_state_response(self, data, **kwargs) -> bool:
        try:
            data = kwargs["old_data"]
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

            db_chns = {i.number: i for i in Channel.objects.filter(controller=self.data_model)}
            chns = list(list(BitArray(uint=s[15], length=8)))[::-1] + list(BitArray(uint=s[16], length=8))[::-1] + list(
                BitArray(uint=s[17], length=8))[::-1] + list(BitArray(uint=s[18], length=8)[::-1])
            for c in db_chns.keys():
                if c < len(chns):
                    s = chns[db_chns[c].number-1]
                    if db_chns[c].state != s:
                        db_chns[c].state = s
                        db_chns[c].save()
            self.data_model.save()

            ControllerConsumer.send_properties(self.get_controller_properties())

            return False
        except:
            return True

    def on_connected(self, mqtt: MQTTManager):
        self.command_get_state()

    def get_check_sum(self, *data: str) -> (int, int):
        check_sum = 0
        for d in data:
            for i in d.split("."):
                if i.isdigit():
                    check_sum += int(i)
        check_sum_bytes = check_sum.to_bytes(2, "big")
        return check_sum_bytes[0], check_sum_bytes[1]

    def handle_message(self, mqtt: MQTTManager, controller_prefix: str, data: str) -> None:
        if self.last_command in self.command_response_handlers.keys():
            if self.command_response_handlers[self.last_command](data.replace(".1.2.3.4.3.2.1.", "").replace(".9.8.7.6.7.8.9..", ""), old_data=data):
                self.last_command = ""


#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.44.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.38.0.0.5.142.127.9.8.7.6.7.8.9..
#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.45.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.37.0.0.5.142.127.9.8.7.6.7.8.9..
#.1.2.3.4.3.2.1.0.2.6.5.35.60.0.0.5.5.1.1.100.0.0.0.1.1.0.0.0.0.0.121.3.9.2.20.30.127.3.1.12.25.35.2.98.9.8.7.6.7.8.9.9.
