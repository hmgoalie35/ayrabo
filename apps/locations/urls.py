from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/', views.LocationDetailView.as_view(), name='detail'),
]
