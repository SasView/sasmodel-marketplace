import os
import re
import logging
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

# Points to a clone of the sasmodels repo
SASMODELS_DIR = os.environ.get("SASMODELS_DIR", "../sasmodels")
TAG_PATTERN = re.compile("(:[a-zA-Z]+:)") # Matches ':tag:'
REF_DEF_PATTERN = re.compile("(.. \[#[a-zA-Z]*\])") # Matches '.. [#RefTag]'
REF_PATTERN = re.compile("(\\\ \[#[a-zA-Z]*\]_)") # Matches '\ #[RefTag]_'
UNDERLINE_PATTERN = re.compile("(-{3,})") # Matches 3 or more consecutive '-'s

def _remove_all(pattern, string):
    # (SRE_Pattern, str) -> (str)
    # Remove all text that matches a compiled regex (from re.compile) from string
    res = pattern.search(string)
    while res is not None:
        string = string.replace(res.group(0), "")
        res = pattern.search(string)
    return string

def parse_all_models():
    models_dir = os.path.join(SASMODELS_DIR, "sasmodels", "models")
    if not os.path.isdir(models_dir):
        logging.error("Models directory not found at: {}".format(models_dir))
        return
    
    logging.info("Uploading sasmodels from {}".format(SASMODELS_DIR))
    # TODO: Better glob so __init__ does't need to be manually skipped
    for file_path in glob(os.path.join(models_dir, "*.py")):
        file_name = os.path.split(file_path)[-1]
        if file_name[0] == '_':
            # Skip __init__.py and _spherepy.py
            continue
        file_name = os.path.splitext(file_name)[0]
        model_name = file_name.replace('_', ' ').title()

        file_contents = ''
        with open(file_path, 'r') as f:
            file_contents = f.read() 

        # BUG: This assumes model names never change, so if the name of a python
        # model file is changed, a new model will be created in the marketplace
        # instead of renaming the existing one
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
            upload_model_files(updated_model, file_path)
        else:
            # Check if model needs updating
            # BUG: If only the c file is changed, but not the python file,
            # the updated c file won't be uploaded. Editing the python file
            # triggers the upload of both the c & the python files.
            if not model.description == updated_model.description or \
                not model.category == updated_model.category:
                model.description = updated_model.description
                model.category = updated_model.category
                model.save()
                logging.info("Updated {}".format(model_name))
                for model_file in ModelFile.objects.filter(model__pk=model.id):
                    model_file.delete()
                upload_model_files(model, file_path)
    logging.info("Upload complete")

def upload_file(model, file_path):
    # (SasviewModel, str) -> ()
    # Upload the file at file_path to the model
    file_name = os.path.split(file_path)[-1]

    file_obj = None
    with open(file_path, 'rb') as file_handle:
        file_obj = SimpleUploadedFile(file_name, file_handle.read())

    if file_obj is None:
        raise Exception("Unable to upload file: {}".format(file_path))
    
    model_file = ModelFile(name=file_name, model=model, model_file=file_obj)
    model_file.save()

def upload_model_files(model, file_path):
    # (SasviewModel, str) -> ()
    # Upload file_path.py and file_path.c to model if they exist
    extensions = [".py", ".c"]
    file_path = os.path.splitext(file_path)[0]
    for ext in extensions:
        if os.path.isfile(file_path + ext):
            try:
                upload_file(model, file_path + ext)
            except Exception as e:
               print(e)

def parse_description(file_contents):
    # (str) -> (str)
    # Extract the model description from the file's docstring, and format it
    # into something the marketplace can make sense of
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
            # skip_line = (line.strip() == "$$")
        elif is_math and line == "" and paragraph.strip() != "$$":
            # if skip_line: # Skip the first blank line after '.. math::'
                # skip_line = False
                # continue
            # else: # End of '.. math::' section
            is_math = False
            paragraph += "\n$$"
            description += paragraph + "\n"
            paragraph = ""
            continue
        elif is_math:
            # MathJax doesn't handle ampersands very well
            line = line.replace("&=", "=")
            line = line.replace("=&\\", "=")
            line = line.replace("&\\", "")
            line = line.strip()
        else:
            # Not math
            line = line.replace("\\ ", "")
        
        # End of a paragraph
        if line == "" and not is_math:
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
    # (str) -> (Category or None)
    # Get the model's category from the contents of its python file
    category_name = ""
    category_regex= "category[\s]?=[\s]?[\"']([a-zA-Z\s:_-]*)[\"']"
    category_result = None
    category_result = re.search(category_regex, file_contents)

    if category_result is not None:
        category_name = category_result.group(1)
        category_name = category_name.split(":")[-1]
    
    category = None
    if category_name != "":
        try:
            category = Category.objects.get(slug=category_name)
        except Exception:
            category = None
    return category

def parse_model(model_name, file_contents):
    # (str) -> (SasviewModel)
    # Return a SasviewModel object given the contents of a model file
    description = parse_description(file_contents)
    category = parse_category(file_contents)
    owner = User.objects.get(username='sasview')

    model = SasviewModel(name=model_name, description=description,
        category=category, in_library=True, owner=owner)
    return model

if __name__ == '__main__':
    logging.basicConfig(filename="upload.log", level=logging.INFO, 
        format="%(asctime)s - %(message)s", datefmt="%m/%d/%y %H:%M:%S")
    logging.info('-' * 30) # Separate log entries
    parse_all_models()
