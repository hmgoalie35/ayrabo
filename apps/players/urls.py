from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^create/$', views.PlayersCreateView.as_view(), name='create'),
    url(r'^(?P<player_pk>\d+)/update/$', views.PlayerUpdateView.as_view(), name='update'),
]
