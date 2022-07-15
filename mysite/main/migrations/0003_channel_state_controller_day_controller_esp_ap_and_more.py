# Generated by Django 4.0.3 on 2022-04-29 18:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_program_days_program_hour_program_minute_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='state',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='day',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_ap',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_connected',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_errors',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_mqtt',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_net',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='esp_v',
            field=models.CharField(default='0.0.0', max_length=12),
        ),
        migrations.AddField(
            model_name='controller',
            name='ip',
            field=models.CharField(default='0.0.0.0', max_length=16),
        ),
        migrations.AddField(
            model_name='controller',
            name='nearest_chn',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='controller',
            name='nearest_time',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AddField(
            model_name='controller',
            name='num',
            field=models.CharField(default='0-0', max_length=12),
        ),
        migrations.AddField(
            model_name='controller',
            name='pause',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='pressure',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='rain',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='controller',
            name='stream',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='t1',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='t2',
            field=models.FloatField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='t_amount',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='controller',
            name='time',
            field=models.TimeField(default=datetime.time(0, 0)),
        ),
        migrations.AddField(
            model_name='controller',
            name='version',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='controller',
            name='week',
            field=models.BooleanField(default=False),
        ),
    ]
