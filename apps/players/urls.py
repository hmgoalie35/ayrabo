from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.CreatePlayersView.as_view(), name='create'),
    url(r'^(?P<player_pk>\d+)/update/$', views.UpdatePlayerView.as_view(), name='update'),
]
