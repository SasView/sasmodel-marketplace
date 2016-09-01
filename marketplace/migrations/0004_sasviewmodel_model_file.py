# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-01 08:23
from __future__ import unicode_literals

from django.db import migrations, models
import marketplace.backends.database


class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0003_auto_20160826_1029'),
    ]

    operations = [
        migrations.AddField(
            model_name='sasviewmodel',
            name='model_file',
            field=models.FileField(default='', storage=marketplace.backends.database.DatabaseStorage(), upload_to=b'uploaded_models'),
            preserve_default=False,
        ),
    ]