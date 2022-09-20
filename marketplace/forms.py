import os
from django import forms
from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.template.defaultfilters import filesizeformat
from magic import Magic
from .models import SasviewModel
from .models import ModelFile
from .models import Comment
from .models import Category


class ModelFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        self.mimetypes = kwargs.pop('mimetypes')
        self.max_size = kwargs.pop('max_size')
        self.file_extensions = kwargs.pop('file_extensions') if 'file_extensions' in kwargs else None
        super(ModelFileField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(ModelFileField, self).clean(*args, **kwargs)
        if data is None:
            return data
        extension = os.path.splitext(data.name)[-1]
        try:
            f = Magic(mime=True)
            content_type = f.from_buffer(data.file.read())
        except Exception as e:
            content_type = data.content_type_extra
        data.seek(0)

        if self.mimetypes is not None and content_type not in self.mimetypes:
            raise ValidationError(
                f"Files of type {content_type} cannot be uploaded. Please select a file of type {self.mimetypes}.")
        if self.file_extensions is not None and extension not in self.file_extensions:
            raise ValidationError(
                f"Files of type {extension} cannot be uploaded. Please select a file of type {self.file_extensions}.")
        if self.max_size is not None and data.size > self.max_size:
            raise ValidationError(f"Files must be smaller than {filesizeformat(self.max_size)}.")
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
            if values[0] in ['<X>', b'<X>']:
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
    example_data = ExampleDataField(mimetypes=['text/plain'], max_size=15*2**10,
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
    model_file = ModelFileField(
        allow_empty_file=False,
        mimetypes=["text/x-c", "text/x-csrc",  # C++ files (.c)
                   "text/x-python", "text/x-python-script",  # Python files (.py)
                   "text/plain"],  # Plain text files (.txt)
        file_extensions=['.c', '.py'],
        max_size=50*2**10)
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
