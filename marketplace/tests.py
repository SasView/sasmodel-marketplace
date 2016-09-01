from django.test import TestCase, RequestFactory
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from marketplace.models import SasviewModel
from marketplace.views import edit, delete

def create_user(username=None, email=None, password="testpassword",
    commit=True, sign_in=False, client=None):
    if username is None:
        username = "testuser{}".format(create_user.id)
        create_user.id += 1
    if email is None:
        email = username + "@test.com"
    user = User(username=username, email=email)
    user.set_password(password)
    if commit:
        user.save()
    if sign_in:
        if client is None:
            raise ValueError("client cannot be None is sign_in is True")
        client.force_login(user)
    return user
create_user.id = 0

def create_model(user=None, name="Model", desc="Description", commit=True):
    if user is None:
        user = create_user()
    model = SasviewModel(name=name, description=desc,
        upload_date=timezone.now(), owner=user)
    if commit:
        model.save()
    return model


class SasviewModelTests(TestCase):

    def test_ownership(self):
        owner = create_user()
        model = create_model(user=owner)

        found_model = SasviewModel.objects.filter(owner__pk=owner.id).first()
        self.assertEqual(model, found_model)

    def test_search(self):
        model = create_model(name="Adsorbed Layer")
        response = self.client.post(reverse('search'), { 'query': 'layer' })
        self.assertContains(response, "Adsorbed Layer")

    def test_cascade_deletion(self):
        user = create_user()
        create_model(user=user)
        create_model(user=user)

        all_models = SasviewModel.objects.all()
        self.assertEqual(len(all_models), 2)

        user.delete()
        all_models = SasviewModel.objects.all()
        self.assertEqual(len(all_models), 0)


class UserTests(TestCase):

    def test_sign_in(self):
        user = create_user()
        self.client.post(reverse('login'),
            { 'username': user.username, 'password': 'testpassword' })

        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)

    def test_sign_out(self):
        user = create_user(sign_in=True, client=self.client)
        response = self.client.get(reverse('logout'), follow=True)
        self.assertContains(response, "Log In")

    def test_profile_permissions(self):
        other_user = create_user()
        current_user = create_user(sign_in=True, client=self.client)

        their_model = create_model(other_user, name="Their Model")
        my_model = create_model(current_user, name="My Model")

        response1 = self.client.get(reverse('profile', kwargs={ 'user_id': current_user.id }))
        response2 = self.client.get(reverse('profile'))

        self.assertContains(response1, current_user.email)
        self.assertContains(response2, current_user.email)
        self.assertContains(response1, "Change Password")
        self.assertContains(response2, "Change Password")
        self.assertContains(response1, "My Model")
        self.assertContains(response2, "My Model")
        self.assertNotContains(response1, "Their Model")
        self.assertNotContains(response2, "Their Model")

        response = self.client.get(reverse('profile',
            kwargs={ 'user_id': other_user.id }))
        self.assertContains(response, other_user.username)
        self.assertNotContains(response, "Change Password")
        self.assertContains(response, "Their Model")
        self.assertNotContains(response, "My Model")

    def test_model_detail_permissions(self):
        user = create_user()
        model = create_model(user=user, name="My Model")

        response = self.client.get(reverse('detail',
            kwargs={ 'model_id': model.id }))
        self.assertContains(response, "My Model")
        self.assertNotContains(response, "Edit Details")
        self.assertNotContains(response, "Delete")

        self.client.force_login(user)

        response = self.client.get(reverse('detail',
            kwargs={ 'model_id': model.id }))
        self.assertContains(response, "My Model")
        self.assertContains(response, "Edit Details")
        self.assertContains(response, "Delete")

    def test_edit_permissions(self):
        factory = RequestFactory()
        owner = create_user()
        current = create_user(sign_in=True, client=self.client)
        model = create_model(user=owner)

        request = factory.get('/models/{}/edit/'.format(model.id))
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = current
        response = edit(request, model_id=model.id)
        self.assertRedirects(response, reverse('detail',
            kwargs={ 'model_id': model.id }), fetch_redirect_response=False)

        self.client.force_login(owner)

        response = self.client.get(reverse('edit',
            kwargs={ 'model_id': model.id }), follow=True)
        self.assertContains(response, "Edit")

    def test_delete_permissions(self):
        factory = RequestFactory()
        owner = create_user()
        current = create_user(sign_in=True, client=self.client)
        model = create_model(user=owner)

        request = factory.get('/models/{}/delete/'.format(model.id))
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = current
        response = edit(request, model_id=model.id)
        self.assertRedirects(response, reverse('detail',
            kwargs={ 'model_id': model.id }), fetch_redirect_response=False)

        self.client.force_login(owner)

        request = factory.get('/models/{}/delete/'.format(model.id))
        setattr(request, 'session', 'session')
        messages = FallbackStorage(request)
        setattr(request, '_messages', messages)
        request.user = owner
        response = delete(request, model.id)
        self.assertRedirects(response, reverse('profile'),
            fetch_redirect_response=False)
