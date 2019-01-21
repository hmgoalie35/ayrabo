from django.conf.urls import url

from . import views


season_urls = [
    url(r'^(?P<season_pk>\d+)/$', views.SeasonDetailScheduleView.as_view(), name='schedule'),
    url(r'^(?P<season_pk>\d+)/divisions/$', views.SeasonDetailDivisionsView.as_view(), name='divisions'),
]

season_roster_urls = [
    url(r'^$', views.SeasonRosterListView.as_view(), name='list'),
    url(r'^create/$', views.SeasonRosterCreateView.as_view(), name='create'),
    url(r'^(?P<pk>\d+)/update/$', views.SeasonRosterUpdateView.as_view(), name='update'),
]

urlpatterns = []
