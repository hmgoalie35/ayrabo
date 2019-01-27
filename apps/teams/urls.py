from django.conf.urls import include, url

from seasons.urls import season_roster_urls
from . import views


season_urls = [
    url(r'^(?P<season_pk>\d+)/$', views.TeamDetailScheduleView.as_view(), name='schedule'),
]

urlpatterns = [
    url(r'^(?P<team_pk>\d+)/seasons/', include(season_urls, namespace='seasons')),
    url(r'^(?P<team_pk>\d+)/season-rosters/', include(season_roster_urls, namespace='season_rosters')),
    url(r'^(?P<team_pk>\d+)/games/', include('games.urls', namespace='games')),
    url(r'^(?P<team_pk>\d+)/$', views.TeamDetailScheduleView.as_view(), name='schedule'),
]
