from django.conf.urls import url
from django.urls import include

from api.v1.seasons.urls import season_roster_urls


app_name = 'teams'
urlpatterns = [
    url(r'^(?P<pk>\d+)/players/', include('api.v1.players.urls')),
    url(r'^(?P<pk>\d+)/season-rosters/', include((season_roster_urls, 'season_rosters'))),
]
