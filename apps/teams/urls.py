from django.conf.urls import url

from seasons.views import CreateSeasonRosterView

urlpatterns = [
    url(r'^(?P<team_pk>\d+)/season-roster/create/$', CreateSeasonRosterView.as_view(), name='create_season_roster'),
]
