from django.conf.urls import url, include

from . import views

sport_urls = [
    url('^(?P<slug>[-\w]+)/games/', include('games.roster_urls', namespace='games')),
    url(r'^(?P<slug>[-\w]+)/players/', include('players.urls', namespace='players')),
]

sport_registration_urls = [
    url(r'^create/$', views.SportRegistrationCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', views.SportRegistrationDetailView.as_view(), name='detail'),
    url(r'^(?P<pk>\d+)/coaches/', include('coaches.urls', namespace='coaches')),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
