# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-09 13:41
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0015_sasviewmodel_in_library'),
    ]

    operations = [
        migrations.AddField(
            model_name='sasviewmodel',
            name='score',
            field=models.IntegerField(default=0),
        ),
    ]
