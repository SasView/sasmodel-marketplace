from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from django.http import HttpResponseServerError
from django.http import Http404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .forms import SignupForm
from .forms import SasviewModelForm
from .forms import ModelFileForm
from .forms import CommentForm
from .models import SasviewModel
from .models import ModelFile
from .models import Comment
from .models import Category
from .models import Vote
from .helpers import check_owned_by_or_admin
from .backends.database import DatabaseStorage

def index(request):
    all_categories = Category.objects.all().order_by('name')

    paginator = Paginator(all_categories, 15)
    page = request.GET.get('page')
    try:
        categories = paginator.page(page)
    except PageNotAnInteger:
        categories = paginator.page(1)
    except EmptyPage:
        # Page is out of range
        categories = paginator.page(paginator.num_pages)

    return render(request, 'marketplace/index.html', { 'categories': categories })

def search(request):
    query = None
    if request.method == 'GET' and ('query' in request.GET):
        query = request.GET['query']
        result_list = SasviewModel.objects.filter(Q(name__icontains=query) | Q(description__icontains=query) | Q(category__name__icontains=query))
        verified_str = ""
        if 'verified' in request.GET:
            try:
                verified_str = request.GET['verified']
                verified = bool(int(verified_str))
                result_list = result_list.filter(verified=verified)
            except:
                pass
    else:
        result_list = SasviewModel.objects.none()

    paginator = Paginator(result_list.order_by('name'), 15)
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        results = paginator.page(1)
    except EmptyPage:
        # Page is out of range
        results = paginator.page(paginator.num_pages)

    return render(request, 'marketplace/search.html',
        { 'results': results, 'query': query, 'verified': verified_str })

# Model views

def detail(request, model_id):
    model = get_object_or_404(SasviewModel, pk=model_id)
    files = ModelFile.objects.filter(model__pk=model.id)
    comments = Comment.objects.filter(model__pk=model.id)
    form = CommentForm(request.POST or None)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "You must log in to post a comment.",
                extra_tags="danger")
            form = CommentForm()
        elif form.is_valid():
            comment = form.save(commit=False)
            comment.model = model
            comment.user = request.user
            comment.save()
            form = CommentForm()
    return render(request, 'marketplace/model_detail.html',
        { 'model': model, 'files': files, 'comments': comments, 'form': form })

def view_category(request, slug=None):
    if slug is None:
        models = SasviewModel.objects.all().order_by("-upload_date")
        category = None
    else:
        category = get_object_or_404(Category, pk=slug)
        models = SasviewModel.objects.filter(category__slug=category.slug).order_by("-score")

    paginator = Paginator(models, 20)
    page = request.GET.get('page')
    try:
        models = paginator.page(page)
    except PageNotAnInteger:
        models = paginator.page(1)
    except EmptyPage:
        # Page is out of range
        models = paginator.page(paginator.num_pages)

    return render(request, 'marketplace/category_view.html',
        { 'models': models, 'category': category, 
            'categories': Category.objects.all().order_by('name') })

@login_required
def create(request):
    if request.method == 'POST':
        form = SasviewModelForm(request.POST, request.FILES)
        if form.is_valid():
            model = form.save(commit=False)
            model.owner = request.user
            if form.cleaned_data['example_data']:
                model.example_data_x = form.cleaned_data['example_data'][0]
                model.example_data_y = form.cleaned_data['example_data'][1]
            model.save()
            messages.success(request, "Model successfully created.")
            return redirect('edit_files', model_id=model.id)

    else:
        form = SasviewModelForm()
    return render(request, 'marketplace/model_create.html', { 'form': form })

@login_required
def edit(request, model_id):
    model = check_owned_by_or_admin(request, model_id)
    if not isinstance(model, SasviewModel):
        return model

    form = SasviewModelForm(request.POST or None, request.FILES or None,
        instance=model)
    if request.method == 'POST':

        if form.is_valid():
            model = form.save(commit=False)
            if form.cleaned_data['example_data']:
                model.example_data_x = form.cleaned_data['example_data'][0]
                model.example_data_y = form.cleaned_data['example_data'][1]
            model.save()
            messages.success(request, "Model successfully updated.")
            return redirect(model)

    return render(request, 'marketplace/model_edit.html', { 'form': form })

