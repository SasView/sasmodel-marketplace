# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-08-25 10:42
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SasviewModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=150)),
                ('description', models.CharField(max_length=500)),
                ('upload_date', models.DateTimeField(verbose_name='date published')),
            ],
        ),
    ]
