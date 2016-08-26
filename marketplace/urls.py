from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from . import receivers

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^models/(?P<model_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^models/(?P<model_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^models/(?P<model_id>[0-9]+)/delete/$', views.delete, name='delete'),
    url(r'^models/(?P<model_id>[0-9]+)/files/$', views.edit_files, name='edit_files'),
    url(r'^models/files/(?P<attachment_pk>[0-9]+)/delete/$', views.delete_file, name='delete_file'),
    url(r'^models/create/$', views.create, name='create'),
    url(r'^accounts/signup/$', views.sign_up, name='signup'),
    url(r'^accounts/login/$', auth_views.login, name='login'),
    url(r'^accounts/logout/$', auth_views.logout, { 'next_page': views.index }, name='logout'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^accounts/user/(?P<user_id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^accounts/password_change/done', views.password_change_done, name="password_change_done"),
    url(r'^accounts/password_change', auth_views.password_change, name="password_change"),
]
