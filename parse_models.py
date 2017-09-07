import os
import re
from glob import glob
import django

# Initialise the Django environment. This must be done before importing anything
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sasmarket.settings")
django.setup()

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from marketplace.models import SasviewModel
from marketplace.models import Category
from marketplace.models import ModelFile

SASMODELS_DIR = os.environ.get("SASMODELS_DIR", "../sasmodels")
TAG_PATTERN = re.compile("(:[a-zA-Z]+:)") # Matches ':tag:'
REF_DEF_PATTERN = re.compile("(.. \[#[a-zA-Z]*\])") # Matches '.. [#RefTag]'
REF_PATTERN = re.compile("(\\\ \[#[a-zA-Z]*\]_)") # Matches '\ #[RefTag]_'
UNDERLINE_PATTERN = re.compile("(-{3,})") # Matches 3 or more consecutive '-'s

file_path = os.path.join(SASMODELS_DIR, "sasmodels", "models", "star_polymer.py")


def _remove_all(pattern, string):
    res = pattern.search(string)
    while res is not None:
        string = string.replace(res.group(0), "")
        res = pattern.search(string)
    return string

def parse_all_models():
    # TODO: Better glob so __init__ does't need to be manually skipped
    for file_path in glob(os.path.join(SASMODELS_DIR, "sasmodels", "models", "*.py")):
        file_name = os.path.split(file_path)[-1]
        if file_name[0] == '_':
            # Skip __init__.py and _spherepy.py
            continue
        file_name = os.path.splitext(file_name)[0]
        model_name = file_name.replace('_', ' ').title()

        file_contents = ''
        with open(file_path, 'r') as f:
            file_contents = f.read() 

        # TODO: This assumes model names never change
        model = None
        try:
            model = SasviewModel.objects.get(name=model_name, in_library=True)
        except Exception:
            model = None

        updated_model = parse_model(model_name, file_contents)
        if model is None:
            # Create new model (verify method saves model)
            updated_model.verify(updated_model.owner)
            print("Created {}".format(model_name))
        else:
            # Check if model needs updating. Explicit check done to avoid
            # calling save on every model - saves time
            if not model.description == updated_model.description or \
                not model.category == updated_model.category:
                model.description = updated_model.description
                model.category = updated_model.category
                model.save()
                print("Updated {}".format(model_name))

def upload_file(model, file_path):
    file_name = os.path.split(file_path)[-1]
    file_name = os.path.splitext(file_name)[0]

    file_obj = None
    with open(file_path, 'rb') as file_handle:
        file_obj = SimpleUploadedFile(file_name, file_handle.read())

    if file_obj is None:
        raise Exception("Unable to open file: {}".format(file_path))
    
    model_file = ModelFile(name=file_name, model=model, model_file=file_obj)
    model_file.save()

def upload_model_files(model, file_path):
    return

def parse_description(file_contents):
    # str -> str
    description = ""
    paragraph = ""
    is_math = False
    skip_line = False
    
    for line in file_contents.split("\n"):
        if line == 'r"""': # First line of desc
            continue
        if '"""' in line: # last line of desc
            description += paragraph
            break
        
        # Remove RST :tags:
        res = TAG_PATTERN.search(line)
        if res is not None:
            tag = res.group(1)
            if tag == ":nowrap:" or tag == ":figure:":
                continue
            line = line.replace(tag, "")

        # Remove links to references
        line = _remove_all(REF_PATTERN, line)

        # Remove underlines
        line = _remove_all(UNDERLINE_PATTERN, line)

        # Can't display images on sasmodels marketplace
        if ".. figure::" in line:
            continue

        # Surround '.. math::' sections with $$...$$
        if ".. math::" in line and not is_math:
            is_math = True
            line = line.replace(".. math::", "$$")
            skip_line = (line.strip() == "$$")
        elif is_math and line == "":
            if skip_line: # Skip the first blank line after '.. math::'
                skip_line = False
                continue
            else: # End of '.. math::' section
                is_math = False
                paragraph += "\n$$"
                description += paragraph + "\n"
                paragraph = ""
                continue
        elif is_math:
            # MathJax doesn't handle ampersands very well
            line = line.replace("&", "")
        
        # End of a paragraph
        if line == "":
            description += paragraph + "\n\n"
            paragraph = ""

        # Reference definition line. Each reference is on a separate line.
        res = REF_DEF_PATTERN.search(line)
        if res is not None:
            line = _remove_all(REF_DEF_PATTERN, line)
            description += line + "\n"
            continue

        # Authorship and Verification line
        if line[:4] == "* **":
            line = line[2:] # Strip '* '
            description += line + "\n"
            continue

        paragraph += line + " "

    return description

def parse_category(file_contents):
    # str -> Category or None
    category_name = ""
    category_regex= "category[\s]?=[\s]?[\"']([a-zA-Z\s:_-]*)[\"']"
    category_result = None
    category_result = re.search(category_regex, file_contents)

    if category_result is not None:
        category_name = category_result.group(1)
        category_name = category_name.split(":")[-1].title()
    
    category = None
    if category_name != "":
        try:
            category = Category.objects.get(name=category_name)
        except Exception:
            category = None
    return category

def parse_model(model_name, file_contents):
    # str -> SasviewModel
    description = parse_description(file_contents)
    category = parse_category(file_contents)
    owner = User.objects.get(username='sasview')

    model = SasviewModel(name=model_name, description=description,
        category=category, in_library=True, owner=owner)
    return model

# if __name__ == '__main__':
#     parse_all_models()
