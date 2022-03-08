# Generated by Django 4.0.3 on 2022-03-08 10:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='program',
            name='days',
            field=models.CharField(default='', max_length=7),
        ),
        migrations.AddField(
            model_name='program',
            name='hour',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='minute',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='t_max',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='program',
            name='t_min',
            field=models.IntegerField(default=0),
        ),
    ]
