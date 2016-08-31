# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import marketplace.backends.database

class Migration(migrations.Migration):

    dependencies = [
        ('marketplace', '0006_sasviewmodel_model_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='uploaded_files',
            fields=[
                ('file_name', models.FilePathField(primary_key=True)),
                ('blob', models.BinaryField()),
                ('size', models.BigIntegerField()),
            ],
        ),
    ]
