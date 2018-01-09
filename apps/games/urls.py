from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.GameListView.as_view(), name='list'),
    url(r'^create/$', views.GameCreateView.as_view(), name='create'),
]
