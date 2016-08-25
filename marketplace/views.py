from django.shortcuts import render
from django.shortcuts import redirect
from django.http import Http404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import SasviewModel

def index(request):
    latest_models = SasviewModel.objects.order_by('-upload_date')[:5]
    context = { 'latest_models': latest_models }
    return render(request, 'marketplace/index.html', context)

# Model views

def detail(request, model_id):
    try:
        model = SasviewModel.objects.get(pk=model_id)
    except SasviewModel.DoesNotExist:
        raise Http404("Model does not exist.")
    return render(request, 'marketplace/detail.html', { 'model': model })

# User views

@login_required
def profile(request):
    return render(request, 'registration/profile.html')

@login_required
def password_change_done(request):
    messages.success(request, "Your password has been changed.")
    return redirect('profile')
