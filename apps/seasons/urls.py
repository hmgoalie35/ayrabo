from django.conf.urls import url, include

from . import views

season_urls = []

season_roster_urls = [
    url(r'^$', views.ListSeasonRosterView.as_view(), name='list'),
    url(r'^create/$', views.CreateSeasonRosterView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update/$', views.UpdateSeasonRosterView.as_view(), name='update'),
]

urlpatterns = [
    url(r'^seasons/', include(season_urls, namespace='seasons')),
    url(r'^season-rosters/', include(season_roster_urls, namespace='season_rosters')),
]
