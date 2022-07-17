from django.db import models
import datetime
from django.contrib.auth.models import User


class UserExtension(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    saved_controllers = models.CharField(max_length=100, default="[]")


class Controller(models.Model):
    prefix = models.CharField(max_length=30, default="")
    password = models.CharField(max_length=30, default="")
    time = models.TimeField(default=datetime.time(0, 0, 0), auto_now=False, auto_now_add=False)
    day = models.IntegerField(default=0)
    week = models.BooleanField(default=False)
    nearest_chn = models.IntegerField(default=1)
    nearest_time = models.TimeField(default=datetime.time(0, 0, 0), auto_now=False, auto_now_add=False)
    t1 = models.FloatField(default=0)
    t2 = models.FloatField(default=0)
    t_amount = models.IntegerField(default=1)
    rain = models.BooleanField(default=False)
    pause = models.BooleanField(default=False)
    version = models.IntegerField(default=0)
    ip = models.CharField(max_length=16, default="0.0.0.0")
    esp_v = models.CharField(max_length=12, default="0.0.0")
    esp_connected = models.BooleanField(default=False)
    esp_ap = models.BooleanField(default=False)
    esp_net = models.BooleanField(default=False)
    esp_mqtt = models.BooleanField(default=False)
    esp_errors = models.BooleanField(default=False)
    pressure = models.FloatField(default=0)
    stream = models.FloatField(default=0)
    num = models.CharField(max_length=12, default="0-0")


    def __str__(self):
        return self.prefix


class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    number = models.IntegerField(default=1)
    name = models.CharField(max_length=64, default="Канал")
    controller = models.ForeignKey('Controller', on_delete=models.CASCADE)
    state = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.controller.prefix} / {self.number}"


class Program(models.Model):
    id = models.AutoField(primary_key=True)
    channel = models.ForeignKey('Channel', on_delete=models.CASCADE)
    days = models.CharField(max_length=7, default='')
    hour = models.IntegerField(default=0)
    minute = models.IntegerField(default=0)
    t_min = models.IntegerField(default=0)
    t_max = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.channel.controller.prefix} / {self.channel.id} / ({self.days}|{self.hour}:{self.minute})"


