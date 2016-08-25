from __future__ import unicode_literals

from django.db import models

class SasviewModel(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    upload_date = models.DateTimeField('date published')
