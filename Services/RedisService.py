import redis
import threading


class RedisService:

    HOST = "localhost"
    PORT = 55000
    PASSWORD = "redispw"

    r = redis.StrictRedis(HOST, PORT, charset="utf-8", decode_responses=True,
                              password=PASSWORD)
    pubsub = r.pubsub()
    registry = {}

    @staticmethod
    def event_handler(event_name):
        def event_decorator(handler):
            RedisService.pubsub.psubscribe(event_name)
            RedisService.registry.setdefault(event_name, []).append(handler)
            return handler

        return event_decorator

    @staticmethod
    def invoke(event_name, data, pattern=None):
        if pattern is None: pattern = event_name
        for func in RedisService.registry.get(pattern, ()):
            func(event_name, data)

    @staticmethod
    def publish(event_name, data=""):
        RedisService.r.publish(event_name, data)


    @staticmethod
    def check_messages():
        while True:
            for message in RedisService.pubsub.listen():
                if message["type"] == "message":
                    RedisService.invoke(message["channel"], message["data"])
                if message["type"] == "pmessage":
                    RedisService.invoke(message["channel"], message["data"], message["pattern"])


thread = threading.Thread(target=RedisService.check_messages)
thread.start()






