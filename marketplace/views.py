from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from attachments.models import Attachment
from .forms import SignupForm
from .forms import SasviewModelForm
from .models import SasviewModel
from .helpers import check_owned_by

def index(request):
    latest_models = SasviewModel.objects.order_by('-upload_date')[:5]
    context = { 'latest_models': latest_models }
    return render(request, 'marketplace/index.html', context)

# Model views

def detail(request, model_id):
    model = get_object_or_404(SasviewModel, pk=model_id)
    return render(request, 'marketplace/model_detail.html', { 'model': model })

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
            return redirect('edit_files', model_id=model.id)
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

@login_required
def edit_files(request, model_id):
    model = check_owned_by(request, model_id)
    if not isinstance(model, SasviewModel):
        return model
    return render(request, 'marketplace/model_files.html', { 'model': model })

@login_required
def delete_file(request, attachment_pk):
    g = get_object_or_404(Attachment, pk=attachment_pk)
    if (
        (request.user.has_perm('attachments.delete_attachment') and
        request.user == g.creator)
    or
        request.user.has_perm('attachments.delete_foreign_attachments')
    ):
        g.delete()
        messages.success(request, "Your attachment was deleted.")
    else:
        messages.error(request, "You don't have permission to delete this file.",
            extra_tags='danger')
    model = g.content_object
    return redirect('edit_files', model_id=model.id)

# User views

def sign_up(request):
    if request.user.is_authenticated:
        messages.info(request, 'You already have an account.')
        return redirect('profile')

    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            content_type = ContentType.objects.get_for_model(Attachment)
            user.user_permissions.add(Permission.objects.get(content_type=content_type,
                codename='add_attachment'))
            user.user_permissions.add(Permission.objects.get(content_type=content_type,
                codename='delete_attachment'))
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
    models = SasviewModel.objects.filter(owner__pk=request.user.id)
    return render(request, 'registration/profile.html', { 'models': models, 'user': user })

@login_required
def password_change_done(request):
    messages.success(request, "Your password has been changed.")
    return redirect('profile')
