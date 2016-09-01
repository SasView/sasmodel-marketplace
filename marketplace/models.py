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

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'model_id': self.id})

@python_2_unicode_compatible
class ModelFile(models.Model):
    name = models.CharField(max_length=100)
    model_file = models.FileField(upload_to='uploaded_models',
        storage=DatabaseStorage())
    model = models.ForeignKey(SasviewModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

@receiver(pre_delete)
def delete_file(sender, instance, **kwargs):
    if sender == SasviewModel:
        files = ModelFile.objects.filter(model__pk=instance.id)
        for f in files:
            f.delete()
    elif sender == ModelFile:
        instance.model_file.delete()
