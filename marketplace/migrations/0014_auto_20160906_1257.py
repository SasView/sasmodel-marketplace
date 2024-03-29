# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-06 12:57
import django.core.validators
from django.db import migrations, models
import re


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0013_auto_20160902_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='sasviewmodel',
            name='example_data_x',
            field=models.CharField(max_length=500, null=True, validators=[django.core.validators.RegexValidator(re.compile(b'^([-+]?\\d*\\.?\\d+[,\\s]*)+$'), 'Must be a list of comma separated float values', b'invalid')]),
        ),
        migrations.AddField(
            model_name='sasviewmodel',
            name='example_data_y',
            field=models.CharField(max_length=500, null=True, validators=[django.core.validators.RegexValidator(re.compile(b'^([-+]?\\d*\\.?\\d+[,\\s]*)+$'), 'Must be a list of comma separated float values', b'invalid')]),
        ),
    ]
