from django.db import models

class Controller(models.Model):
    prefix = models.CharField(max_length=30)

    def __str__(self):
        return self.prefix

class Channel(models.Model):
    id = models.AutoField(primary_key=True)
    controller = models.ForeignKey('Controller', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.controller.prefix} / {self.id}"


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


