from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<slug>[-\w]+)/$', views.LeagueScheduleView.as_view(), name='schedule'),
    url(r'^(?P<slug>[-\w]+)/seasons/(?P<season_pk>\d+)/$', views.LeagueScheduleView.as_view(), name='seasons'),
    url(r'^(?P<slug>[-\w]+)/divisions/$', views.LeagueDivisionsView.as_view(), name='divisions'),
]
