from django.shortcuts import get_object_or_404
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import SasviewModel

def check_owned_by(request, model_id, user=None):
    if user is None:
        user = request.user
    model = get_object_or_404(SasviewModel, pk=model_id)
    if model.owner != user:
        messages.error(request, "You are not authorised to edit this model.",
            extra_tags='danger')
        return redirect(model)
    return model
