from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^create/$', views.CreateUserProfileView.as_view(), name='create'),
]
