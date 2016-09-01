from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.postgres.search import SearchVector
from .forms import SignupForm
from .forms import SasviewModelForm
from .models import SasviewModel
from .models import ModelFile
from .helpers import check_owned_by
from .backends.database import DatabaseStorage

def index(request):
    latest_models = SasviewModel.objects.order_by('-upload_date')[:5]
    context = { 'latest_models': latest_models }
    return render(request, 'marketplace/index.html', context)

def search(request):
    if request.method == 'POST' and ('query' in request.POST):
        query = request.POST['query']
        results = SasviewModel.objects.annotate(
            search=SearchVector('name', 'description')).filter(search=query)
    else:
        results = []
    return render(request, 'marketplace/search.html',
        { 'results': results, 'query': query })

def show_file(request, file_id):
    model_file = get_object_or_404(ModelFile, pk=file_id)
    file_content = model_file.model_file.read()

    try:
        res = render(request, 'marketplace/show_code.html',
            { 'file_object': model_file, 'file_content': file_content })
    except:
        res = render(request, 'marketplace/show_code.html',
            { 'file_object': model_file })

    return res

def download_file(request, filename):
    storage = DatabaseStorage()
    try:
        model_file = storage.open(filename, 'rb')
        file_content = model_file.read()
    except Exception as e:
        file_content = str(e)
    res = HttpResponse(file_content, content_type="application/force_download")
    return res

# Model views

def detail(request, model_id):
    model = get_object_or_404(SasviewModel, pk=model_id)
    files = ModelFile.objects.filter(model__pk=model.id)
    return render(request, 'marketplace/model_detail.html',
        { 'model': model, 'files': files })

@login_required
def create(request):
    if request.method == 'POST':
        form = SasviewModelForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.owner = request.user
            model.upload_date = timezone.now()
            model.save()
            messages.success(request, "Model successfully created.")
            return redirect('detail', model_id=model.id)
    else:
        form = SasviewModelForm()
    return render(request, 'marketplace/model_create.html', { 'form': form })

@login_required
def edit(request, model_id):
    model = check_owned_by(request, model_id)
    if not isinstance(model, SasviewModel):
        return model

    form = SasviewModelForm(request.POST or None, instance=model)
    if request.method == 'POST':

        if form.is_valid():
            model = form.save()
            messages.success(request, "Model successfully updated.")
            return redirect(model)

    return render(request, 'marketplace/model_edit.html', { 'form': form })

@login_required
def delete(request, model_id):
    model = check_owned_by(request, model_id)
    if not isinstance(model, SasviewModel):
        return model
    model.delete()
    messages.success(request, "Model deleted")
    return redirect('profile')

# User views

def sign_up(request):
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('profile')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.info(request, 'Account created successfully.')
            return redirect('profile')
    else:
        form = SignupForm()
    return render(request, 'registration/signup.html', { 'form': form })


def profile(request, user_id=None):
    if user_id is None:
        user_id = request.user.id
    user = get_object_or_404(User, pk=user_id)
    models = SasviewModel.objects.filter(owner__pk=user.id)
    return render(request, 'registration/profile.html', { 'models': models, 'user': user })

@login_required
def password_change_done(request):
    messages.success(request, "Your password has been changed.")
    return redirect('profile')
