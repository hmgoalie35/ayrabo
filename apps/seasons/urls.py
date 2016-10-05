from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^-roster/create/$', views.CreateSeasonRosterView.as_view(), name='create_season_roster'),
    url(r'^-roster/(?P<team_pk>\d+)/create/$', views.CreateSeasonRosterView.as_view(),
        name='create_season_roster_team_param'),
]
