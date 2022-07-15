from RedisService import RedisService

Instance = None

def try_int(i):
    try:
        return int(i)
    except:
        return 0


class ControllerV2Manager:

    def __init__(self, controller_prefix: str):
        self.cmd_pattern = "1.2.3.4.3.2.1.{request_code}.{payload}.{check_sum[0]}.{check_sum[1]}.9.8.7.6.7.8.9"
        self.topic_send = "aqua_smart"
        self.topic_receive = "aqua_kontr"

        self.last_command = ""

        self.commands = {
            "8.8.8.8.8.8.8.8": (self.command_get_state, self.command_get_state_response)
        }

        self.on_connected()

    def subscribe(self) -> None:
        RedisService.publish("mqtt:subscribe", self.topic_receive)

    def send_command(self, request_code: str, payload: str = ""):
        msg = self.wrap_command(request_code, payload)
        self.last_command = request_code
        RedisService.publish(f"mqtt:send:{self.topic_send}", msg)

    def wrap_command(self, request_code: str, payload: str) -> str:
        return self.cmd_pattern.format(request_code=request_code, payload=payload, check_sum=self.get_check_sum(payload))

    def command_get_state(self) -> None:
        self.send_command("8.8.8.8.8.8.8.8")

    def on_connected(self) -> None:
        self.subscribe()
        self.command_get_state()

    def command_get_state_response(self, message: str) -> bool:
        print(message)
        data = list(map(try_int, message.split(".")))[8:-9]
        print("Data:")
        [print(f'{num}: {i}') for num, i in enumerate(data)]

        return True

    def on_message(self, topic: str, data: str) -> None:
        if self.last_command in self.commands.keys() and topic == self.topic_receive:
            if self.commands[self.last_command][1](data):
                self.last_command = ""

    @staticmethod
    @RedisService.event_handler("mqtt:connected")
    def on_connected_handler(channel: str, data: str) -> None:
        Instance.on_connected()

    @staticmethod
    @RedisService.event_handler("mqtt:message:*")
    def on_message_handler(channel: str, data: str) -> None:
        topic = channel.replace("mqtt:message:", "")
        Instance.on_message(topic, data)

    @staticmethod
    def get_check_sum(data: str) -> (int, int):
        bytes = sum(list(data.encode("ascii"))).to_bytes(2, "little")
        return bytes[0], bytes[1]


if __name__ == "__main__":
    Instance = ControllerV2Manager("")

#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.44.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.38.0.0.5.142.127.9.8.7.6.7.8.9..
#MQTT - [aqua_kontr] - .1.2.3.4.3.2.1.18.45.29.3.23.0.0.0.0.0.0.1.0.0.0.0.25.61.0.159.192.168.31.160.1.9.3.13.37.0.0.5.142.127.9.8.7.6.7.8.9..

