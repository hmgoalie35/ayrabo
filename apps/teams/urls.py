from django.conf.urls import include, url

from seasons.urls import season_roster_urls
from . import views


season_urls = [
    url(r'^$', views.TeamDetailScheduleView.as_view(), name='schedule'),
    url(r'^season-rosters/$', views.TeamDetailSeasonRostersView.as_view(), name='season_rosters-list'),
]

urlpatterns = [
    url(r'^(?P<team_pk>\d+)/seasons/(?P<season_pk>\d+)/', include(season_urls, namespace='seasons')),
    url(r'^(?P<team_pk>\d+)/season-rosters/', include(season_roster_urls, namespace='season_rosters')),
    url(r'^(?P<team_pk>\d+)/games/', include('games.urls', namespace='games')),
    url(r'^(?P<team_pk>\d+)/$', views.TeamDetailScheduleView.as_view(), name='schedule'),
    url(r'^(?P<team_pk>\d+)/players/$', views.TeamDetailPlayersView.as_view(), name='players'),
]
