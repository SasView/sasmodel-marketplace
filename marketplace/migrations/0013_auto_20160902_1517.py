# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-09-02 15:17
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('marketplace', '0012_auto_20160902_1320'),
    ]

    operations = [
        migrations.AddField(
            model_name='sasviewmodel',
            name='verfied_date',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='sasviewmodel',
            name='verified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='sasviewmodel',
            name='verified_by',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='models_verified', to=settings.AUTH_USER_MODEL),
        ),
    ]
