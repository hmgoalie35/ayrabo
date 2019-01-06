from django.conf.urls import include, url

from api.v1.seasons.urls import season_roster_urls


urlpatterns = [
    url(r'^(?P<pk>\d+)/players/', include('api.v1.players.urls', namespace='players')),
    url(r'^(?P<pk>\d+)/season-rosters/', include(season_roster_urls, namespace='season_rosters')),
]
