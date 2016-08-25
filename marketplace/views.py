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

def detail(request, model_id):
    try:
        model = SasviewModel.objects.get(pk=model_id)
    except SasviewModel.DoesNotExist:
        raise Http404("Model does not exist.")
    return render(request, 'marketplace/detail.html', { 'model': model })

@login_required
def profile(request):
    return render(request, 'registration/profile.html')
