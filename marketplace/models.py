from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from .backends.database import DatabaseStorage
from .validators import validate_comma_separated_float_list
from django.dispatch import receiver
from django.db.models.signals import pre_delete, post_save

def truncate(string, length):
    if len(string) > length:
        string = string[:length-3] + "..."
    return string

@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, primary_key=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

@python_2_unicode_compatible
class SasviewModel(models.Model):
    name = models.CharField(max_length=150)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    upload_date = models.DateTimeField(verbose_name='Date Published',
        auto_now_add=True)
    example_data_x = models.CharField(validators=[validate_comma_separated_float_list],
        max_length=5000, null=True,blank=True)
    example_data_y = models.CharField(validators=[validate_comma_separated_float_list],
        max_length=5000, null=True,blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    verified = models.BooleanField(default=False,blank=True)
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
        related_name='models_verified',blank=True)
    verfied_date = models.DateTimeField(null=True,blank=True)

    in_library = models.BooleanField(default=False)

    def verify(self, user):
        if not user.is_staff:
            raise PermissionDenied("Only staff have permission to verify models")
        if not self.verified:
            self.verified = True
            self.verified_by = user
            self.verfied_date = timezone.now()
        else:
            self.verified = False
            self.verified_by = None
            self.verfied_date = None
        self.save()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('detail', kwargs={'model_id': self.id})

    def description_truncated(self):
        return truncate(self.description, 200)

    def example_data_json(self):
        if self.example_data_x is None or self.example_data_y is None:
            return "[]"
        json = "["
        x_data = self.example_data_x.split(",")
        y_data = self.example_data_y.split(",")
        for point in zip(x_data, y_data):
            json += "{" + "x: " + point[0] + ", y: " + point[1] + "},"
        json += "]"
        return json

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.IntegerField()
    model = models.ForeignKey(SasviewModel, on_delete=models.CASCADE)

@python_2_unicode_compatible
class ModelFile(models.Model):
    name = models.CharField(max_length=100)
    model_file = models.FileField(upload_to='uploaded_models',
        storage=DatabaseStorage())
    model = models.ForeignKey(SasviewModel, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Comment(models.Model):
    content = models.TextField(max_length=500)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    model = models.ForeignKey(SasviewModel, on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)

    def content_truncated(self):
        return truncate(self.content, 150)

    def __str__(self):
        content_str = self.content_truncated()
        return "{}: {}".format(self.user.username, content_str)

@receiver(pre_delete)
def pre_Delete_handler(sender, instance, **kwargs):
    if sender == SasviewModel:
        # Delete all files when a model is deleted
        files = ModelFile.objects.filter(model__pk=instance.id)
        for f in files:
            f.delete()
    elif sender == ModelFile:
        # Delete file data when a ModelFile instance is deleted
        instance.model_file.delete()
    elif sender == Vote:
        # Undo the vote when it's deleted
        instance.model.score -= instance.value
        instance.model.save()

@receiver(post_save)
def post_save_handler(sender, instance, **kwargs):
    if sender == Vote:
        # Update the model's score when a vote is made
        instance.model.score += instance.value
        instance.model.save()
