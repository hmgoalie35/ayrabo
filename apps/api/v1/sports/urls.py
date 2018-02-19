from django.conf.urls import url, include

sport_urls = [
    url(r'^(?P<pk>\d+)/games/', include('api.v1.games.roster_urls', namespace='games')),
]

sport_registration_urls = [
    url(r'^(?P<pk>\d+)/players/', include('api.v1.players.deactivation_urls', namespace='players')),
    url(r'^(?P<pk>\d+)/coaches/', include('api.v1.coaches.deactivation_urls', namespace='coaches')),
    url(r'^(?P<pk>\d+)/referees/', include('api.v1.referees.deactivation_urls', namespace='referees')),
    url(r'^(?P<pk>\d+)/managers/', include('api.v1.managers.deactivation_urls', namespace='managers')),
    url(r'^(?P<pk>\d+)/scorekeepers/', include('api.v1.scorekeepers.deactivation_urls', namespace='scorekeepers')),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
