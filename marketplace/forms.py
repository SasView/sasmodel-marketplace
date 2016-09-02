from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import filesizeformat
from .models import SasviewModel
from .models import ModelFile
from .models import Comment
import magic

class SasviewModelForm(ModelForm):
    class Meta:
        model = SasviewModel
        fields = ("name", "description")
        help_texts = {
            'description': ("LaTeX formatting is supported. Use $...$ to"
                " denote inline maths, and $$...$$ or \\[...\\] to denote"
                " displayed maths.")
        }

class ModelFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.mimetypes = kwargs.pop('mimetypes')
        self.max_size = kwargs.pop('max_size')
        super(ModelFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ModelFileField, self).clean(*args, **kwargs)
        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)
        if self.mimetypes is not None and content_type not in self.mimetypes:
            raise ValidationError(
                ("Files of type %(content_type)s cannot be uploaded. Please select a C file or Python script."),
                params={ 'content_type': content_type }
            )
        if self.max_size is not None and data.size > self.max_size:
            raise ValidationError(
                ("Files must be smaller than %(file_size)s."),
                params={ 'file_size': filesizeformat(self.max_size) }
            )
        return data

class ModelFileForm(ModelForm):
    model_file = ModelFileField(allow_empty_file=False,
        mimetypes=["text/x-c", "text/x-python"], max_size=20*2**10)
    class Meta:
        model = ModelFile
        fields = ("model_file",)
        labels = { "model_file": "Upload a model file:" }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ("content",)
        labels = { "content": "Add a comment:" }

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    email.help_text = "Required."
    first_name = forms.CharField()
    last_name = forms.CharField()

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(SignupForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user
