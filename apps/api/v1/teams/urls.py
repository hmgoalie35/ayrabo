from django.conf.urls import url, include

urlpatterns = [
    url(r'^(?P<pk>\d+)/players/', include('api.v1.players.urls', namespace='players')),
    url(r'^(?P<pk>\d+)/season-rosters/', include('api.v1.seasons.roster_urls', namespace='season_rosters')),
]
