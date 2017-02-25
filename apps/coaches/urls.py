from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.CreateCoachesView.as_view(), name='create'),
]
