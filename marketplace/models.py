from django.db import models
from django.utils.encoding import python_2_unicode_compatible

@python_2_unicode_compatible
class SasviewModel(models.Model):
    name = models.CharField(max_length=150)
    description = models.CharField(max_length=500)
    upload_date = models.DateTimeField('date published')

    def __str__(self):
        return self.name
