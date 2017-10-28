from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.RefereesCreateView.as_view(), name='create'),
]
