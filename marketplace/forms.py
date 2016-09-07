from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import filesizeformat
from .models import SasviewModel
from .models import ModelFile
from .models import Comment
from .models import Category
import magic

class ModelFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.mimetypes = kwargs.pop('mimetypes')
        self.max_size = kwargs.pop('max_size')
        super(ModelFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ModelFileField, self).clean(*args, **kwargs)
        if data is None:
            return data
        content_type = magic.from_buffer(data.read(), mime=True)
        data.seek(0)
        if self.mimetypes is not None and content_type not in self.mimetypes:
            raise ValidationError(
                ("Files of type %(content_type)s cannot be uploaded. Please select a file of type %(accepted_types)s."),
                params={ 'content_type': content_type, 'accepted_types': self.mimetypes }
            )
        if self.max_size is not None and data.size > self.max_size:
            raise ValidationError(
                ("Files must be smaller than %(file_size)s."),
                params={ 'file_size': filesizeformat(self.max_size) }
            )
        return data

class ExampleDataField(ModelFileField):
    def clean(self, *args, **kwargs):
        data = super(ExampleDataField, self).clean(*args, **kwargs)
        if data is None:
            return data
        x = []
        y = []
        error = None
        for line in data:
            values = line.split()
            if values[0] == '<X>':
                continue # Header row
            if len(values) < 2 and len(values) != 0:
                try:
                    float(values[0])
                except:
                    raise ValidationError(
                        ("Error parsing float %(error_val)s"),
                        params = { 'error_val': values[0] }
                    )
                raise ValidationError(("x and y columns must be the same length"))
            try:
                x.append(float(values[0]))
            except:
                error = values[0]
                break
            try:
                y.append(float(values[1]))
            except:
                error = values[0]
                break
        if error is not None:
            raise ValidationError(
                ("Error parsing float %(error_val)s"),
                params = { 'error_val': error }
            )
        x = ",".join([str(x_i) for x_i in x])
        y = ",".join([str(y_i) for y_i in y])

        return (x, y)

class SasviewModelForm(ModelForm):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False)
    example_data = ExampleDataField(mimetypes=['text/plain'], max_size=5*2**10,
        required=False, help_text=("(Optional) Run your model in SasView, right click on the "
        "theory curve and select \"Save As\". Save the data as a "
        ".txt file and upload it here. The data will display as a graph on"
        " the model's page."))
    class Meta:
        model = SasviewModel
        fields = ("name", "category", "description", "example_data")
        help_texts = {
            'description': ("LaTeX formatting is supported. Use $...$ to"
                " denote inline maths, and $$...$$ or \\[...\\] to denote"
                " displayed maths.")
        }

class ModelFileForm(ModelForm):
    model_file = ModelFileField(allow_empty_file=False,
        mimetypes=["text/x-c", "text/x-python"], max_size=20*2**10)
    class Meta:
        model = ModelFile
        fields = ("model_file",)
        labels = { "model_file": "Upload a model file:" }

class CommentForm(ModelForm):
    model = forms.ModelChoiceField(queryset=SasviewModel.objects.all(), required=False)
    class Meta:
        model = Comment
        fields = ("content", "model")
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
