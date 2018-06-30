from django.conf.urls import url, include

from . import views

sport_urls = [
    url(r'^(?P<slug>[-\w]+)/games/', include('games.roster_urls', namespace='games')),
    url(r'^(?P<slug>[-\w]+)/players/', include('players.urls', namespace='players')),
    url(r'^(?P<slug>[-\w]+)/coaches/', include('coaches.urls', namespace='coaches')),
]

sport_registration_urls = [
    url(r'^create/$', views.SportRegistrationCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/$', views.SportRegistrationDetailView.as_view(), name='detail'),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
    url(r'^sport-registrations/', include(sport_registration_urls, namespace='sportregistrations')),
]
