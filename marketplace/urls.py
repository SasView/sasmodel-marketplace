from django.urls import re_path as url
from django.contrib.auth import views as auth_views
from . import views
from . import receivers

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^models/(?P<model_id>[0-9]+)/$', views.detail, name='detail'),
    url(r'^models/(?P<model_id>[0-9]+)/edit/$', views.edit, name='edit'),
    url(r'^models/(?P<model_id>[0-9]+)/delete/$', views.delete, name='delete'),
    url(r'^models/(?P<model_id>[0-9]+)/files/$', views.edit_files, name='edit_files'),
    url(r'^models/(?P<model_id>[0-9]+)/vote/$', views.vote, name='vote'),
    url(r'^models/(?P<model_id>[0-9]+)/verify/$', views.verify, name='verify'),
    url(r'^models/(?P<model_id>[0-9]+)/library/$', views.toggle_in_library, name='toggle_in_library'),
    url(r'^models/create/$', views.create, name='create'),
    url(r'^models/(?P<slug>[-\w]+)/$', views.view_category, name='view_category'),
    url(r'^models/$', views.view_category, name='view_category'),
    url(r'^search/$', views.search, name='search'),
    url(r'^uploads/(?P<file_id>[0-9]+)/delete/$', views.delete_file, name='delete_file'),
    url(r'^uploads/(?P<file_id>[0-9]+)$', views.show_file, name='show_file'),
    url(r'^uploads/(?P<filename>.*)$', views.download_file, name='download_file'),
    url(r'^comments/(?P<comment_id>[0-9]+)/delete/$', views.delete_comment, name='delete_comment'),
    url(r'^accounts/signup/$', views.sign_up, name='signup'),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(), name='login'),
    url(r'^accounts/logout/$', auth_views.LogoutView.as_view(), { 'next_page': views.index }, name='logout'),
    url(r'^accounts/profile/$', views.profile, name='profile'),
    url(r'^accounts/user/(?P<user_id>[0-9]+)/$', views.profile, name='profile'),
    url(r'^accounts/password_change/done', views.password_change_done, name="password_change_done"),
    url(r'^accounts/password_change', auth_views.PasswordChangeView.as_view(), name="password_change"),
]
