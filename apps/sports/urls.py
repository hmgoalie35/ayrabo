from django.conf.urls import include, url

from . import views

urlpatterns = [
    url(r'^register/$', views.SportRegistrationCreateView.as_view(), name='register'),
    url(r'^dashboard/$', views.SportDashboardView.as_view(), name='dashboard'),
    url(r'^(?P<slug>[-\w]+)/games/', include('games.roster_urls', namespace='games')),
    url(r'^(?P<slug>[-\w]+)/players/', include('players.urls', namespace='players')),
    url(r'^(?P<slug>[-\w]+)/coaches/', include('coaches.urls', namespace='coaches')),
]
