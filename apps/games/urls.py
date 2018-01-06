from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.HockeyGameListView.as_view(), name='list'),
    url(r'^create/$', views.HockeyGameCreateView.as_view(), name='create'),
]
