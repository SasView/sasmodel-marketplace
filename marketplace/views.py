from django.shortcuts import render
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignupForm
from .forms import SasviewModelForm
from .models import SasviewModel

def index(request):
    latest_models = SasviewModel.objects.order_by('-upload_date')[:5]
    context = { 'latest_models': latest_models }
    return render(request, 'marketplace/index.html', context)

# Model views

def detail(request, model_id):
    model = get_object_or_404(SasviewModel, pk=model_id)
    return render(request, 'marketplace/detail.html', { 'model': model })

@login_required
def create(request):
    if request.method == 'POST':
        form = SasviewModelForm(request.POST)
        if form.is_valid():
            model = form.save(commit=False)
            model.owner = request.user
            model.upload_date = timezone.now()
            model.save()
            messages.success(request, "Model successfully uploaded.")
            return redirect(model)
    else:
        form = SasviewModelForm()
    return render(request, 'marketplace/create_model.html', { 'form': form })


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


@login_required
def profile(request):
    models = SasviewModel.objects.filter(owner__pk=request.user.id)
    return render(request, 'registration/profile.html', { 'models': models })

@login_required
def password_change_done(request):
    messages.success(request, "Your password has been changed.")
    return redirect('profile')
