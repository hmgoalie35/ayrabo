from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.CreateManagersView.as_view(), name='create'),
]
