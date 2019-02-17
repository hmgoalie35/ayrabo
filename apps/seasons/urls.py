from django.conf.urls import url

from teams.views import TeamDetailSeasonRostersView
from . import views


season_roster_urls = [
    url(r'^$', TeamDetailSeasonRostersView.as_view(), name='list'),
    url(r'^create/$', views.SeasonRosterCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update/$', views.SeasonRosterUpdateView.as_view(), name='update'),
]

urlpatterns = []
