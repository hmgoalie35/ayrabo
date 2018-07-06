from django.conf.urls import include, url

from . import views

sport_urls = [
    url(r'^register/$', views.SportRegistrationCreateView.as_view(), name='register'),
    url(r'^(?P<slug>[-\w]+)/games/', include('games.roster_urls', namespace='games')),
    url(r'^(?P<slug>[-\w]+)/players/', include('players.urls', namespace='players')),
    url(r'^(?P<slug>[-\w]+)/coaches/', include('coaches.urls', namespace='coaches')),
]

urlpatterns = [
    url(r'^sports/', include(sport_urls, namespace='sports')),
]
