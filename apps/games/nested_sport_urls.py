from django.conf.urls import url
from django.urls import include

from . import views


"""
This module represents urls that solely need to be nested under a sport. The current games.urls are nested under team.
"""

roster_urls = [
    url(r'^rosters/update/$', views.GameRostersUpdateView.as_view(), name='update'),
]

app_name = 'games'
urlpatterns = [
    url(r'^(?P<game_pk>\d+)/', include((roster_urls, 'rosters'))),
    url(r'^(?P<game_pk>\d+)/$', views.GameScoresheetView.as_view(), name='scoresheet'),
]
