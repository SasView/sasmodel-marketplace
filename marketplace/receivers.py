from django.contrib.auth.signals import user_logged_out
from django.dispatch import receiver
from django.contrib import messages


# Show a success flash when the user has been logged out
@receiver(user_logged_out)
def on_user_logged_out(sender, request, **kwargs):
    messages.success(request, 'You have been logged out.')