@login_required
def vote(request, model_id):
    model = get_object_or_404(SasviewModel, pk=model_id)

    if model.owner == request.user:
        messages.error(request, "You cannot vote on your own model.",
            extra_tags="danger")
        return redirect('detail', model_id)

    vote = Vote.objects.filter(model__id=model_id, user__id=request.user.id).first()
    if vote is None:
        vote = Vote(user=request.user, model=model, value=0)
    else:
        # User has already voted, undo their last vote
        vote.value = -vote.value
        vote.save()

    if request.GET['vote'] == 'up':
        vote.value = 1
    elif request.GET['vote'] == 'down':
        vote.value = -1
    else:
        return HttpResponseServerError("Invalid request. 'vote' must be 'up' or 'down'")

    vote.save()
    messages.success(request, "Vote successful.")
    return redirect('detail', model_id=model_id)


@login_required
def delete(request, model_id):
    model = check_owned_by_or_admin(request, model_id)
    if not isinstance(model, SasviewModel):
        return model
    model.delete()
    messages.success(request, "Model deleted")
    return redirect('profile')

@login_required
def verify(request, model_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to verify this model",
            extra_tags="danger")
        return redirect('detail', model_id=model_id)
    model = get_object_or_404(SasviewModel, pk=model_id)
    model.verify(request.user)
    action = "unverified"
    if model.verified: action = "verified"
    messages.success(request, "Model has been {}".format(action))
    return redirect('detail', model_id=model.id)

@login_required
def toggle_in_library(request, model_id):
    if not request.user.is_staff:
        messages.error(request, "You do not have permission to edit library status",
            extra_tags="danger")
        return redirect('detail', model_id=model_id)
    model = get_object_or_404(SasviewModel, pk=model_id)
    model.in_library = not model.in_library
    model.save()
    messages.success(request, "Library status changed successfully")
    return redirect('detail', model_id=model_id)


# Model file views

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
    except Exception as e:
        return HttpResponseServerError(str(e))
    if model_file is None:
        raise Http404("File not found.")
    file_content = model_file.read()
    res = HttpResponse(file_content, content_type="application/force_download")
    return res

@login_required
def delete_file(request, file_id):
    model_file = ModelFile.objects.filter(pk=file_id).first()
    model = check_owned_by_or_admin(request, model_file.model.id)
    if model != model_file.model:
        messages.error(request, "You are not authorised to delete this file.",
            extra_tags="danger")
        return redirect('detail', model_id=model_file.model.id)
    model_file.delete()
    messages.success(request, "File successfully deleted.")
    return redirect('edit_files', model_id=model_file.model.id)

@login_required
def edit_files(request, model_id):
    model = check_owned_by_or_admin(request, model_id)
    if not isinstance(model, SasviewModel):
        return model
    files = ModelFile.objects.filter(model__id=model.id)
    form = ModelFileForm()

    if request.method == 'POST':
        form = ModelFileForm(request.POST, request.FILES)
        if form.is_valid():
            model_file = form.save(commit=False)
            model_file.name = request.FILES['model_file'].name
            model_file.model = model
            model_file.save()
            messages.success(request, 'Model file successfully added.')
            return redirect('edit_files', model_id=model_id)
    return render(request, 'marketplace/model_file_edit.html',
        { 'model': model, 'files': files, 'form': form })

# Comment views

@login_required
def delete_comment(request, comment_id):
    comment = Comment.objects.filter(pk=comment_id).first()
    if comment.user != request.user:
        messages.error(request, "You are not authorised to delete this comment",
            extra_tags="danger")
    else:
        comment.delete()
        messages.success(request, "Comment successfully deleted.")
    return redirect('detail', model_id=comment.model.id)

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
    all_models = SasviewModel.objects.filter(owner__pk=user.id).order_by('-upload_date')

    paginator = Paginator(all_models, 15)

    page = request.GET.get('page')
    try:
        models = paginator.page(page)
    except PageNotAnInteger:
        models = paginator.page(1)
    except EmptyPage:
        # Page is out of range
        models = paginator.page(paginator.num_pages)

    return render(request, 'registration/profile.html', { 'models': models, 'user': user })

@login_required
def password_change_done(request):
    messages.success(request, "Your password has been changed.")
    return redirect('profile')
