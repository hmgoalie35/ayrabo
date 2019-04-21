from django.conf.urls import url

from . import views


app_name = 'players'
urlpatterns = [
    url(r'^(?P<player_pk>\d+)/update/$', views.PlayerUpdateView.as_view(), name='update'),
]
