from django.conf.urls import url, include

sport_urls = []

sport_registration_urls = [
    url(r'^(?P<pk>\d+)/players/', include('api.v1.players.urls', namespace='players')),
    url(r'^(?P<pk>\d+)/coaches/', include('api.v1.coaches.urls', namespace='coaches')),
    url(r'^(?P<pk>\d+)/referees/', include('api.v1.referees.urls', namespace='referees')),
    url(r'^(?P<pk>\d+)/managers/', include('api.v1.managers.urls', namespace='managers')),
    url(r'^(?P<pk>\d+)/scorekeepers/', include('api.v1.scorekeepers.urls', namespace='scorekeepers')),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
