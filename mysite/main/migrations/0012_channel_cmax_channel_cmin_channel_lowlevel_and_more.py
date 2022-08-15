# Generated by Django 4.0.5 on 2022-07-27 13:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_remove_program_cmax_remove_program_cmin_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='channel',
            name='cmax',
            field=models.IntegerField(default=30),
        ),
        migrations.AddField(
            model_name='channel',
            name='cmin',
            field=models.IntegerField(default=10),
        ),
        migrations.AddField(
            model_name='channel',
            name='lowlevel',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='channel',
            name='meandr_on',
            field=models.IntegerField(default=60),
        ),
        migrations.AddField(
            model_name='channel',
            name='meaoff_cmax',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channel',
            name='meaoff_cmin',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='channel',
            name='press_off',
            field=models.FloatField(default=3.8),
        ),
        migrations.AddField(
            model_name='channel',
            name='press_on',
            field=models.FloatField(default=2.1),
        ),
        migrations.AddField(
            model_name='channel',
            name='rainsens',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='channel',
            name='season',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='channel',
            name='tempsens',
            field=models.IntegerField(default=1),
        ),
    ]