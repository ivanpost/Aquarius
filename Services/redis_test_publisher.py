import redis

r = redis.StrictRedis("localhost", 55000, charset="utf-8", decode_responses=True, password="redispw")
pubsub = r.pubsub()
r.publish("chn-2", "Hello World!")
