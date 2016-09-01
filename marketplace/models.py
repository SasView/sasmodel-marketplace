from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from .backends.database import DatabaseStorage
from django.dispatch import receiver
from django.db.models.signals import pre_delete

@python_2_unicode_compatible
class SasviewModel(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    upload_date = models.DateTimeField('date published')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    model_file = models.FileField(upload_to='uploaded_models',
        storage=DatabaseStorage())

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'model_id': self.id})

@receiver(pre_delete)
def delete_file(sender, instance, **kwargs):
    if sender == SasviewModel:
        instance.model_file.delete()
